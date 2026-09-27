import io
import json
from pathlib import Path
import random
import tempfile
import unittest
from unittest.mock import patch

from chunking import PROFILES, chunk_documents, split_text, validate_token_lengths
from ingest import clean_text, extract, extract_html, extract_reddit, make_document, read_sources, run


def source(kind="html", profile="formal", **extra):
    return dict(id="example", source="Example", url="https://example.org/research", kind=kind, profile=profile, **extra)


def pdf_fixture(text):
    """Build a tiny real PDF without adding a PDF-authoring test dependency."""
    stream = f"BT /F1 12 Tf 72 720 Td ({text}) Tj ET".encode()
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream",
    ]
    result = b"%PDF-1.4\n"
    offsets = [0]
    for number, obj in enumerate(objects, 1):
        offsets.append(len(result))
        result += f"{number} 0 obj\n".encode() + obj + b"\nendobj\n"
    xref = len(result)
    result += b"xref\n0 6\n0000000000 65535 f \n"
    result += b"".join(f"{offset:010d} 00000 n \n".encode() for offset in offsets[1:])
    result += f"trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF".encode()
    return result


class ChunkTests(unittest.TestCase):
    def test_profiles_preserve_every_character_and_exact_overlap(self):
        rng = random.Random(42)
        texts = ["x" * 2401, "word " * 401, "Short paragraph.\n\n" * 90]
        texts += ["".join(rng.choice("abc .!?\n") for _ in range(n)) for n in (1, 499, 500, 501, 799, 800, 801, 8000)]
        for profile in PROFILES.values():
            for text in texts:
                spans = split_text(text, profile.size, profile.overlap)
                self.assertEqual(spans[0][0], 0)
                self.assertEqual(spans[-1][1], len(text))
                rebuilt = text[slice(*spans[0])]
                for i, (start, end) in enumerate(spans):
                    self.assertLessEqual(end - start, profile.size)
                    if i:
                        self.assertEqual(spans[i-1][1] - start, profile.overlap)
                        self.assertGreater(end, spans[i-1][1])
                        rebuilt += text[start + profile.overlap:end]
                self.assertEqual(rebuilt, text)

    def test_boundaries_and_invalid_configuration(self):
        text = "a" * 280 + "\n\n" + "b" * 280
        self.assertEqual(split_text(text, 500, 100)[0][1], 282)
        self.assertEqual(split_text(" \n", 500, 100), [])
        for size, overlap in ((0, 0), (100, 100), (100, -1)):
            with self.assertRaises(ValueError):
                split_text("abc", size, overlap)

    def test_stable_ids_metadata_and_token_failure(self):
        doc = make_document(source(), "body", "Research " * 130)
        chunks = chunk_documents([doc])
        self.assertEqual(chunks, chunk_documents([doc]))
        self.assertEqual(chunks[0]["metadata"]["url"], source()["url"])
        class Tokenizer:
            def encode(self, text, **kwargs):
                return [0] * 257
        with self.assertRaisesRegex(ValueError, "257 tokens"):
            validate_token_lengths(chunks, Tokenizer())


class ExtractionTests(unittest.TestCase):
    def test_html_keeps_inline_context_and_removes_boilerplate(self):
        html = b"""<html><head><title>Research</title></head><body>
        <header>Site header</header><nav>Menu</nav><main><h1>Requirements</h1>
        <p>Need a <strong>3.5 GPA</strong> and junior standing.</p>
        <p>Contact a <a href='/faculty'>faculty sponsor</a>.</p>
        <footer>Copyright</footer><script>tracking()</script></main></body></html>"""
        text, title = extract_html(html)
        self.assertEqual(title, "Research")
        self.assertIn("Need a 3.5 GPA and junior standing.", text)
        self.assertIn("Contact a faculty sponsor.", text)
        for unwanted in ("Site header", "Menu", "Copyright", "tracking"):
            self.assertNotIn(unwanted, text)
        self.assertIn("\n\n", text)
        with self.assertRaisesRegex(ValueError, "selector"):
            extract_html(html, ".missing")

    def test_normalization_and_challenge_rejection(self):
        self.assertEqual(clean_text(" A\u00a0 B \r\n\r\n\r\n C\u200b "), "A B\n\nC")
        with self.assertRaisesRegex(ValueError, "challenge"):
            extract_html(b"<html><title>Access denied</title><body>Forbidden</body></html>")

    def test_source_specific_selectors_remove_related_stories_and_sidebar(self):
        html = b"""<html><title>Research profile</title><body><main>
        <div id="story"><p>Student joined a faculty lab.</p>
        <div class="contact-box">Unrelated quotation</div></div>
        <div class="article-footer">Keep Reading: Campus Store</div>
        </main></body></html>"""
        docs, _ = extract(html, source(selector="#story", exclude_selector=".contact-box"))
        self.assertEqual(docs[0]["text"], "Student joined a faculty lab.")
        self.assertEqual(docs[0]["metadata"]["title"], "Research profile")

    def test_real_pdf_extraction_and_page_metadata(self):
        docs, warnings = extract(pdf_fixture("Junior or senior standing and 3.5 GPA required."), source("pdf"))
        self.assertFalse(warnings)
        self.assertIn("3.5 GPA", docs[0]["text"])
        self.assertEqual(docs[0]["metadata"]["page"], 1)
        with self.assertRaisesRegex(ValueError, "Expected a PDF"):
            extract(b"<html>Blocked</html>", source("pdf"))

    def test_reddit_comments_are_isolated_and_incompleteness_reported(self):
        reply = {"kind": "t1", "data": {"name": "t1_b", "body": "Bob's view", "author": "bob"}}
        comment = {"kind": "t1", "data": {"name": "t1_a", "body": "Alice's view " * 70, "author": "alice",
                   "permalink": "/r/example/comments/post/a/", "replies": {"data": {"children": [reply]}}}}
        payload = [{"data": {"children": [{"data": {"name": "t3_post", "title": "R1 discussion"}}]}},
                   {"data": {"children": [comment, {"kind": "more", "data": {}}]}}]
        docs, warnings = extract_reddit(json.dumps(payload).encode(), source("reddit", "commentary"))
        self.assertEqual(len(docs), 3)
        self.assertTrue(warnings)
        for chunk in chunk_documents(docs):
            self.assertFalse("Alice" in chunk["text"] and "Bob" in chunk["text"])
            self.assertLessEqual(len(chunk["text"]), 500)
        self.assertTrue(docs[1]["metadata"]["url"].endswith("/a/"))

    def test_offline_pipeline_partial_failure_and_reproducible_outputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "source.txt").write_text("Contact a faculty mentor. " * 100)
            manifest = root / "sources.json"
            manifest.write_text(json.dumps([
                source("text", local_path="source.txt"),
                {**source("text", local_path="absent.txt"), "id": "missing"},
            ]))
            with patch("requests.Session.get", side_effect=AssertionError("Offline run fetched a URL")), patch("sys.stdout", new_callable=io.StringIO):
                report = run(manifest, root / "out", offline=True)
                first = [json.loads(line)["id"] for line in (root / "out/chunks.jsonl").read_text().splitlines()]
                run(manifest, root / "out", offline=True)
                second = [json.loads(line)["id"] for line in (root / "out/chunks.jsonl").read_text().splitlines()]
            self.assertEqual(first, second)
            self.assertEqual(report["successful_sources"], 1)
            self.assertEqual(report["sources"][1]["status"], "error")
            self.assertTrue(first)

    def test_manifest_matches_plan(self):
        root = Path(__file__).resolve().parents[1]
        sources = read_sources(root / "sources.json")
        self.assertEqual(len(sources), 10)
        self.assertEqual(sum(s["profile"] == "commentary" for s in sources), 2)
        self.assertEqual(len({s["url"] for s in sources}), 10)
        self.assertTrue(all(s["kind"] == "html" for s in sources))
        self.assertIn("dig-goldwater", {s["id"] for s in sources})
        self.assertIn("afro-independent-study", {s["id"] for s in sources})
        self.assertFalse({"reddit-r1", "pols-independent-study"} & {s["id"] for s in sources})
        for item in sources:
            self.assertIn(item["url"], (root / "planning.md").read_text())


if __name__ == "__main__":
    unittest.main()

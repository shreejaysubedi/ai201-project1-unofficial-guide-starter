"""Load Howard research sources, clean them, and write citation-ready chunks.

Run `python ingest.py --help` for online and local-file usage.
"""

import argparse
from datetime import datetime, timezone
import io
import json
from pathlib import Path
import re
import unicodedata

from bs4 import BeautifulSoup
import pdfplumber
from pdfminer.pdftypes import PDFException
from pdfminer.psparser import PSException
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from chunking import PROFILES, chunk_documents, validate_token_lengths

ROOT = Path(__file__).resolve().parent


def clean_text(text: str) -> str:
    text = unicodedata.normalize("NFKC", text).replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[\u200b\ufeff\x00]", "", text)
    text = re.sub(r"[^\S\n]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def extract_html(
    content: bytes, selector: str | None = None, exclude_selector: str | None = None,
) -> tuple[str, str]:
    soup = BeautifulSoup(content, "html.parser")
    title = soup.title.get_text(" ", strip=True) if soup.title else ""
    for tag in soup.select(
        "script, style, noscript, nav, footer, aside, form, svg, iframe, "
        "[role='navigation'], [role='contentinfo'], [hidden], "
        ".breadcrumb, .breadcrumbs, .menu, #menu, #footer, .footer, "
        "#countdownClock, .cookie-banner, .social-share"
    ):
        tag.decompose()
    # Remove only site headers, retaining article titles and bylines.
    for header in soup.select("body > header, [role='banner']"):
        header.decompose()
    if exclude_selector:
        for tag in soup.select(exclude_selector):
            tag.decompose()
    selectors = [selector] if selector else [".entry-content", "article", "main", "[role='main']"]
    root = next((node for choice in selectors if (node := soup.select_one(choice)) is not None), None)
    if selector and root is None:
        raise ValueError(f"Content selector not found: {selector}")
    root = root if root is not None else soup.body
    if root is None:
        raise ValueError("No HTML body found")
    # Inline emphasis/links stay in their sentences; block boundaries survive.
    for br in root.find_all("br"):
        br.replace_with("\n")
    for block in root.find_all(["p", "div", "section", "h1", "h2", "h3", "h4", "li", "tr", "blockquote"]):
        block.insert_before("\n\n")
        block.insert_after("\n\n")
    for cell in root.find_all(["td", "th"]):
        cell.insert_after(" | ")
    text = clean_text(root.get_text())
    if re.search(r"just a moment|access denied|verify you are human|blocked by network security", title, re.I):
        raise ValueError(f"Received an access/challenge page: {title}")
    return text, clean_text(title)


def make_document(source: dict, suffix: str, text: str, **metadata) -> dict:
    return {
        "id": f"{source['id']}:{suffix}",
        "text": clean_text(text),
        "metadata": {
            "source_id": source["id"], "source": source["source"],
            "url": source["url"], "profile": source["profile"],
            "kind": source["kind"], **metadata,
        },
    }


def extract_reddit(content: bytes, source: dict) -> tuple[list[dict], list[str]]:
    payload = json.loads(content)
    if not isinstance(payload, list) or len(payload) < 2:
        raise ValueError("Expected Reddit thread JSON with post and comment listings")
    documents, warnings = [], []
    post = payload[0]["data"]["children"][0]["data"]
    documents.append(make_document(
        source, post["name"], post["title"] + "\n\n" + post.get("selftext", ""),
        author=post.get("author", "[deleted]"), title=post["title"],
    ))

    def visit(children):
        for child in children:
            data = child["data"]
            if child["kind"] == "more":
                warnings.append("Reddit has unexpanded comments; this snapshot is incomplete.")
                continue
            if child["kind"] != "t1":
                continue
            body = data.get("body", "")
            if body.strip() and body.strip() not in ("[deleted]", "[removed]"):
                permalink = data.get("permalink", "")
                documents.append(make_document(
                    source, data["name"], body,
                    author=data.get("author", "[deleted]"),
                    comment_id=data["name"], parent_id=data.get("parent_id", ""),
                    url="https://www.reddit.com" + permalink if permalink.startswith("/") else source["url"],
                    title=post["title"],
                ))
            replies = data.get("replies")
            if isinstance(replies, dict):
                visit(replies["data"]["children"])

    visit(payload[1]["data"]["children"])
    return documents, list(dict.fromkeys(warnings))


def extract(content: bytes, source: dict) -> tuple[list[dict], list[str]]:
    kind = source["kind"]
    if kind == "reddit":
        return extract_reddit(content, source)
    if kind == "pdf":
        if not content.lstrip().startswith(b"%PDF-"):
            raise ValueError("Expected a PDF, but received another format")
        documents, warnings = [], []
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            for number, page in enumerate(pdf.pages, 1):
                text = clean_text(page.extract_text() or "")
                if text:
                    documents.append(make_document(source, f"page-{number}", text, page=number))
                else:
                    warnings.append(f"PDF page {number} has no extractable text; OCR/manual review required.")
        return documents, warnings
    if kind == "html":
        text, title = extract_html(content, source.get("selector"), source.get("exclude_selector"))
        return [make_document(source, "body", text, title=title)], []
    if kind == "text":
        return [make_document(source, "body", content.decode("utf-8-sig"))], []
    raise ValueError(f"Unsupported source kind: {kind}")


def read_sources(path: Path) -> list[dict]:
    sources = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(sources, list) or not sources:
        raise ValueError("Source manifest must be a nonempty JSON list")
    seen = set()
    for source in sources:
        for key in ("id", "source", "url", "kind", "profile"):
            if not isinstance(source.get(key), str) or not source[key]:
                raise ValueError(f"Missing or invalid manifest field: {key}")
        if not re.fullmatch(r"[a-z0-9_-]+", source["id"]) or source["id"] in seen:
            raise ValueError(f"Invalid or duplicate source id: {source['id']}")
        seen.add(source["id"])
        if source["profile"] not in PROFILES or source["kind"] not in {"html", "pdf", "reddit", "text"}:
            raise ValueError(f"Invalid kind/profile for {source['id']}")
    return sources


def write_jsonl(path: Path, records: list[dict]) -> None:
    path.write_text("".join(json.dumps(record, ensure_ascii=False) + "\n" for record in records), encoding="utf-8")


def run(manifest: Path, output: Path, *, offline=False, tokenizer=None) -> dict:
    sources = read_sources(manifest)
    output.mkdir(parents=True, exist_ok=True)
    raw_dir = output / "raw"
    raw_dir.mkdir(exist_ok=True)
    documents, chunks, summaries = [], [], []
    timestamp = datetime.now(timezone.utc).isoformat()
    with requests.Session() as session:
        session.headers["User-Agent"] = "HowardResearchGuide/0.1 (educational document ingestion)"
        session.mount("https://", HTTPAdapter(max_retries=Retry(
            total=2, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504],
            respect_retry_after_header=False,
        )))
        for source in sources:
            summary = {"source_id": source["id"], "source": source["source"], "url": source["url"]}
            try:
                suffix = {"reddit": "json", "text": "txt"}.get(source["kind"], source["kind"])
                raw_path = raw_dir / f"{source['id']}.{suffix}"
                resolved_url = source["url"]
                if source.get("local_path"):
                    raw_path = manifest.resolve().parent / source["local_path"]
                    content = raw_path.read_bytes()
                    mode = "local"
                elif offline:
                    content = raw_path.read_bytes()
                    mode = "cached"
                else:
                    url = source["url"]
                    if source["kind"] == "reddit":
                        url = url.rstrip("/") + ".json?raw_json=1&limit=500"
                    response = session.get(url, timeout=(10, 30))
                    response.raise_for_status()
                    content = response.content
                    resolved_url = response.url
                    raw_path.write_bytes(content)
                    mode = "downloaded"
                loaded, warnings = extract(content, source)
                loaded = [doc for doc in loaded if doc["text"].strip()]
                if not loaded:
                    raise ValueError("Source yielded no usable text")
                for doc in loaded:
                    doc["metadata"].update(raw_path=str(raw_path), load_mode=mode, processed_at=timestamp)
                source_chunks = chunk_documents(loaded)
                if tokenizer is not None:
                    validate_token_lengths(source_chunks, tokenizer)
                char_count = sum(len(doc["text"]) for doc in loaded)
                if char_count < 300 or len(source_chunks) <= 2:
                    warnings.append("Thin source: manually inspect extracted text for useful content.")
                documents.extend(loaded)
                chunks.extend(source_chunks)
                summary.update(status="ok", characters=char_count, documents=len(loaded),
                               chunks=len(source_chunks), warnings=warnings, load_mode=mode,
                               resolved_url=resolved_url)
            except (requests.RequestException, OSError, ValueError, KeyError, IndexError, TypeError, PDFException, PSException) as exc:
                summary.update(status="error", error=str(exc), characters=0, documents=0, chunks=0)
            summaries.append(summary)
            print(f"{source['id']}: {summary['status']} — {summary.get('error', str(summary['chunks']) + ' chunks')}")
    report = {
        "processed_at": timestamp,
        "token_lengths_checked": tokenizer is not None,
        "source_count": len(sources),
        "successful_sources": sum(s["status"] == "ok" for s in summaries),
        "document_count": len(documents), "chunk_count": len(chunks), "sources": summaries,
    }
    write_jsonl(output / "documents.jsonl", documents)
    write_jsonl(output / "chunks.jsonl", chunks)
    (output / "report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources", type=Path, default=ROOT / "sources.json")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "documents" / "processed")
    parser.add_argument("--offline", action="store_true", help="Use cached raw files or manifest local_path entries; never fetch sources")
    parser.add_argument("--check-tokens", action="store_true", help="Validate against the MiniLM tokenizer's 256-token limit (may download tokenizer)")
    args = parser.parse_args()
    tokenizer = None
    if args.check_tokens:
        from transformers import AutoTokenizer
        tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2", local_files_only=args.offline)
    report = run(args.sources, args.output_dir, offline=args.offline, tokenizer=tokenizer)
    print(f"Wrote {report['chunk_count']} chunks; {report['successful_sources']}/{report['source_count']} sources succeeded. See {args.output_dir / 'report.json'}")
    return 0 if report["successful_sources"] == report["source_count"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

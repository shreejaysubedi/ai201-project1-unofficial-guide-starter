"""Offline behavior tests using real Chroma and tiny deterministic test vectors."""

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import chromadb
from chromadb.api.models.Collection import Collection
import numpy as np

from embeddings import build_index
from evaluate_retrieval import evaluation_questions
from retrieval import Retriever


class TestTokenizer:
    def encode(self, text, **kwargs):
        return [0] * (len(text.split()) + 2)


class TestEncoder:
    tokenizer = TestTokenizer()

    def encode(self, texts, **kwargs):
        vectors = np.zeros((len(texts), 384), dtype=np.float32)
        for row, text in enumerate(texts):
            # Explicit angles let tests distinguish cosine distance from squared L2.
            vectors[row, :2] = [0.8, 0.6] if "lab" in text else [1.0, 0.0]
        return vectors


def chunk(identifier, text, index=0):
    return {"id": identifier, "text": text, "metadata": {
        "source": "Howard test guide", "source_id": "test-guide", "document_id": "test-guide:body",
        "url": "https://example.org/research", "chunk_index": index,
    }}


class RetrievalTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.path = self.root / "chunks.jsonl"
        self.db = self.root / "db"
        self.model = TestEncoder()

    def write_chunks(self, records):
        self.path.write_text("".join(json.dumps(c) + "\n" for c in records))

    def build(self):
        return build_index(self.path, self.db, model=self.model)

    def test_persistence_cosine_ranking_full_text_and_attribution(self):
        records = [chunk("funding", "scholarship support", 3), chunk("lab", "faculty lab mentorship", 8)]
        self.write_chunks(records)
        self.assertEqual(self.build()["chunks"], 2)
        retriever = Retriever(self.db, model=self.model)
        results = retriever.retrieve("scholarship", k=5)
        self.assertEqual([r["id"] for r in results], ["funding", "lab"])
        self.assertAlmostEqual(results[0]["distance"], 0.0, places=5)
        self.assertAlmostEqual(results[1]["distance"], 0.2, places=5)
        self.assertEqual(results[1]["text"], records[1]["text"])
        self.assertEqual(results[1]["metadata"]["chunk_index"], 8)
        self.assertEqual(results[1]["metadata"]["url"], records[1]["metadata"]["url"])
        self.assertEqual(Retriever(self.db, model=self.model).retrieve("lab")[0]["id"], "lab")

    def test_reindex_updates_records_without_duplicates_and_removes_retired_sources(self):
        self.write_chunks([chunk("retired", "old source"), chunk("keep", "old text")])
        self.build()
        self.write_chunks([chunk("keep", "updated lab text", 2), chunk("new", "new guide")])
        self.assertEqual(self.build()["removed_stale_chunks"], 1)
        self.assertEqual(self.build()["chunks"], 2)
        results = Retriever(self.db, model=self.model).retrieve("lab", k=20)
        self.assertEqual({r["id"] for r in results}, {"keep", "new"})
        self.assertEqual(results[0]["text"], "updated lab text")

    def test_invalid_input_and_token_overflow_preserve_previous_index(self):
        self.write_chunks([chunk("good", "original guide")])
        self.build()
        invalid_inputs = [
            [], [chunk("same", "one"), chunk("same", "two")],
            [chunk("bad", "word " * 255)],  # 257 tokens with special tokens
            [chunk("bad", "missing position", -1)],
            [{"id": "bad", "text": "no metadata"}],
        ]
        for records in invalid_inputs:
            self.write_chunks(records)
            with self.assertRaises(ValueError):
                self.build()
        self.assertEqual(Retriever(self.db, model=self.model).retrieve("guide")[0]["id"], "good")

    def test_missing_index_and_invalid_queries(self):
        with self.assertRaisesRegex(ValueError, "run embeddings.py"):
            Retriever(self.db, model=self.model)
        self.write_chunks([chunk("good", "guide")])
        self.build()
        retriever = Retriever(self.db, model=self.model)
        for query, k in [(" ", 5), (None, 5), ("test", 0), ("test", True), ("word " * 255, 5)]:
            with self.assertRaises(ValueError):
                retriever.retrieve(query, k)

    def test_source_prefix_is_counted_toward_token_limit(self):
        record = chunk("too-long-with-source", "word " * 251)
        self.write_chunks([record])
        with self.assertRaisesRegex(ValueError, "source \\+ text"):
            self.build()

    def test_interrupted_write_cannot_be_queried_until_rebuilt(self):
        self.write_chunks([chunk("good", "guide")])
        self.build()
        retriever = Retriever(self.db, model=self.model)
        with patch.object(Collection, "upsert", side_effect=RuntimeError("disk failure")):
            with self.assertRaisesRegex(RuntimeError, "disk failure"):
                self.build()
        with self.assertRaisesRegex(ValueError, "incomplete"):
            retriever.retrieve("guide")
        self.build()
        self.assertEqual(retriever.retrieve("guide")[0]["id"], "good")

    def test_wrong_distance_configuration_is_rejected(self):
        self.write_chunks([chunk("good", "guide")])
        client = chromadb.PersistentClient(path=str(self.db))
        from embeddings import INDEX_METADATA
        client.create_collection("howard_research", embedding_function=None,
                                 configuration={"hnsw": {"space": "l2"}}, metadata=INDEX_METADATA)
        with self.assertRaisesRegex(ValueError, "cosine"):
            self.build()

    def test_evaluation_uses_current_planning_questions(self):
        path = Path(__file__).resolve().parents[1] / "planning.md"
        questions = evaluation_questions(path)
        self.assertIn("Karsh", questions[1])
        self.assertIn("Amgen", questions[3])
        self.assertIn("Afro-American", questions[4])


if __name__ == "__main__":
    unittest.main()

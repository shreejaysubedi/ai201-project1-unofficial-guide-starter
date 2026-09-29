"""Stage 4: retrieve full chunks with citation metadata and cosine distances."""

import argparse
import json
from pathlib import Path

import chromadb
from chromadb.errors import NotFoundError

from embeddings import COLLECTION_NAME, DEFAULT_DB, MAX_TOKENS, check_collection, load_model


class Retriever:
    """Create once and reuse so the local embedding model stays loaded."""

    def __init__(self, db_path: Path = DEFAULT_DB, collection_name: str = COLLECTION_NAME, *, offline=False, model=None):
        self.client = chromadb.PersistentClient(path=str(db_path))
        try:
            self.collection = self.client.get_collection(collection_name, embedding_function=None)
        except NotFoundError as exc:
            raise ValueError("No research index found; run embeddings.py first") from exc
        check_collection(self.collection)
        self.model = model if model is not None else load_model(offline=offline)

    def retrieve(self, query: str, k: int = 5) -> list[dict]:
        """Return nearest chunks in ascending distance order; lower is closer.

        Scores are cosine distances, not confidence probabilities. No source
        filter or hard distance cutoff is applied to this baseline retriever.
        """
        if not isinstance(query, str) or not query.strip():
            raise ValueError("Query must contain text")
        if type(k) is not int or k <= 0:
            raise ValueError("k must be a positive integer")
        query = query.strip()
        token_count = len(self.model.tokenizer.encode(query, add_special_tokens=True, truncation=False))
        if token_count > MAX_TOKENS:
            raise ValueError(f"Query has {token_count} tokens; shorten it to at most {MAX_TOKENS}")
        # Refresh metadata in case another build was interrupted since construction.
        self.collection = self.client.get_collection(self.collection.name, embedding_function=None)
        check_collection(self.collection)
        count = self.collection.count()
        if count == 0:
            return []
        vector = self.model.encode([query], normalize_embeddings=True, convert_to_numpy=True)
        result = self.collection.query(
            query_embeddings=vector.tolist(), n_results=min(k, count),
            include=["documents", "metadatas", "distances"],
        )
        # Chroma supports batches of queries, so each field has an outer query list.
        return [
            {"id": identifier, "text": text, "metadata": metadata, "distance": float(distance)}
            for identifier, text, metadata, distance in zip(
                result["ids"][0], result["documents"][0], result["metadatas"][0], result["distances"][0],
            )
        ]


def print_results(query: str, results: list[dict]) -> None:
    print(f"\nQuery: {query}")
    for rank, result in enumerate(results, 1):
        metadata = result["metadata"]
        print(f"\n[{rank}] distance={result['distance']:.4f} | {metadata['source']}")
        print(f"Chunk position (zero-based): {metadata['chunk_index']} | ID: {result['id']}")
        print(f"Source: {metadata['url']}")
        print(result["text"])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query")
    parser.add_argument("--k", type=int, default=5)
    parser.add_argument("--db-dir", type=Path, default=DEFAULT_DB)
    parser.add_argument("--collection", default=COLLECTION_NAME)
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--json", action="store_true", help="Print structured results")
    args = parser.parse_args()
    results = Retriever(args.db_dir, args.collection, offline=args.offline).retrieve(args.query, args.k)
    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        print_results(args.query, results)


if __name__ == "__main__":
    main()

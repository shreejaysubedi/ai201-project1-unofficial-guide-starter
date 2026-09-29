"""Stage 3: embed ingestion JSONL and synchronize a persistent Chroma collection."""

import argparse
import hashlib
import json
import math
from pathlib import Path

import chromadb
from chromadb.errors import NotFoundError
from sentence_transformers import SentenceTransformer

from chunking import validate_token_lengths

ROOT = Path(__file__).resolve().parent
DEFAULT_CHUNKS = ROOT / "documents" / "processed" / "chunks.jsonl"
DEFAULT_DB = ROOT / "chroma_db"
COLLECTION_NAME = "howard_research"
MODEL_NAME = "all-MiniLM-L6-v2"
MODEL_ID = f"sentence-transformers/{MODEL_NAME}"
DIMENSIONS = 384
MAX_TOKENS = 256
INPUT_FORMAT = "source-and-text-v1"
INDEX_METADATA = {"embedding_model": MODEL_ID, "dimensions": DIMENSIONS, "max_tokens": MAX_TOKENS}


def load_model(*, offline: bool = False) -> SentenceTransformer:
    """CPU inference requires no API key; only the first download needs network."""
    model = SentenceTransformer(
        MODEL_NAME, device="cpu", cache_folder=str(ROOT / ".cache" / "sentence-transformers"),
        local_files_only=offline,
    )
    if model.get_sentence_embedding_dimension() != DIMENSIONS or model.max_seq_length != MAX_TOKENS:
        raise ValueError("Model does not match the planned 384 dimensions / 256 tokens")
    return model


def load_chunks(path: Path) -> list[dict]:
    chunks, seen = [], set()
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        record = json.loads(line)
        if not isinstance(record, dict):
            raise ValueError(f"Line {number}: expected a chunk object")
        identifier, text, metadata = record.get("id"), record.get("text"), record.get("metadata")
        if not isinstance(identifier, str) or not identifier.strip() or identifier in seen:
            raise ValueError(f"Line {number}: missing or duplicate chunk id")
        if not isinstance(text, str) or not text.strip() or not isinstance(metadata, dict):
            raise ValueError(f"Line {number}: missing text or metadata")
        for key in ("source", "source_id", "url", "document_id"):
            if not isinstance(metadata.get(key), str) or not metadata[key].strip():
                raise ValueError(f"{identifier}: missing citation field {key}")
        position = metadata.get("chunk_index")
        if type(position) is not int or position < 0:
            raise ValueError(f"{identifier}: chunk_index must be a nonnegative integer")
        # Chroma metadata must contain scalar values; never silently drop attribution.
        for key, value in metadata.items():
            if not isinstance(key, str) or not isinstance(value, (str, int, float, bool)):
                raise ValueError(f"{identifier}: unsupported metadata value for {key}")
            if isinstance(value, float) and not math.isfinite(value):
                raise ValueError(f"{identifier}: non-finite metadata value for {key}")
        seen.add(identifier)
        chunks.append(record)
    if not chunks:
        raise ValueError("No chunks found; run ingest.py first")
    return chunks


def check_collection(collection, *, ready: bool = True) -> None:
    metadata = collection.metadata or {}
    if any(metadata.get(key) != value for key, value in INDEX_METADATA.items()):
        raise ValueError("Collection uses another embedding model/schema; choose a different collection name")
    if collection.configuration.get("hnsw", {}).get("space") != "cosine":
        raise ValueError("Collection must use cosine distance; choose a different collection name")
    if ready and metadata.get("input_format") != INPUT_FORMAT:
        raise ValueError("Index uses an older embedding input format; run embeddings.py to rebuild")
    if ready and (metadata.get("index_ready") is not True or collection.count() != metadata.get("chunk_count")):
        raise ValueError("Index is incomplete; run embeddings.py before querying")


def build_index(
    chunks_path: Path = DEFAULT_CHUNKS, db_path: Path = DEFAULT_DB,
    collection_name: str = COLLECTION_NAME, *, model=None, offline: bool = False,
) -> dict:
    chunks = load_chunks(chunks_path)
    model = model if model is not None else load_model(offline=offline)
    # Recount from actual text instead of trusting the ingestion token_count field.
    validate_token_lengths(chunks, model.tokenizer, MAX_TOKENS)
    # Some requirement-list chunks omit their program/department name. Include
    # source context in the vector input while storing the original text intact.
    texts = [f"Source: {chunk['metadata']['source']}\n\n{chunk['text']}" for chunk in chunks]
    for chunk, text in zip(chunks, texts):
        count = len(model.tokenizer.encode(text, add_special_tokens=True, truncation=False))
        if count > MAX_TOKENS:
            raise ValueError(f"{chunk['id']}: source + text has {count} tokens (limit {MAX_TOKENS})")
        chunk["metadata"]["embedding_token_count"] = count
    vectors = model.encode(texts, batch_size=32, normalize_embeddings=True, convert_to_numpy=True)
    if vectors.shape != (len(chunks), DIMENSIONS):
        raise ValueError("Embedding output has an unexpected shape")
    if not all(math.isfinite(float(value)) for vector in vectors for value in vector):
        raise ValueError("Embedding output contains non-finite values")

    # Embedding/validation complete before touching an existing collection.
    client = chromadb.PersistentClient(path=str(db_path))
    try:
        collection = client.get_collection(collection_name, embedding_function=None)
        check_collection(collection, ready=False)
    except NotFoundError:
        collection = client.create_collection(
            name=collection_name, embedding_function=None,
            configuration={"hnsw": {"space": "cosine"}},
            metadata={**INDEX_METADATA, "index_ready": False},
        )
    # Upsert + stale deletion is not a transaction. Queries refuse an interrupted build.
    collection.modify(metadata={**INDEX_METADATA, "input_format": INPUT_FORMAT, "index_ready": False})
    ids = [chunk["id"] for chunk in chunks]
    batch_size = min(256, client.get_max_batch_size())
    for start in range(0, len(chunks), batch_size):
        batch = chunks[start:start + batch_size]
        collection.upsert(
            ids=ids[start:start + batch_size], documents=[chunk["text"] for chunk in batch],
            metadatas=[chunk["metadata"] for chunk in batch],
            embeddings=vectors[start:start + batch_size].tolist(),
        )
    # Content-derived chunk IDs change after re-ingestion; remove obsolete records.
    current = set(ids)
    stale = [identifier for identifier in collection.get(include=[])["ids"] if identifier not in current]
    for start in range(0, len(stale), batch_size):
        collection.delete(ids=stale[start:start + batch_size])
    fingerprint = hashlib.sha256(chunks_path.read_bytes()).hexdigest()
    if collection.count() != len(chunks):
        raise RuntimeError("Stored chunk count does not match input")
    collection.modify(metadata={
        **INDEX_METADATA, "input_format": INPUT_FORMAT, "index_ready": True,
        "chunk_count": len(chunks), "chunks_sha256": fingerprint,
    })
    return {
        "chunks": collection.count(), "sources": len({c["metadata"]["source_id"] for c in chunks}),
        "dimensions": DIMENSIONS, "distance": "cosine", "removed_stale_chunks": len(stale),
        "max_chunk_tokens": max(c["metadata"]["token_count"] for c in chunks),
        "max_embedding_tokens": max(c["metadata"]["embedding_token_count"] for c in chunks),
        "input_format": INPUT_FORMAT,
        "chunks_sha256": fingerprint, "collection": collection_name, "db_path": str(db_path),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chunks", type=Path, default=DEFAULT_CHUNKS)
    parser.add_argument("--db-dir", type=Path, default=DEFAULT_DB)
    parser.add_argument("--collection", default=COLLECTION_NAME)
    parser.add_argument("--offline", action="store_true", help="Load model only from the local cache")
    args = parser.parse_args()
    print(json.dumps(build_index(args.chunks, args.db_dir, args.collection, offline=args.offline), indent=2))


if __name__ == "__main__":
    main()

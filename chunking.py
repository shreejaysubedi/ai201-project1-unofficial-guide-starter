"""Character-based recursive chunking for the two profiles in planning.md."""

from dataclasses import dataclass
import hashlib
import re


@dataclass(frozen=True)
class ChunkProfile:
    size: int
    overlap: int


PROFILES = {
    "commentary": ChunkProfile(500, 100),
    "formal": ChunkProfile(800, 150),
}
# Prefer paragraphs, then lines, sentences, words, and finally characters.
SEPARATORS = (r"\n\n", r"\n", r"(?<=[.!?])\s+", r"\s+")


def _boundary(text: str, lower: int, upper: int, level: int = 0) -> int:
    if level == len(SEPARATORS):
        return upper
    matches = list(re.finditer(SEPARATORS[level], text[lower:upper]))
    if matches:
        return lower + matches[-1].end()
    return _boundary(text, lower, upper, level + 1)


def split_text(text: str, size: int, overlap: int) -> list[tuple[int, int]]:
    """Return contiguous spans with exact character overlap and no lost text.

    Natural breaks in the latter half of a window are preferred. Long words
    fall back to character splitting. Whitespace is retained so offsets and
    overlaps refer exactly to the cleaned document.
    """
    if not 0 <= overlap < size:
        raise ValueError("Require 0 <= overlap < size")
    if not text.strip():
        return []
    spans = []
    start = 0
    while start < len(text):
        end = min(start + size, len(text))
        if end < len(text):
            lower = start + max(overlap + 1, size // 2)
            end = _boundary(text, lower, end)
        spans.append((start, end))
        if end == len(text):
            break
        start = end - overlap
    return spans


def chunk_documents(documents: list[dict]) -> list[dict]:
    """Never merge separate documents (including individual Reddit comments)."""
    chunks = []
    for document in documents:
        metadata = document["metadata"]
        profile = PROFILES[metadata["profile"]]
        text = document["text"]
        for index, (start, end) in enumerate(split_text(text, profile.size, profile.overlap)):
            chunk_text = text[start:end]
            digest = hashlib.sha256(chunk_text.encode()).hexdigest()[:16]
            chunks.append({
                "id": f"{document['id']}:{index}:{digest}",
                "text": chunk_text,
                "metadata": {
                    **metadata,
                    "document_id": document["id"],
                    "chunk_index": index,
                    "start_char": start,
                    "end_char": end,
                    "char_count": len(chunk_text),
                    "chunk_size": profile.size,
                    "chunk_overlap": profile.overlap,
                },
            })
    return chunks


def validate_token_lengths(chunks: list[dict], tokenizer, limit: int = 256) -> None:
    """Count special tokens too; fail rather than silently truncate embeddings."""
    for chunk in chunks:
        count = len(tokenizer.encode(chunk["text"], add_special_tokens=True, truncation=False))
        chunk["metadata"]["token_count"] = count
        if count > limit:
            raise ValueError(f"{chunk['id']} has {count} tokens (limit {limit}); revise chunking before embedding")

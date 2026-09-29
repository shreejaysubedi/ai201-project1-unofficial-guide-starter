# Embedding and retrieval

The architecture in `planning.md` maps to these files:

1. `ingest.py` fetches and cleans the 10 sources.
2. `chunking.py` writes citation-bearing chunks through ingestion to
   `documents/processed/chunks.jsonl`.
3. `embeddings.py` loads MiniLM, embeds every chunk, and stores vectors, original
   text, and metadata in the `howard_research` collection in `./chroma_db`.
4. `retrieval.py` embeds a query with the same model and returns the closest five
   chunks by cosine distance, along with their attribution metadata.
5. Grounded answer generation through Groq and its answer UI are planned next.
   The current query CLI returns evidence, not a generated answer.

## Run it

Use the project virtual environment or another Python environment with
`requirements.txt` installed. Chroma is pinned to the tested version, 1.5.9.

```bash
python embeddings.py
python retrieval.py "What are the requirements for the Amgen Scholars Program?" --offline
python evaluate_retrieval.py --offline
python -m unittest discover -s tests -v
```

The first embedding run downloads the public `all-MiniLM-L6-v2` model to
`.cache/sentence-transformers/`. No API key or paid embedding service is involved.
Later commands can use `--offline`; it fails if model files are not cached.
Both the model cache and Chroma database are ignored by Git. Rebuild the index
after re-ingestion or cloning the project:

```bash
python embeddings.py --offline
python retrieval.py "How do I find a research mentor?" --offline --k 4 --json
python evaluate_retrieval.py --offline --questions 1 3 4 --k 5
```

`--chunks`, `--db-dir`, and `--collection` on `embeddings.py` select alternate
inputs and storage. Retrieval and evaluation accept the same database and
collection options. Rebuilding synchronizes that collection to the entire input
file, removing records no longer present; use separate collections for separate
corpora. Do not run builds concurrently with queries or other builds.

## Calling retrieval from Python

```python
from retrieval import Retriever

retriever = Retriever(offline=True)  # Keep this instance for repeated queries.
results = retriever.retrieve("How do I apply for independent study?", k=5)
for result in results:
    print(result["distance"], result["text"])
    print(result["metadata"]["source"], result["metadata"]["url"])
    print(result["metadata"]["document_id"], result["metadata"]["chunk_index"])
```

Each result contains `id`, full original `text`, `metadata`, and `distance`.
The source name, URL, document ID, zero-based chunk position, offsets, and other
ingestion metadata are preserved. `token_count` describes the chunk body;
`embedding_token_count` also includes its source prefix and special tokens.
Blank queries, invalid k, missing/incomplete indexes, and overlong queries fail
with explanatory errors. If k exceeds the collection size, all available chunks
are returned.

## What the Chroma calls mean

- `PersistentClient(path=...)` opens an on-disk database. Chroma saves writes
  automatically; no separate `persist()` call is needed.
- `create_collection(..., configuration={"hnsw": {"space": "cosine"}})` sets
  cosine distance for the collection's nearest-neighbor index. The code checks
  an existing collection's configuration instead of assuming it is correct.
- `embedding_function=None` disables Chroma's automatic text embedding. We
  explicitly supply vectors from SentenceTransformer for both stored chunks and
  queries, avoiding an accidental second model or backend.
- `upsert(ids=..., documents=..., metadatas=..., embeddings=...)` inserts new IDs
  and updates existing ones. Corresponding positions in these lists describe
  the same chunk. A second run does not append duplicates.
- `get(include=[])` reads IDs without transferring stored texts or vectors. The
  indexer compares these IDs with the input and deletes obsolete chunks.
- `query(query_embeddings=[vector], n_results=k, include=[...])` searches by
  the supplied vector and returns documents, metadata, and distances. IDs are
  returned automatically. Results are nested by query because Chroma accepts
  multiple queries in a single call; `[0]` selects our one query's results.

See the official [collection configuration documentation](https://docs.trychroma.com/docs/collections/configure)
and [query documentation](https://docs.trychroma.com/docs/querying-collections/query-and-get).

The model is loaded as `SentenceTransformer("all-MiniLM-L6-v2", ...)` with CPU
inference and a project cache. `encode(..., normalize_embeddings=True)` produces
unit-length, 384-dimensional vectors. Cosine distance is `1 - cosine_similarity`:
smaller distances mean closer vectors, not higher factual confidence. The rough
0.6–0.7 weak-match heuristic is a debugging aid, not a universal rejection rule.
Even a low-distance result can concern the wrong program.

## Debugging the first retrieval run

The initial index embedded only chunk bodies. For planning questions 1, 3, and 4:

- Karsh's required-summer-internships chunk was absent from the first five hits.
- Amgen returned all five relevant program chunks.
- Afro-American Studies returned only two department chunks, with general
  research and Amgen requirements occupying the remaining positions.

Inspection of full text and metadata showed correct attribution, but important
lists omitted their program or department name. The final embedding input is
`Source: <source name>`, two newlines, then the original chunk. The stored text is
unchanged. Both the body and the complete embedding input are token-checked to
prevent MiniLM's 256-token truncation. The longest body is 193 tokens and the
longest contextual input is 200 tokens in the 88-chunk corpus.

This brought the Karsh requirements list to rank 3 and the full-time AFRO faculty
advisor rule to rank 3; all four department chunks now precede other sources.
The original and final runs are saved in
`evaluation/retrieval_baseline.json` and `evaluation/retrieval_results.json`.
The README includes full final results and manual relevance assessments.

The default remains k=5 as planned. All key requirements appear in the first
three hits for these queries, so more hits are not automatically better: Karsh
still includes Amgen and general R1 reporting in ranks 4–5, and independent study
has a general opportunity list at rank 5. A broader evaluation is needed before
changing the default or adding reranking. This run supports improving source
context without increasing chunk sizes; it does not prove all seven evaluation
queries work. Opening fragments and some Hilltop advertisement text remain known
ingestion issues. Future generation must not combine different programs' rules.

## Integrity checks

The indexer validates required attribution fields, unique IDs, text, metadata
types, token limits, finite vectors, dimensions, model identity, and cosine
configuration. Encoding finishes before existing records are changed. During
upserts and stale-record removal, the collection is marked incomplete; queries
refuse that state after an interrupted build. These operations are not a database
transaction, so concurrent indexing and querying are not supported.

Tests use small deterministic vectors with real temporary Chroma databases;
they verify cosine ranking, attribution, update/removal behavior, validation,
interrupted-build recovery, and incompatible configurations without downloading
a model. The three saved evaluation queries separately exercise the actual
MiniLM model against the complete stored corpus.

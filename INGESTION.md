# Ingestion and chunking

Run from the project directory with Python 3.10 or newer and the dependencies in
`requirements.txt` installed. With the existing virtual environment:

```bash
.venv/bin/python ingest.py --check-tokens
```

The loader fetches the 10 HTML sources configured in `sources.json`. The Dig
student profile and the Afro-American Studies Independent Study guide replace
the inaccessible Reddit thread and Political Science PDF. It parses HTML
with Beautiful Soup, removes navigation/footer/script content, and normalizes
Unicode and whitespace using regex while preserving paragraph breaks. It reads
PDF text with pdfplumber, retaining page numbers, when a manifest includes PDFs.
Optional Reddit support uses the public thread
JSON endpoint, retaining authors and comment permalinks; each comment is a
separate document, including nested replies. Deleted comments are skipped, and
unexpanded comment listings produce an incompleteness warning. Scanned PDFs need
OCR or manually prepared text; blank pages are reported.

The recursive chunker prefers paragraphs, lines, sentence endings, then spaces.
It falls back to character boundaries for long unbroken text. The Dig and Hilltop
use at most 500 characters with exactly 100 characters of overlap. Official
sources use at most 800 characters with exactly 150 characters of overlap.
Natural endpoints are selected in the latter half of each window so chunks keep
useful context and make forward progress. Overlap starts may fall inside a word
or sentence; exact character overlap does not guarantee complete sentences.
Chunks never span documents, Reddit comments, or PDF pages.

## Outputs

Each run replaces the generated JSON outputs in `documents/processed/`:

- `raw/`: downloaded HTML, PDF, and Reddit JSON snapshots.
- `documents.jsonl`: cleaned documents, with citation and provenance metadata.
- `chunks.jsonl`: one record per chunk, with `id`, `text`, and `metadata`.
- `report.json`: per-source errors, character counts, chunk counts, and warnings
  for thin content or incomplete extraction.

Chunk metadata contains source name, original URL (comment permalink for Reddit
comments), source ID, profile, document ID, zero-based chunk index, character
offsets with an exclusive end, size, and overlap. PDF page numbers are one-based.
IDs are deterministic for unchanged text; timestamps and paths are provenance,
not part of the ID. These records can later be converted to Chroma's `ids`,
`documents`, and `metadatas` inputs.

Failures do not prevent other sources from processing. Any failed source makes
the CLI exit with status 1; successful sources remain in the output. Inspect the
report before treating the corpus as complete. A successful extraction does not
verify the factual accuracy or completeness of a webpage.

## Token validation

`--check-tokens` loads the `sentence-transformers/all-MiniLM-L6-v2` tokenizer and
counts tokens including special tokens. Its first use may download the tokenizer.
The check enforces the embedding model's 256-token limit explicitly, even though
the underlying tokenizer advertises a larger limit. A source containing an
oversized chunk is reported as failed, rather than silently truncating text.
Revise the chunking plan before reducing sizes to resolve such a failure.

Without this flag, only character limits are enforced; character counts do not
guarantee token counts. `report.json` records whether token validation ran.

## Offline runs and local source files

Reuse snapshots without fetching sources:

```bash
.venv/bin/python ingest.py --offline --check-tokens
```

Offline token validation requires a cached tokenizer. To use an exported source,
add a `local_path` to that source's entry in `sources.json`. Relative paths are
resolved against the manifest's directory. Preserve its original `url` and
`profile` for citation and chunking. Use `kind: "html"` for saved HTML, `"pdf"`
for PDF, `"reddit"` for exported thread JSON, or `"text"` for UTF-8 plain text.
Reddit JSON preserves comment attribution; a plain-text thread export does not
automatically identify individual authors or comment boundaries.

You can also use a separate manifest and output folder:

```bash
.venv/bin/python ingest.py --sources local-sources.json --output-dir documents/local-run --offline
```

Only `documents/processed/` is ignored by Git by default. An HTML source can
specify a CSS `selector` to target its content; a missing selector fails visibly.
An optional `exclude_selector` removes source-specific non-content elements.
The Dig selector targets the article body, excluding recommendations and sharing
controls; its exclusion removes hidden image labels. The Afro-American Studies
exclusion removes the decorative quotation sidebar without removing guidance.

## Verification

```bash
.venv/bin/python -m unittest discover -s tests -v
```

Tests run without network access and cover exact overlaps, character limits,
complete text preservation, stable IDs, token overflow rejection, HTML cleaning,
real PDF text extraction, Reddit comment isolation, and partial offline runs.

On September 27, 2026, all 10 updated live sources loaded successfully. After
source-specific cleanup, the cached rerun produced 88 chunks: The Dig supplied
17 and Afro-American Studies supplied 4. All chunks passed MiniLM’s 256-token
check; the maximum was 193 tokens. The README contains five actual samples,
including both replacements, and a per-source count breakdown.

The removed sources are no longer in the active manifest or generated corpus.
PDF and Reddit loaders remain available and tested for other manifests. The
planning document now evaluates Afro-American Studies requirements and includes
a student-experience question grounded in The Dig profile. Its negative funding
question asks about the limits of the collected evidence rather than asserting
an unsupported university-wide rule.

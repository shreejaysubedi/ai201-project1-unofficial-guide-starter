"""Print and save actual top-k results for selected planning.md evaluation queries."""

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re

from embeddings import COLLECTION_NAME, DEFAULT_DB, MODEL_ID, ROOT
from retrieval import Retriever, print_results


def evaluation_questions(path: Path) -> dict[int, str]:
    section = path.read_text(encoding="utf-8").split("## Evaluation Plan", 1)[1].split("\n## ", 1)[0]
    questions = {}
    for line in section.splitlines():
        if re.match(r"\|\s*\d+\s*\|", line):
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            questions[int(cells[0])] = cells[1]
    return questions


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--planning", type=Path, default=ROOT / "planning.md")
    parser.add_argument("--questions", type=int, nargs="+", default=[1, 3, 4])
    parser.add_argument("--k", type=int, default=5)
    parser.add_argument("--db-dir", type=Path, default=DEFAULT_DB)
    parser.add_argument("--collection", default=COLLECTION_NAME)
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--output", type=Path, default=ROOT / "evaluation" / "retrieval_results.json")
    args = parser.parse_args()
    questions = evaluation_questions(args.planning)
    if any(number not in questions for number in args.questions):
        parser.error("Question numbers must exist in planning.md's Evaluation Plan")
    retriever = Retriever(args.db_dir, args.collection, offline=args.offline)
    runs = []
    for number in args.questions:
        query = questions[number]
        results = retriever.retrieve(query, k=args.k)
        print_results(query, results)
        runs.append({"question_number": number, "query": query, "results": results})
    report = {
        "evaluated_at": datetime.now(timezone.utc).isoformat(), "model": MODEL_ID,
        "distance_metric": "cosine", "k": args.k, "collection": args.collection,
        "indexed_chunks": retriever.collection.count(),
        "input_format": retriever.collection.metadata["input_format"],
        "chunks_sha256": retriever.collection.metadata["chunks_sha256"], "queries": runs,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"\nSaved complete results to {args.output}")


if __name__ == "__main__":
    main()

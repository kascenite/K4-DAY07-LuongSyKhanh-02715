#!/usr/bin/env python3
"""Bài tập 3.1 — baseline vs. tuned RecursiveChunker on the data/ecommerce/ corpus.

Loads every .md document in data/ecommerce/, runs the baseline
ChunkingStrategyComparator (default settings), then compares it against a
heading/section-aware RecursiveChunker tuned for this corpus's Markdown
structure. Prints a copy-pasteable comparison table.
"""

from __future__ import annotations

import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src import ChunkingStrategyComparator, Document, RecursiveChunker

DATA_DIR = ROOT / "data" / "ecommerce"
BASELINE_CHUNK_SIZE = 200
TUNED_CHUNK_SIZE = 400
TUNED_SEPARATORS = ["\n## ", "\n### ", "\n\n", ". ", " ", ""]


def parse_frontmatter(path: Path) -> Document:
    """Split '---\\n<yaml>\\n---\\n<body>' into a Document (no PyYAML dependency)."""
    text = path.read_text(encoding="utf-8")
    metadata: dict[str, str] = {}
    content = text

    if text.startswith("---\n"):
        end = text.find("\n---\n", 4)
        if end != -1:
            front_matter = text[4:end]
            content = text[end + 5 :].lstrip("\n")
            for line in front_matter.splitlines():
                if ":" not in line:
                    continue
                key, _, value = line.partition(":")
                value = value.strip()
                if not value.startswith('"') and " #" in value:
                    value = value.split(" #", 1)[0].strip()
                metadata[key.strip()] = value.strip('"')

    doc_id = metadata.get("doc_id", path.stem)
    return Document(id=doc_id, content=content, metadata=metadata)


def load_corpus() -> list[Document]:
    return [parse_frontmatter(p) for p in sorted(DATA_DIR.glob("*.md"))]


def summarize(chunks: list[str]) -> dict:
    lengths = [len(c) for c in chunks]
    return {
        "count": len(chunks),
        "avg_length": round(statistics.mean(lengths), 1) if lengths else 0,
        "min_length": min(lengths) if lengths else 0,
        "max_length": max(lengths) if lengths else 0,
    }


def print_table(title: str, rows: dict[str, dict]) -> None:
    print(f"\n=== {title} ===")
    header = f"{'strategy':<24}{'count':>8}{'avg_len':>10}{'min_len':>10}{'max_len':>10}"
    print(header)
    print("-" * len(header))
    for name, stats in rows.items():
        print(
            f"{name:<24}{stats['count']:>8}{stats['avg_length']:>10}"
            f"{stats['min_length']:>10}{stats['max_length']:>10}"
        )


def main() -> int:
    docs = load_corpus()
    if not docs:
        print(f"No documents found in {DATA_DIR}")
        return 1

    print(f"Loaded {len(docs)} documents from {DATA_DIR}:")
    for doc in docs:
        print(f"  - {doc.id} (audience={doc.metadata.get('audience', '?')}, {len(doc.content)} chars)")

    tuned_chunker = RecursiveChunker(separators=TUNED_SEPARATORS, chunk_size=TUNED_CHUNK_SIZE)

    for doc in docs:
        baseline = ChunkingStrategyComparator().compare(doc.content, chunk_size=BASELINE_CHUNK_SIZE)
        tuned_chunks = tuned_chunker.chunk(doc.content)

        rows = {
            "fixed_size (baseline)": summarize(baseline["fixed_size"]["chunks"]),
            "by_sentences (baseline)": summarize(baseline["by_sentences"]["chunks"]),
            "recursive (baseline, size=200)": summarize(baseline["recursive"]["chunks"]),
            "recursive (tuned, headings, size=400)": summarize(tuned_chunks),
        }
        print_table(f"{doc.id} ({len(doc.content)} chars)", rows)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

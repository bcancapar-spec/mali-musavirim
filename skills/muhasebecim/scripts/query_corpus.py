#!/usr/bin/env python3
"""Search a Muhasebecim local corpus without network access."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any


MASK_PATTERNS = [
    (re.compile(r"\b\d{11}\b"), "[MASKED_TCKN]"),
    (re.compile(r"\b\d{10}\b"), "[MASKED_VKN]"),
    (re.compile(r"\bTR\d{24}\b", re.IGNORECASE), "[MASKED_IBAN]"),
]


class QueryError(ValueError):
    pass


def load_index(corpus: Path) -> list[dict[str, Any]]:
    path = corpus / "index.jsonl"
    if not path.is_file():
        raise QueryError(f"index not found: {path}")
    records = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise QueryError(f"invalid JSON at index line {line_number}") from exc
    return records


def mask(text: str) -> str:
    for pattern, replacement in MASK_PATTERNS:
        text = pattern.sub(replacement, text)
    return text


def active_on(record: dict[str, Any], as_of: date) -> bool:
    start = date.fromisoformat(record["effective_from"]) if record.get("effective_from") else None
    end = date.fromisoformat(record["effective_to"]) if record.get("effective_to") else None
    return (start is None or start <= as_of) and (end is None or as_of <= end)


def latest_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    superseded = {record.get("supersedes") for record in records if record.get("supersedes")}
    return [record for record in records if record.get("record_id") not in superseded]


def snippets(text: str, pattern: re.Pattern[str], context: int, limit: int) -> list[str]:
    output = []
    for match in pattern.finditer(text):
        start = max(match.start() - context, 0)
        end = min(match.end() + context, len(text))
        output.append(re.sub(r"\s+", " ", text[start:end]).strip())
        if len(output) >= limit:
            break
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", required=True, type=Path)
    parser.add_argument("--query", required=True)
    parser.add_argument("--authority")
    parser.add_argument("--document-type")
    parser.add_argument("--status")
    parser.add_argument("--tag")
    parser.add_argument("--as-of", type=date.fromisoformat)
    parser.add_argument("--all-versions", action="store_true")
    parser.add_argument("--regex", action="store_true")
    parser.add_argument("--case-sensitive", action="store_true")
    parser.add_argument("--no-mask", action="store_true")
    parser.add_argument("--context", type=int, default=160)
    parser.add_argument("--limit", type=int, default=20)
    args = parser.parse_args()

    try:
        corpus = args.corpus.resolve()
        records = load_index(corpus)
        if not args.all_versions:
            records = latest_records(records)
        flags = 0 if args.case_sensitive else re.IGNORECASE
        pattern = re.compile(args.query if args.regex else re.escape(args.query), flags)
        results = []
        for record in records:
            if args.authority and args.authority.casefold() not in record.get("authority", "").casefold():
                continue
            if args.document_type and record.get("document_type") != args.document_type:
                continue
            if args.status and record.get("status") != args.status:
                continue
            if args.tag and args.tag not in record.get("tags", []):
                continue
            if args.as_of and not active_on(record, args.as_of):
                continue
            text_path = record.get("text_path")
            if not text_path:
                continue
            text_file = (corpus / text_path).resolve()
            try:
                text_file.relative_to(corpus)
            except ValueError as exc:
                raise QueryError("text path escapes corpus") from exc
            text = text_file.read_text(encoding="utf-8")
            found = snippets(text, pattern, max(args.context, 0), 3)
            if found:
                results.append(
                    {
                        "record_id": record["record_id"],
                        "authority": record["authority"],
                        "title": record["title"],
                        "status": record["status"],
                        "effective_from": record.get("effective_from"),
                        "effective_to": record.get("effective_to"),
                        "uri": record["uri"],
                        "snippets": found if args.no_mask else [mask(item) for item in found],
                    }
                )
                if len(results) >= max(args.limit, 1):
                    break
        print(json.dumps({"query": args.query, "count": len(results), "results": results}, ensure_ascii=False, indent=2))
        return 0
    except (QueryError, OSError, re.error, ValueError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Build a local-ingest manifest for selected official 2026 KGK standards."""

from __future__ import annotations

import argparse
import json
import re
from datetime import date
from pathlib import Path
from urllib.parse import quote


TFRS = {"1", "2", "3", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17"}
TMS = {"1", "2", "7", "8", "10", "12", "16", "19", "20", "21", "23", "24", "26", "27", "28", "29", "32", "33", "34", "36", "37", "38", "39", "40", "41"}
BASE = "https://www.kgk.gov.tr/Portalv2Uploads/files/Duyurular/v2/TMS_TFRS_Setleri/2026/Mavi_Kitap"


class CatalogError(ValueError):
    pass


def normalize_code(raw: str) -> tuple[str, str]:
    match = re.fullmatch(r"\s*(TMS|TFRS)[\s_-]*(\d+)\s*", raw.upper())
    if not match:
        raise CatalogError(f"invalid standard code: {raw}")
    family, number = match.groups()
    catalog = TMS if family == "TMS" else TFRS
    if number not in catalog:
        raise CatalogError(f"{family} {number} is not in the 2026 Mavi Kitap catalog")
    return family, number


def build_manifest(codes: list[str], as_of_date: str) -> dict[str, object]:
    try:
        normalized_as_of = date.fromisoformat(as_of_date).isoformat()
    except ValueError as exc:
        raise CatalogError("as-of must be YYYY-MM-DD") from exc
    normalized = sorted({normalize_code(code) for code in codes}, key=lambda item: (item[0], int(item[1])))
    if not normalized:
        raise CatalogError("at least one standard code is required")
    documents = []
    for family, number in normalized:
        filename = quote(f"{family} {number}.pdf")
        documents.append(
            {
                "uri": f"{BASE}/{family}/{filename}",
                "authority": "KGK",
                "title": f"{family} {number} — TFRS 2026 Seti (Mavi Kitap)",
                "document_type": "accounting_standard",
                "publication_date": None,
                "effective_from": "2026-01-01",
                "effective_to": "2026-12-31",
                "status": "in_force",
                "tags": [family.lower(), number, "2026", "mavi-kitap"],
                "pinpoint_hint": f"{family} {number}, ilgili paragraf",
                "scope": "public",
            }
        )
    return {"as_of_date": normalized_as_of, "allowed_hosts": ["kgk.gov.tr"], "documents": documents}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--standards", nargs="+", required=True, help="Examples: TMS-2 TMS-16 TFRS-15")
    parser.add_argument("--as-of", required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        manifest = build_manifest(args.standards, args.as_of)
    except CatalogError as exc:
        parser.error(str(exc))
    rendered = json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

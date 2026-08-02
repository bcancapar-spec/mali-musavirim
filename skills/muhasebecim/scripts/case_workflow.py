#!/usr/bin/env python3
"""Create and validate a local end-to-end Muhasebecim case workspace."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any


VERSION = "0.0.2"
CASE_ID = re.compile(r"^[a-z0-9][a-z0-9_-]{0,63}$")
REQUIRED_FACTS = {
    "as_of_date",
    "period_start",
    "period_end",
    "entity_type",
    "purpose",
    "reporting_framework",
    "tax_layer",
    "materiality",
    "currency",
}


class WorkflowError(ValueError):
    pass


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes((json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise WorkflowError(f"missing file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise WorkflowError(f"invalid JSON: {path}: {exc}") from exc


def init_case(case_dir: Path, case_id: str, as_of_date: str) -> dict[str, Any]:
    if not CASE_ID.fullmatch(case_id):
        raise WorkflowError("case-id must use lowercase letters, digits, underscore, or hyphen")
    try:
        normalized_date = date.fromisoformat(as_of_date).isoformat()
    except ValueError as exc:
        raise WorkflowError("as-of must be YYYY-MM-DD") from exc
    case_dir = case_dir.resolve()
    if case_dir.exists() and any(case_dir.iterdir()):
        raise WorkflowError("case directory must not contain files")
    for name in ("calculations", "documents", "workpapers", "outputs", "corpus"):
        (case_dir / name).mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).isoformat()
    case = {
        "schema_version": 1,
        "case_id": case_id,
        "status": "open",
        "created_at": now,
        "updated_at": now,
        "requires_calculation": True,
        "requires_journal": False,
        "requires_thp_validation": False,
        "requires_inspection_readiness": False,
        "requires_ymm_certification": False,
        "requires_tax_reconciliation": False,
    }
    facts = {
        "as_of_date": normalized_date,
        "period_start": "",
        "period_end": "",
        "entity_type": "",
        "purpose": "",
        "reporting_framework": "unresolved",
        "tax_layer": "VUK/MSUGT",
        "materiality": "",
        "currency": "TRY",
        "facts": [],
        "assumptions": [],
        "open_items": [],
    }
    write_json(case_dir / "case.json", case)
    write_json(case_dir / "facts.json", facts)
    write_json(case_dir / "sources.json", {"sources": []})
    write_json(case_dir / "review.json", {"prepared_by": "", "review_status": "pending_professional_review", "reviewed_by": "", "reviewed_at": None})
    (case_dir / "workpapers" / "analysis.md").write_bytes(b"# Analysis\n\n")
    return {"ok": True, "case_dir": str(case_dir), "case_id": case_id, "status": "open"}


def gate(name: str, passed: bool, details: Any) -> dict[str, Any]:
    return {"name": name, "passed": passed, "details": details}


def _valid_iso(value: Any) -> bool:
    try:
        date.fromisoformat(str(value))
        return True
    except ValueError:
        return False


def _valid_receipt(value: Any) -> bool:
    if not isinstance(value, dict) or not isinstance(value.get("receipt_sha256"), str):
        return False
    supplied = value["receipt_sha256"]
    payload = dict(value)
    del payload["receipt_sha256"]
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    actual = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return supplied == actual


def check_case(case_dir: Path) -> dict[str, Any]:
    case_dir = case_dir.resolve()
    case = read_json(case_dir / "case.json")
    facts = read_json(case_dir / "facts.json")
    source_root = read_json(case_dir / "sources.json")
    gates = []

    if not isinstance(facts, dict):
        raise WorkflowError("facts.json root must be an object")
    missing = sorted(key for key in REQUIRED_FACTS if not facts.get(key))
    date_errors = sorted(key for key in ("as_of_date", "period_start", "period_end") if facts.get(key) and not _valid_iso(facts[key]))
    unresolved = facts.get("reporting_framework") == "unresolved"
    gates.append(gate("scope_and_facts", not missing and not date_errors and not unresolved, {"missing": missing, "invalid_dates": date_errors, "reporting_framework_unresolved": unresolved}))

    sources = source_root.get("sources") if isinstance(source_root, dict) else None
    source_errors = []
    if not isinstance(sources, list) or not sources:
        source_errors.append("at least one source is required")
        sources = []
    for index, source in enumerate(sources):
        if not isinstance(source, dict):
            source_errors.append(f"sources[{index}] must be an object")
            continue
        for key in ("authority", "title", "url", "status", "accessed_at", "pinpoint"):
            if not source.get(key):
                source_errors.append(f"sources[{index}].{key} is required")
        if source.get("supports_conclusion") and source.get("status") != "in_force":
            source_errors.append(f"sources[{index}] supports a conclusion but is not in_force")
    gates.append(gate("sources", not source_errors, source_errors))

    analysis_path = case_dir / "workpapers" / "analysis.md"
    analysis_text = analysis_path.read_text(encoding="utf-8").strip() if analysis_path.is_file() else ""
    gates.append(gate("reasoning_workpaper", len(analysis_text) > len("# Analysis"), {"path": str(analysis_path), "characters": len(analysis_text)}))

    calculation_files = sorted((case_dir / "calculations").rglob("result*.json"))
    calculation_errors = []
    for path in calculation_files:
        value = read_json(path)
        if not isinstance(value, dict) or not value.get("input_sha256") or not value.get("result"):
            calculation_errors.append(f"invalid calculation envelope: {path.name}")
    calculation_required = bool(case.get("requires_calculation", True))
    calculation_passed = (not calculation_required) or (bool(calculation_files) and not calculation_errors)
    gates.append(gate("python_calculations", calculation_passed, {"required": calculation_required, "files": [str(path) for path in calculation_files], "errors": calculation_errors}))

    journal_required = bool(case.get("requires_journal", False))
    journal_path = case_dir / "outputs" / "journal-result.json"
    thp_path = case_dir / "outputs" / "thp-validation-result.json"
    if not journal_path.is_file() and thp_path.is_file():
        journal_path = thp_path
    journal_balanced = False
    if journal_path.is_file():
        journal = read_json(journal_path)
        result = journal.get("result", journal) if isinstance(journal, dict) else {}
        totals = result.get("totals", {}) if isinstance(result, dict) else {}
        engine_decision_ok = not isinstance(journal, dict) or journal.get("decision") in {None, "PASS", "PASS_WITH_WARNINGS"}
        journal_balanced = isinstance(result, dict) and engine_decision_ok and bool(result.get("balanced") or (isinstance(totals, dict) and totals.get("balanced")))
    gates.append(gate("journal", (not journal_required) or journal_balanced, {"required": journal_required, "path": str(journal_path), "balanced": journal_balanced}))

    thp_required = bool(case.get("requires_thp_validation", False))
    thp_passed = False
    thp_decision = None
    thp_receipt_valid = False
    if thp_path.is_file():
        thp_result = read_json(thp_path)
        if isinstance(thp_result, dict):
            thp_decision = thp_result.get("decision")
            thp_receipt_valid = _valid_receipt(thp_result)
            thp_engine = thp_result.get("engine", {})
            thp_passed = (
                isinstance(thp_engine, dict)
                and thp_engine.get("name") == "muhasebecim-thp-vuk"
                and thp_result.get("operation") in {"journal-validate", "trial-balance-validate", "account-validate"}
                and thp_decision in {"PASS", "PASS_WITH_WARNINGS"}
                and thp_receipt_valid
            )
    gates.append(gate(
        "thp_vuk_validation",
        (not thp_required) or thp_passed,
        {
            "required": thp_required,
            "path": str(thp_path),
            "decision": thp_decision,
            "receipt_valid": thp_receipt_valid,
            "passed": thp_passed,
        },
    ))

    professional_gate_specs = (
        (
            "inspection_readiness",
            "requires_inspection_readiness",
            "inspection-readiness-result.json",
            "inspection-readiness-validate",
            {"DRAFT_TAXPAYER_READINESS_ONLY", "DRAFT_FOR_AUTHORIZED_INSPECTOR"},
        ),
        (
            "ymm_certification",
            "requires_ymm_certification",
            "ymm-certification-result.json",
            "ymm-certification-validate",
            {"DRAFT_READINESS_ONLY", "DRAFT_FOR_LICENSED_YMM"},
        ),
    )
    for gate_name, requirement_field, file_name, operation_name, allowed_output_statuses in professional_gate_specs:
        required = bool(case.get(requirement_field, False))
        result_path = case_dir / "outputs" / file_name
        passed = False
        decision = None
        receipt_valid = False
        output_status = None
        if result_path.is_file():
            professional_result = read_json(result_path)
            if isinstance(professional_result, dict):
                decision = professional_result.get("decision")
                receipt_valid = _valid_receipt(professional_result)
                professional_engine = professional_result.get("engine", {})
                result_body = professional_result.get("result", {})
                if isinstance(result_body, dict):
                    output_status = result_body.get("output_status")
                passed = (
                    isinstance(professional_engine, dict)
                    and professional_engine.get("name") == "muhasebecim-professional-roles"
                    and professional_result.get("operation") == operation_name
                    and decision in {"PASS", "PASS_WITH_WARNINGS"}
                    and receipt_valid
                    and isinstance(result_body, dict)
                    and result_body.get("professional_act_permitted") is False
                    and output_status in allowed_output_statuses
                )
        gates.append(gate(
            gate_name,
            (not required) or passed,
            {
                "required": required,
                "path": str(result_path),
                "operation": operation_name,
                "decision": decision,
                "output_status": output_status,
                "allowed_output_statuses": sorted(allowed_output_statuses),
                "receipt_valid": receipt_valid,
                "passed": passed,
            },
        ))

    reconciliation_required = bool(case.get("requires_tax_reconciliation", False))
    reconciliation_path = case_dir / "outputs" / "tax-reconciliation-result.json"
    reconciliation_ok = False
    if reconciliation_path.is_file():
        reconciliation = read_json(reconciliation_path)
        reconciliation_ok = isinstance(reconciliation, dict) and bool(reconciliation.get("result", reconciliation))
    gates.append(gate("tax_reconciliation", (not reconciliation_required) or reconciliation_ok, {"required": reconciliation_required, "path": str(reconciliation_path), "present": reconciliation_ok}))

    open_items = facts.get("open_items", [])
    unresolved_items = [item for item in open_items if isinstance(item, dict) and item.get("affects_conclusion") and item.get("status") != "resolved"] if isinstance(open_items, list) else ["open_items must be a list"]
    gates.append(gate("conclusion_affecting_open_items", not unresolved_items, unresolved_items))

    passed = all(item["passed"] for item in gates)
    return {
        "schema_version": 1,
        "case_id": case.get("case_id"),
        "case_dir": str(case_dir),
        "ready_for_professional_review": passed,
        "gates": gates,
        "professional_review": "required before filing, signing, certification, or external submission",
    }


def finalize_case(case_dir: Path) -> dict[str, Any]:
    result = check_case(case_dir)
    if not result["ready_for_professional_review"]:
        return {**result, "finalized": False}
    case_path = case_dir.resolve() / "case.json"
    case = read_json(case_path)
    now = datetime.now(timezone.utc).isoformat()
    case["status"] = "ready_for_professional_review"
    case["updated_at"] = now
    write_json(case_path, case)
    write_json(case_dir.resolve() / "outputs" / "completion-check.json", result)
    return {**result, "finalized": True, "status": case["status"]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    init_parser = sub.add_parser("init")
    init_parser.add_argument("--case", required=True, type=Path)
    init_parser.add_argument("--case-id", required=True)
    init_parser.add_argument("--as-of", required=True)
    for command in ("check", "finalize"):
        command_parser = sub.add_parser(command)
        command_parser.add_argument("--case", required=True, type=Path)
    args = parser.parse_args()
    try:
        if args.command == "init":
            result = init_case(args.case, args.case_id, args.as_of)
        elif args.command == "check":
            result = check_case(args.case)
        else:
            result = finalize_case(args.case)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        if args.command in {"check", "finalize"} and not result["ready_for_professional_review"]:
            return 2
        return 0
    except (WorkflowError, OSError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

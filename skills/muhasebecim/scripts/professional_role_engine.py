#!/usr/bin/env python3
"""Deterministic tax-inspection readiness and YMM certification gate engine.

Exit codes:
  0: PASS or PASS_WITH_WARNINGS
  1: valid input, but one or more business rules BLOCK the result
  2: schema, catalog, or system error
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any


ENGINE_NAME = "muhasebecim-professional-roles"
ENGINE_VERSION = "0.0.3"
DEFAULT_CATALOG = Path(__file__).with_name("data") / "professional_roles.v1.json"
EXPECTED_CATALOG_SHA256 = "c7f09a3f3564dd22e384420b0af3c528096fd65ea6d4860eb5f053985194d066"
OPERATIONS = {"inspection-readiness-validate", "ymm-certification-validate"}
SEVERITY_ORDER = {"BLOCK": 0, "WARN": 1, "INFO": 2}
INSPECTION_MODES = {"taxpayer_readiness", "authorized_inspector_support"}
EXAMINATION_TYPES = {"readiness_unknown", "full", "limited", "vat_refund"}
YMM_MODES = {"pre_certification_readiness", "licensed_ymm_support"}
YMM_SERVICE_TYPES = {
    "full_certification", "vat_refund", "exemption", "refund", "deduction",
    "deferment_or_cancellation", "loss_offset", "special_purpose", "other",
}

INSPECTION_ENGAGEMENT_FIELDS = {
    "mode", "taxpayer_reference", "examination_type", "authority_evidence",
    "assignment_reference", "start_notice_present", "start_notice_reference",
    "periods", "tax_types", "current_law_verified", "secrecy_controls_confirmed",
    "data_location",
}
YMM_ENGAGEMENT_FIELDS = {
    "mode", "taxpayer_reference", "service_type", "legal_basis_reference",
    "licensed_ymm_confirmed", "license_evidence", "working_list_confirmed",
    "seal_available", "written_contract_present", "certification_relationship_stated",
    "independence_confirmed", "prohibited_relationship_absent",
    "bookkeeping_separation_confirmed", "scope_document_present",
    "current_communique_verified", "variable_thresholds_as_inputs", "periods",
    "tax_types", "data_location",
}
INSPECTION_WORK_FIELDS = {
    "purpose_and_scope_defined", "risk_hypotheses_documented",
    "books_records_declarations_reconciled", "document_request_scope_tracked",
    "evidence_chain_documented", "taxpayer_rights_reviewed",
    "procedural_deadlines_calculated", "sampling_method_documented",
    "findings_structure_complete", "taxpayer_explanations_recorded",
    "potential_crime_escalation_protocol", "report_review_gate", "professional_review",
}
YMM_WORK_FIELDS = {
    "client_and_engagement_understood", "materiality_documented", "audit_plan_documented",
    "books_and_documents_examined", "financial_statements_reconciled", "declarations_reconciled",
    "sufficient_reliable_evidence", "sampling_documented",
    "counter_examinations_completed_or_explained", "findings_resolved_or_qualified",
    "report_scope_explicit", "report_form_current", "management_responses_documented",
    "responsibility_acknowledged", "professional_review",
}
EXPECTED_RULE_IDS = {
    "inspection-readiness-validate": {
        "VI-YETKI-001", "VI-GOREV-001", "VI-BASLAMA-001", "VI-BASLAMA-002",
        "VI-GUNCEL-001", "VI-GIZLILIK-001", "VI-YEREL-001", "VI-AMAC-001",
        "VI-RISK-001", "VI-MUTABAKAT-001", "VI-IBRAZ-001", "VI-KANIT-001",
        "VI-HAK-001", "VI-SURE-001", "VI-ORNEKLEM-001", "VI-BULGU-001",
        "VI-ACIKLAMA-001", "VI-359-001", "VI-RDK-001", "VI-INCELEME-001",
    },
    "ymm-certification-validate": {
        "YMM-RUHSAT-001", "YMM-RUHSAT-002", "YMM-LISTE-001", "YMM-MUHUR-001",
        "YMM-SOZLESME-001", "YMM-SOZLESME-002", "YMM-BAGIMSIZLIK-001",
        "YMM-ILISKI-001", "YMM-DEFTER-001", "YMM-KAPSAM-001", "YMM-GUNCEL-001",
        "YMM-DEGISKEN-001", "YMM-YEREL-001", "YMM-TANIMA-001", "YMM-ONEMLILIK-001",
        "YMM-PLAN-001", "YMM-KAYIT-001", "YMM-MUTABAKAT-001", "YMM-BEYAN-001",
        "YMM-KANIT-001", "YMM-ORNEKLEM-001", "YMM-KARSIT-001", "YMM-BULGU-001",
        "YMM-RAPOR-001", "YMM-RAPOR-002", "YMM-TEMSIL-001", "YMM-SORUMLULUK-001",
        "YMM-INCELEME-001",
    },
}


class InputError(ValueError):
    """Raised for closed-schema or type errors."""


class CatalogError(ValueError):
    """Raised when the installed rule catalog is invalid."""


class JsonArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise InputError(message)


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_value(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def require_object(value: Any, location: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise InputError(f"{location} must be an object")
    return value


def require_list(value: Any, location: str) -> list[Any]:
    if not isinstance(value, list):
        raise InputError(f"{location} must be an array")
    return value


def enforce_fields(
    value: dict[str, Any], location: str, allowed: set[str], required: set[str] | None = None,
) -> None:
    unknown = sorted(set(value) - allowed)
    if unknown:
        raise InputError(f"{location} contains unknown fields: {', '.join(unknown)}")
    missing = sorted((required or set()) - set(value))
    if missing:
        raise InputError(f"{location} is missing required fields: {', '.join(missing)}")


def parse_iso_date(value: Any, location: str) -> date:
    if not isinstance(value, str):
        raise InputError(f"{location} must be an ISO date string")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise InputError(f"{location} must be YYYY-MM-DD") from exc


def parse_bool(value: Any, location: str) -> bool:
    if not isinstance(value, bool):
        raise InputError(f"{location} must be boolean")
    return value


def parse_string(value: Any, location: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise InputError(f"{location} must be a non-empty string")
    return value.strip()


def parse_nullable_string(value: Any, location: str) -> str | None:
    if value is None:
        return None
    return parse_string(value, location)


def parse_periods(value: Any, location: str) -> list[dict[str, str]]:
    rows = require_list(value, location)
    if not rows:
        raise InputError(f"{location} must contain at least one period")
    normalized: list[dict[str, str]] = []
    for index, raw in enumerate(rows):
        row_location = f"{location}[{index}]"
        row = require_object(raw, row_location)
        enforce_fields(row, row_location, {"start", "end"}, {"start", "end"})
        start = parse_iso_date(row["start"], f"{row_location}.start")
        end = parse_iso_date(row["end"], f"{row_location}.end")
        if start > end:
            raise InputError(f"{row_location}.start must not be after end")
        normalized.append({"start": start.isoformat(), "end": end.isoformat()})
    return sorted(normalized, key=lambda item: (item["start"], item["end"]))


def parse_tax_types(value: Any, location: str) -> list[str]:
    rows = require_list(value, location)
    if not rows:
        raise InputError(f"{location} must contain at least one tax type")
    normalized = [parse_string(item, f"{location}[{index}]") for index, item in enumerate(rows)]
    if len(set(normalized)) != len(normalized):
        raise InputError(f"{location} must not contain duplicates")
    return sorted(normalized)


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise InputError(f"missing JSON file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise InputError(f"invalid JSON in {path}: {exc}") from exc


def load_catalog(path: Path) -> tuple[dict[str, Any], str]:
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise CatalogError(f"cannot read catalog {path}: {exc}") from exc
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CatalogError(f"invalid UTF-8 JSON catalog {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise CatalogError("catalog root must be an object")
    return value, sha256_value(value)


def finding(
    rule_id: str, severity: str, location: str, message: str,
    source_refs: list[str], **evidence: Any,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "rule_id": rule_id,
        "severity": severity,
        "location": location,
        "message": message,
        "source_refs": sorted(set(source_refs)),
    }
    if evidence:
        result["evidence"] = evidence
    return result


def sort_findings(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        items,
        key=lambda item: (
            SEVERITY_ORDER[item["severity"]], item["rule_id"], item["location"],
            item["message"], canonical_json(item.get("evidence", {})),
        ),
    )


def validate_catalog(catalog: dict[str, Any], catalog_sha256: str | None = None) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    required = {"schema_version", "catalog_version", "verified_through", "framework", "operations", "sources", "rules"}
    unknown = sorted(set(catalog) - required)
    missing = sorted(required - set(catalog))
    if catalog.get("schema_version") != 1:
        findings.append(finding("CAT-SCHEMA-001", "BLOCK", "schema_version", "Catalog schema_version must equal 1.", []))
    if catalog_sha256 is not None and catalog_sha256 != EXPECTED_CATALOG_SHA256:
        findings.append(finding(
            "CAT-HASH-001", "BLOCK", "catalog.sha256",
            "Installed catalog hash does not match the engine's pinned release catalog.", [],
            actual=catalog_sha256, expected=EXPECTED_CATALOG_SHA256,
        ))
    if unknown or missing:
        findings.append(finding("CAT-SCHEMA-002", "BLOCK", "catalog", "Catalog top-level fields do not match the closed schema.", [], unknown=unknown, missing=missing))
    try:
        parse_iso_date(catalog.get("verified_through"), "verified_through")
    except InputError as exc:
        findings.append(finding("CAT-DATE-001", "BLOCK", "verified_through", str(exc), []))

    operations = catalog.get("operations")
    if not isinstance(operations, list) or set(operations) != OPERATIONS or len(operations) != len(OPERATIONS):
        findings.append(finding("CAT-OPERATION-001", "BLOCK", "operations", "Catalog operations must contain each supported operation exactly once.", [], actual=operations))

    source_ids: set[str] = set()
    sources = catalog.get("sources")
    if not isinstance(sources, list) or not sources:
        findings.append(finding("CAT-SOURCE-001", "BLOCK", "sources", "Catalog must contain sources.", []))
        sources = []
    source_fields = {"id", "title", "authority", "url", "pinpoint", "status"}
    for index, raw in enumerate(sources):
        location = f"sources[{index}]"
        if not isinstance(raw, dict) or set(raw) != source_fields or not all(isinstance(raw.get(key), str) and raw[key] for key in source_fields):
            findings.append(finding("CAT-SOURCE-002", "BLOCK", location, "Source must contain the six required non-empty string fields.", []))
            continue
        if raw["id"] in source_ids:
            findings.append(finding("CAT-SOURCE-003", "BLOCK", location, "Source id must be unique.", [], source_id=raw["id"]))
        source_ids.add(raw["id"])

    rule_root = catalog.get("rules")
    if not isinstance(rule_root, dict) or set(rule_root) != OPERATIONS:
        findings.append(finding("CAT-RULE-001", "BLOCK", "rules", "Rule groups must match supported operations.", []))
        rule_root = {}
    rule_ids: set[str] = set()
    rule_fields = {"rule_id", "field_path", "test", "expected", "condition", "severity", "message", "source_refs"}
    rule_count = 0
    for operation in sorted(OPERATIONS):
        rows = rule_root.get(operation, []) if isinstance(rule_root, dict) else []
        if not isinstance(rows, list) or not rows:
            findings.append(finding("CAT-RULE-002", "BLOCK", f"rules.{operation}", "Operation must contain rules.", []))
            continue
        operation_rule_ids: set[str] = set()
        engagement_fields = INSPECTION_ENGAGEMENT_FIELDS if operation == "inspection-readiness-validate" else YMM_ENGAGEMENT_FIELDS
        work_fields = INSPECTION_WORK_FIELDS if operation == "inspection-readiness-validate" else YMM_WORK_FIELDS
        allowed_paths = {f"engagement.{field}" for field in engagement_fields} | {f"work_program.{field}" for field in work_fields}
        for index, raw in enumerate(rows):
            rule_count += 1
            location = f"rules.{operation}[{index}]"
            if not isinstance(raw, dict) or set(raw) != rule_fields:
                findings.append(finding("CAT-RULE-003", "BLOCK", location, "Rule fields do not match the closed schema.", []))
                continue
            rule_id = raw.get("rule_id")
            if not isinstance(rule_id, str) or not rule_id:
                findings.append(finding("CAT-RULE-004", "BLOCK", location, "Rule id must be a non-empty string.", []))
            elif rule_id in rule_ids:
                findings.append(finding("CAT-RULE-005", "BLOCK", location, "Rule id must be unique.", [], rule_id=rule_id))
            else:
                rule_ids.add(rule_id)
                operation_rule_ids.add(rule_id)
            if raw.get("test") not in {"equals", "non_empty"} or raw.get("severity") not in SEVERITY_ORDER:
                findings.append(finding("CAT-RULE-006", "BLOCK", location, "Rule test or severity is unsupported.", []))
            if not isinstance(raw.get("field_path"), str) or raw["field_path"] not in allowed_paths:
                findings.append(finding("CAT-RULE-007", "BLOCK", location, "Rule field_path is invalid.", []))
            condition = raw.get("condition")
            if condition is not None and (
                not isinstance(condition, dict) or set(condition) != {"field_path", "equals"}
                or not isinstance(condition.get("field_path"), str)
            ):
                findings.append(finding("CAT-RULE-008", "BLOCK", location, "Rule condition is invalid.", []))
            refs = raw.get("source_refs")
            if not isinstance(refs, list) or not refs or not all(isinstance(ref, str) for ref in refs):
                findings.append(finding("CAT-RULE-009", "BLOCK", location, "Rule must cite at least one source.", []))
            else:
                missing_refs = sorted(set(refs) - source_ids)
                if missing_refs:
                    findings.append(finding("CAT-RULE-010", "BLOCK", location, "Rule cites unknown sources.", [], missing_refs=missing_refs))
        if operation_rule_ids != EXPECTED_RULE_IDS[operation]:
            findings.append(finding(
                "CAT-RULE-011", "BLOCK", f"rules.{operation}",
                "Installed rule ids must exactly match the engine's fail-closed baseline.", [],
                missing_rule_ids=sorted(EXPECTED_RULE_IDS[operation] - operation_rule_ids),
                unexpected_rule_ids=sorted(operation_rule_ids - EXPECTED_RULE_IDS[operation]),
            ))
    return findings, {"source_count": len(sources), "rule_count": rule_count, "operation_count": len(OPERATIONS)}


def _get_path(root: dict[str, Any], field_path: str) -> Any:
    current: Any = root
    for part in field_path.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def _required_work_fields(catalog: dict[str, Any], operation: str) -> set[str]:
    del catalog
    return INSPECTION_WORK_FIELDS if operation == "inspection-readiness-validate" else YMM_WORK_FIELDS


def validate_input(data: Any, operation: str, catalog: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    root = require_object(data, "input")
    enforce_fields(root, "input", {"schema_version", "as_of_date", "engagement", "work_program"}, {"schema_version", "as_of_date", "engagement", "work_program"})
    if root["schema_version"] != 1:
        raise InputError("input.schema_version must equal 1")
    as_of = parse_iso_date(root["as_of_date"], "as_of_date")
    engagement = require_object(root["engagement"], "engagement")
    work_program = require_object(root["work_program"], "work_program")
    work_fields = _required_work_fields(catalog, operation)
    enforce_fields(work_program, "work_program", work_fields, work_fields)
    for field in sorted(work_fields):
        parse_bool(work_program[field], f"work_program.{field}")

    if operation == "inspection-readiness-validate":
        enforce_fields(engagement, "engagement", INSPECTION_ENGAGEMENT_FIELDS, INSPECTION_ENGAGEMENT_FIELDS)
        mode = parse_string(engagement["mode"], "engagement.mode")
        if mode not in INSPECTION_MODES:
            raise InputError(f"engagement.mode must be one of {sorted(INSPECTION_MODES)}")
        examination_type = parse_string(engagement["examination_type"], "engagement.examination_type")
        if examination_type not in EXAMINATION_TYPES:
            raise InputError(f"engagement.examination_type must be one of {sorted(EXAMINATION_TYPES)}")
        parse_string(engagement["taxpayer_reference"], "engagement.taxpayer_reference")
        parse_nullable_string(engagement["authority_evidence"], "engagement.authority_evidence")
        parse_nullable_string(engagement["assignment_reference"], "engagement.assignment_reference")
        parse_bool(engagement["start_notice_present"], "engagement.start_notice_present")
        parse_nullable_string(engagement["start_notice_reference"], "engagement.start_notice_reference")
        parse_bool(engagement["current_law_verified"], "engagement.current_law_verified")
        parse_bool(engagement["secrecy_controls_confirmed"], "engagement.secrecy_controls_confirmed")
    else:
        enforce_fields(engagement, "engagement", YMM_ENGAGEMENT_FIELDS, YMM_ENGAGEMENT_FIELDS)
        mode = parse_string(engagement["mode"], "engagement.mode")
        if mode not in YMM_MODES:
            raise InputError(f"engagement.mode must be one of {sorted(YMM_MODES)}")
        service_type = parse_string(engagement["service_type"], "engagement.service_type")
        if service_type not in YMM_SERVICE_TYPES:
            raise InputError(f"engagement.service_type must be one of {sorted(YMM_SERVICE_TYPES)}")
        parse_string(engagement["taxpayer_reference"], "engagement.taxpayer_reference")
        parse_string(engagement["legal_basis_reference"], "engagement.legal_basis_reference")
        parse_nullable_string(engagement["license_evidence"], "engagement.license_evidence")
        for field in sorted(YMM_ENGAGEMENT_FIELDS - {"mode", "taxpayer_reference", "service_type", "legal_basis_reference", "license_evidence", "periods", "tax_types", "data_location"}):
            parse_bool(engagement[field], f"engagement.{field}")

    periods = parse_periods(engagement["periods"], "engagement.periods")
    tax_types = parse_tax_types(engagement["tax_types"], "engagement.tax_types")
    data_location = parse_string(engagement["data_location"], "engagement.data_location")
    if data_location not in {"local", "external"}:
        raise InputError("engagement.data_location must be local or external")
    return root, {
        "as_of_date": as_of.isoformat(), "mode": mode, "periods": periods,
        "tax_types": tax_types, "data_location": data_location,
    }


def evaluate_rules(root: dict[str, Any], operation: str, catalog: dict[str, Any]) -> tuple[list[dict[str, Any]], list[str]]:
    findings: list[dict[str, Any]] = []
    evaluated: list[str] = []
    for rule in catalog["rules"][operation]:
        condition = rule["condition"]
        if condition is not None and _get_path(root, condition["field_path"]) != condition["equals"]:
            continue
        evaluated.append(rule["rule_id"])
        actual = _get_path(root, rule["field_path"])
        if rule["test"] == "equals":
            passed = actual == rule["expected"]
        else:
            passed = isinstance(actual, str) and bool(actual.strip())
        if not passed:
            findings.append(finding(
                rule["rule_id"], rule["severity"], rule["field_path"], rule["message"],
                rule["source_refs"], actual=actual, expected=rule["expected"] if rule["test"] == "equals" else "non_empty",
            ))
    return findings, evaluated


def decision_for(findings: list[dict[str, Any]]) -> str:
    if any(item["severity"] == "BLOCK" for item in findings):
        return "BLOCK"
    if any(item["severity"] == "WARN" for item in findings):
        return "PASS_WITH_WARNINGS"
    return "PASS"


def envelope(
    operation: str, input_data: Any, catalog: dict[str, Any], catalog_sha256: str,
    findings: list[dict[str, Any]], result: dict[str, Any], evaluated_rule_ids: list[str],
) -> dict[str, Any]:
    ordered = sort_findings(findings)
    output: dict[str, Any] = {
        "schema_version": 1,
        "engine": {"name": ENGINE_NAME, "version": ENGINE_VERSION},
        "operation": operation,
        "catalog": {
            "version": catalog.get("catalog_version"),
            "verified_through": catalog.get("verified_through"),
            "sha256": catalog_sha256,
            "framework": catalog.get("framework"),
        },
        "input_sha256": sha256_value(input_data),
        "decision": decision_for(ordered),
        "summary": {
            "block_count": sum(item["severity"] == "BLOCK" for item in ordered),
            "warning_count": sum(item["severity"] == "WARN" for item in ordered),
            "info_count": sum(item["severity"] == "INFO" for item in ordered),
            "finding_count": len(ordered),
        },
        "evaluated_rule_ids": sorted(set(evaluated_rule_ids)),
        "findings": ordered,
        "result": result,
    }
    output["receipt_sha256"] = sha256_value(output)
    return output


def run_catalog_audit(catalog: dict[str, Any], catalog_sha256: str) -> dict[str, Any]:
    findings, summary = validate_catalog(catalog, catalog_sha256)
    input_data = {"catalog_sha256": catalog_sha256}
    evaluated = [
        "CAT-SCHEMA-001", "CAT-SCHEMA-002", "CAT-HASH-001", "CAT-DATE-001", "CAT-OPERATION-001",
        "CAT-SOURCE-001", "CAT-SOURCE-002", "CAT-SOURCE-003", "CAT-RULE-001",
        "CAT-RULE-002", "CAT-RULE-003", "CAT-RULE-004", "CAT-RULE-005",
        "CAT-RULE-006", "CAT-RULE-007", "CAT-RULE-008", "CAT-RULE-009", "CAT-RULE-010",
        "CAT-RULE-011",
    ]
    return envelope("catalog-audit", input_data, catalog, catalog_sha256, findings, summary, evaluated)


def run_validate(data: Any, operation: str, catalog: dict[str, Any], catalog_sha256: str) -> dict[str, Any]:
    catalog_findings, _ = validate_catalog(catalog, catalog_sha256)
    if catalog_findings:
        raise CatalogError("installed professional role catalog failed audit")
    root, normalized = validate_input(data, operation, catalog)
    findings, evaluated = evaluate_rules(root, operation, catalog)
    if operation == "inspection-readiness-validate":
        output_status = "DRAFT_FOR_AUTHORIZED_INSPECTOR" if normalized["mode"] == "authorized_inspector_support" else "DRAFT_TAXPAYER_READINESS_ONLY"
        limitations = [
            "The engine does not exercise public authority or issue an official tax inspection report.",
            "A VUK 359 indicator is an escalation flag, not a finding of criminal liability.",
            "Current primary law prevails over an older processed regulation text where they conflict.",
        ]
    else:
        output_status = "DRAFT_FOR_LICENSED_YMM" if normalized["mode"] == "licensed_ymm_support" else "DRAFT_READINESS_ONLY"
        limitations = [
            "The engine cannot sign, seal, certify, file, or assume a YMM's statutory responsibility.",
            "PASS means only that the defined workfile gates passed; it is not a certification opinion.",
            "Service-specific communiques, thresholds, forms, and deadlines must be verified for the engagement date.",
        ]
    result = {
        **normalized,
        "output_status": output_status,
        "professional_act_permitted": False,
        "applicable_rule_count": len(evaluated),
        "completed_control_count": len(evaluated) - len(findings),
        "limitations": limitations,
    }
    return envelope(operation, root, catalog, catalog_sha256, findings, result, evaluated)


def examples(operation: str) -> dict[str, Any]:
    if operation == "inspection-readiness-validate":
        return {
            "schema_version": 1,
            "as_of_date": "2026-08-02",
            "engagement": {
                "mode": "taxpayer_readiness",
                "taxpayer_reference": "MASKED-VKN",
                "examination_type": "readiness_unknown",
                "authority_evidence": None,
                "assignment_reference": None,
                "start_notice_present": False,
                "start_notice_reference": None,
                "periods": [{"start": "2025-01-01", "end": "2025-12-31"}],
                "tax_types": ["corporate_income_tax", "vat"],
                "current_law_verified": True,
                "secrecy_controls_confirmed": True,
                "data_location": "local",
            },
            "work_program": {
                "purpose_and_scope_defined": True,
                "risk_hypotheses_documented": True,
                "books_records_declarations_reconciled": True,
                "document_request_scope_tracked": True,
                "evidence_chain_documented": True,
                "taxpayer_rights_reviewed": True,
                "procedural_deadlines_calculated": True,
                "sampling_method_documented": True,
                "findings_structure_complete": True,
                "taxpayer_explanations_recorded": True,
                "potential_crime_escalation_protocol": True,
                "report_review_gate": True,
                "professional_review": True,
            },
        }
    if operation == "ymm-certification-validate":
        return {
            "schema_version": 1,
            "as_of_date": "2026-08-02",
            "engagement": {
                "mode": "pre_certification_readiness",
                "taxpayer_reference": "MASKED-VKN",
                "service_type": "full_certification",
                "legal_basis_reference": "3568/12 ve işlem tarihinde doğrulanan tasdik tebliği",
                "licensed_ymm_confirmed": False,
                "license_evidence": None,
                "working_list_confirmed": False,
                "seal_available": False,
                "written_contract_present": True,
                "certification_relationship_stated": True,
                "independence_confirmed": True,
                "prohibited_relationship_absent": True,
                "bookkeeping_separation_confirmed": True,
                "scope_document_present": True,
                "current_communique_verified": True,
                "variable_thresholds_as_inputs": True,
                "periods": [{"start": "2025-01-01", "end": "2025-12-31"}],
                "tax_types": ["corporate_income_tax"],
                "data_location": "local",
            },
            "work_program": {
                "client_and_engagement_understood": True,
                "materiality_documented": True,
                "audit_plan_documented": True,
                "books_and_documents_examined": True,
                "financial_statements_reconciled": True,
                "declarations_reconciled": True,
                "sufficient_reliable_evidence": True,
                "sampling_documented": True,
                "counter_examinations_completed_or_explained": True,
                "findings_resolved_or_qualified": True,
                "report_scope_explicit": True,
                "report_form_current": True,
                "management_responses_documented": True,
                "responsibility_acknowledged": True,
                "professional_review": True,
            },
        }
    raise InputError(f"no example for operation: {operation}")


def error_envelope(operation: str | None, message: str) -> dict[str, Any]:
    value: dict[str, Any] = {
        "schema_version": 1,
        "engine": {"name": ENGINE_NAME, "version": ENGINE_VERSION},
        "operation": operation,
        "decision": "ERROR",
        "error": {"type": "INPUT_OR_SYSTEM_ERROR", "message": message},
    }
    value["receipt_sha256"] = sha256_value(value)
    return value


def write_output(value: dict[str, Any], path: Path | None) -> None:
    rendered = json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(rendered.encode("utf-8"))
    sys.stdout.buffer.write(rendered.encode("utf-8"))


def build_parser() -> argparse.ArgumentParser:
    parser = JsonArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    subparsers = parser.add_subparsers(dest="operation", required=True)
    audit = subparsers.add_parser("catalog-audit")
    audit.add_argument("--output", type=Path)
    for operation in sorted(OPERATIONS):
        command = subparsers.add_parser(operation)
        group = command.add_mutually_exclusive_group(required=True)
        group.add_argument("--input", type=Path)
        group.add_argument("--example", action="store_true")
        command.add_argument("--output", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args: argparse.Namespace | None = None
    operation: str | None = None
    try:
        args = parser.parse_args(argv)
        operation = args.operation
        catalog, catalog_sha256 = load_catalog(args.catalog)
        if operation == "catalog-audit":
            output = run_catalog_audit(catalog, catalog_sha256)
        else:
            data = examples(operation) if args.example else read_json(args.input)
            if args.example:
                write_output(data, args.output)
                return 0
            output = run_validate(data, operation, catalog, catalog_sha256)
        write_output(output, args.output)
        return 1 if output["decision"] == "BLOCK" else 0
    except (InputError, CatalogError, OSError) as exc:
        output_path = getattr(args, "output", None)
        write_output(error_envelope(operation, str(exc)), output_path)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

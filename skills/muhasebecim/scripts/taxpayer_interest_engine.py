#!/usr/bin/env python3
"""Deterministic taxpayer-interest and internal-alert gate.

The engine does not hide, falsify, destroy, or externally transmit adverse facts.
It requires a lawful taxpayer-protective action and a local, acknowledged internal
alert for every adverse matter before a case can move to professional review.

Exit codes:
  0: PASS or PASS_WITH_WARNINGS
  1: valid input, but one or more business rules BLOCK the result
  2: schema, catalog, or system error
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any


ENGINE_NAME = "muhasebecim-taxpayer-interest"
ENGINE_VERSION = "0.0.3"
DEFAULT_CATALOG = Path(__file__).with_name("data") / "taxpayer_interest_rules.v1.json"
EXPECTED_CATALOG_SHA256 = "86028df4be151358de890738d03b8b4c7777065bb7050dc9500dd632333e5f95"
OPERATION = "taxpayer-interest-validate"
OPERATIONS = {OPERATION}
SEVERITY_ORDER = {"BLOCK": 0, "WARN": 1, "INFO": 2}
IDENTIFIER = re.compile(r"^[A-Z0-9][A-Z0-9_-]{0,63}$")

ROLE_MODES = {
    "accountant_advisory",
    "taxpayer_readiness",
    "authorized_inspector_support",
    "pre_certification_readiness",
    "licensed_ymm_support",
}
ACTION_TYPES = {
    "right_assertion", "evidence_completion", "voluntary_correction", "reconciliation",
    "explanation", "objection", "settlement", "appeal", "payment_or_installment", "other",
}
ALERT_RECIPIENTS = {"user", "smmm", "ymm"}
MATTER_SEVERITIES = {"low", "medium", "high", "critical"}
EXPECTED_RULE_IDS = {
    "ML-LEH-001", "ML-LEH-002", "ML-LEH-003", "ML-SURE-001", "ML-SURE-002",
    "ML-ALEYH-001", "ML-ALICI-001", "ML-ACK-001", "ML-KORUMA-001", "ML-DIS-001",
    "ML-YEREL-001", "ML-GIZLEME-001", "ML-HUKUK-001", "ML-BAGIMSIZLIK-001",
    "ML-INCELEME-001", "ML-OZELLIK-001",
}

ROOT_FIELDS = {
    "schema_version", "as_of_date", "case_reference", "role_mode",
    "favorable_actions", "adverse_matters", "controls",
}
ACTION_FIELDS = {
    "action_id", "action_type", "summary", "legal_basis_reference", "evidence_references",
    "action_reference", "action_sha256", "deadline_applicable", "deadline", "prepared",
}
MATTER_FIELDS = {
    "matter_id", "severity", "summary", "factual_basis_references", "legal_basis_reference",
    "estimated_impact_reference", "protective_action_id", "internal_alert",
}
ALERT_FIELDS = {
    "prepared", "alert_reference", "alert_sha256", "recipients", "acknowledged",
    "acknowledged_by", "acknowledged_at", "external_transmission",
}
CONTROL_FIELDS = {
    "local_processing_confirmed", "adverse_facts_suppressed", "lawful_only",
    "independence_and_impartiality_preserved", "human_review_required",
    "internal_alerts_private",
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


def enforce_fields(value: dict[str, Any], location: str, allowed: set[str]) -> None:
    unknown = sorted(set(value) - allowed)
    missing = sorted(allowed - set(value))
    if unknown:
        raise InputError(f"{location} contains unknown fields: {', '.join(unknown)}")
    if missing:
        raise InputError(f"{location} is missing required fields: {', '.join(missing)}")


def parse_string(value: Any, location: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise InputError(f"{location} must be a non-empty string")
    return value.strip()


def parse_nullable_string(value: Any, location: str) -> str | None:
    if value is None:
        return None
    return parse_string(value, location)


def parse_bool(value: Any, location: str) -> bool:
    if not isinstance(value, bool):
        raise InputError(f"{location} must be boolean")
    return value


def parse_date(value: Any, location: str) -> date:
    if not isinstance(value, str):
        raise InputError(f"{location} must be an ISO date string")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise InputError(f"{location} must be YYYY-MM-DD") from exc


def parse_nullable_date(value: Any, location: str) -> date | None:
    if value is None:
        return None
    return parse_date(value, location)


def parse_enum(value: Any, location: str, allowed: set[str]) -> str:
    parsed = parse_string(value, location)
    if parsed not in allowed:
        raise InputError(f"{location} must be one of: {', '.join(sorted(allowed))}")
    return parsed


def parse_strings(value: Any, location: str, *, allow_empty: bool) -> list[str]:
    rows = require_list(value, location)
    parsed = [parse_string(item, f"{location}[{index}]") for index, item in enumerate(rows)]
    if not allow_empty and not parsed:
        raise InputError(f"{location} must contain at least one item")
    if len(parsed) != len(set(parsed)):
        raise InputError(f"{location} must not contain duplicates")
    return sorted(parsed)


def parse_identifier(value: Any, location: str) -> str:
    parsed = parse_string(value, location)
    if not IDENTIFIER.fullmatch(parsed):
        raise InputError(f"{location} must use uppercase letters, digits, underscore, or hyphen")
    return parsed


def parse_sha256(value: Any, location: str) -> str:
    parsed = parse_string(value, location).lower()
    if not re.fullmatch(r"[0-9a-f]{64}", parsed):
        raise InputError(f"{location} must be a lowercase 64-character SHA-256 hex digest")
    return parsed


def parse_nullable_sha256(value: Any, location: str) -> str | None:
    if value is None:
        return None
    return parse_sha256(value, location)


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise InputError(f"missing JSON file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise InputError(f"invalid JSON in {path}: {exc}") from exc


def load_catalog(path: Path) -> tuple[dict[str, Any], str]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CatalogError(f"cannot load UTF-8 JSON catalog {path}: {exc}") from exc
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


def sort_findings(findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        findings,
        key=lambda item: (
            SEVERITY_ORDER.get(item["severity"], 99), item["rule_id"], item["location"],
            canonical_json(item.get("evidence", {})),
        ),
    )


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


def _audit_finding(rule_id: str, message: str, **evidence: Any) -> dict[str, Any]:
    return finding(rule_id, "BLOCK", "catalog", message, [], **evidence)


def validate_catalog(catalog: dict[str, Any], catalog_sha256: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    expected_fields = {
        "schema_version", "catalog_version", "verified_through", "framework", "operations",
        "role_modes", "action_types", "alert_recipients", "sources", "rules",
    }
    unknown = sorted(set(catalog) - expected_fields)
    missing = sorted(expected_fields - set(catalog))
    if unknown or missing:
        findings.append(_audit_finding("CAT-SCHEMA-001", "Catalog root fields are not exact.", unknown=unknown, missing=missing))
    if catalog.get("schema_version") != 1:
        findings.append(_audit_finding("CAT-SCHEMA-002", "Catalog schema_version must equal 1."))
    if catalog_sha256 != EXPECTED_CATALOG_SHA256:
        findings.append(_audit_finding("CAT-HASH-001", "Catalog canonical SHA-256 differs from the pinned release hash.", actual=catalog_sha256, expected=EXPECTED_CATALOG_SHA256))
    try:
        parse_date(catalog.get("verified_through"), "catalog.verified_through")
    except InputError as exc:
        findings.append(_audit_finding("CAT-DATE-001", str(exc)))
    if catalog.get("operations") != [OPERATION]:
        findings.append(_audit_finding("CAT-OPERATION-001", "Catalog operations are not the closed release set."))
    for field_name, expected in (
        ("role_modes", ROLE_MODES), ("action_types", ACTION_TYPES), ("alert_recipients", ALERT_RECIPIENTS),
    ):
        value = catalog.get(field_name)
        if not isinstance(value, list) or set(value) != expected or len(value) != len(expected):
            findings.append(_audit_finding("CAT-ENUM-001", f"catalog.{field_name} differs from the closed release set."))

    source_ids: set[str] = set()
    sources = catalog.get("sources")
    if not isinstance(sources, list) or not sources:
        findings.append(_audit_finding("CAT-SOURCE-001", "Catalog must contain sources."))
        sources = []
    source_fields = {"id", "title", "authority", "url", "pinpoint", "status"}
    for index, raw in enumerate(sources):
        if not isinstance(raw, dict) or set(raw) != source_fields:
            findings.append(_audit_finding("CAT-SOURCE-002", "Source fields are not exact.", index=index))
            continue
        if any(not isinstance(raw[field], str) or not raw[field].strip() for field in source_fields):
            findings.append(_audit_finding("CAT-SOURCE-002", "Source values must be non-empty strings.", index=index))
        source_id = raw.get("id")
        if source_id in source_ids:
            findings.append(_audit_finding("CAT-SOURCE-003", "Source id is duplicated.", source_id=source_id))
        if isinstance(source_id, str):
            source_ids.add(source_id)

    rules = catalog.get("rules")
    if not isinstance(rules, list):
        findings.append(_audit_finding("CAT-RULE-001", "Catalog rules must be an array."))
        rules = []
    rule_ids: set[str] = set()
    for index, raw in enumerate(rules):
        if not isinstance(raw, dict) or set(raw) != {"rule_id", "severity", "source_refs"}:
            findings.append(_audit_finding("CAT-RULE-002", "Rule fields are not exact.", index=index))
            continue
        rule_id = raw.get("rule_id")
        if rule_id in rule_ids:
            findings.append(_audit_finding("CAT-RULE-003", "Rule id is duplicated.", rule_id=rule_id))
        if isinstance(rule_id, str):
            rule_ids.add(rule_id)
        if raw.get("severity") not in SEVERITY_ORDER:
            findings.append(_audit_finding("CAT-RULE-004", "Rule severity is invalid.", rule_id=rule_id))
        refs = raw.get("source_refs")
        if not isinstance(refs, list) or not refs or any(ref not in source_ids for ref in refs):
            findings.append(_audit_finding("CAT-RULE-005", "Rule source reference is missing or unknown.", rule_id=rule_id))
    if rule_ids != EXPECTED_RULE_IDS:
        findings.append(_audit_finding("CAT-RULE-006", "Catalog rule ids differ from the closed release set.", missing=sorted(EXPECTED_RULE_IDS - rule_ids), unexpected=sorted(rule_ids - EXPECTED_RULE_IDS)))

    return findings, {
        "catalog_sha256": catalog_sha256,
        "operation_count": len(catalog.get("operations", [])) if isinstance(catalog.get("operations"), list) else 0,
        "rule_count": len(rules),
        "source_count": len(sources),
    }


def rule_sources(catalog: dict[str, Any]) -> dict[str, list[str]]:
    return {row["rule_id"]: row["source_refs"] for row in catalog["rules"]}


def validate_input(value: Any, catalog: dict[str, Any]) -> dict[str, Any]:
    root = require_object(value, "input")
    enforce_fields(root, "input", ROOT_FIELDS)
    if root["schema_version"] != 1 or isinstance(root["schema_version"], bool):
        raise InputError("input.schema_version must equal integer 1")
    as_of = parse_date(root["as_of_date"], "input.as_of_date")
    case_reference = parse_string(root["case_reference"], "input.case_reference")
    role_mode = parse_enum(root["role_mode"], "input.role_mode", ROLE_MODES)

    actions: list[dict[str, Any]] = []
    action_ids: set[str] = set()
    for index, raw in enumerate(require_list(root["favorable_actions"], "input.favorable_actions")):
        location = f"input.favorable_actions[{index}]"
        row = require_object(raw, location)
        enforce_fields(row, location, ACTION_FIELDS)
        action_id = parse_identifier(row["action_id"], f"{location}.action_id")
        if action_id in action_ids:
            raise InputError(f"{location}.action_id is duplicated")
        action_ids.add(action_id)
        deadline = parse_nullable_date(row["deadline"], f"{location}.deadline")
        actions.append({
            "action_id": action_id,
            "action_type": parse_enum(row["action_type"], f"{location}.action_type", ACTION_TYPES),
            "summary": parse_string(row["summary"], f"{location}.summary"),
            "legal_basis_reference": parse_string(row["legal_basis_reference"], f"{location}.legal_basis_reference"),
            "evidence_references": parse_strings(row["evidence_references"], f"{location}.evidence_references", allow_empty=False),
            "action_reference": parse_string(row["action_reference"], f"{location}.action_reference"),
            "action_sha256": parse_sha256(row["action_sha256"], f"{location}.action_sha256"),
            "deadline_applicable": parse_bool(row["deadline_applicable"], f"{location}.deadline_applicable"),
            "deadline": deadline.isoformat() if deadline else None,
            "prepared": parse_bool(row["prepared"], f"{location}.prepared"),
        })

    matters: list[dict[str, Any]] = []
    matter_ids: set[str] = set()
    for index, raw in enumerate(require_list(root["adverse_matters"], "input.adverse_matters")):
        location = f"input.adverse_matters[{index}]"
        row = require_object(raw, location)
        enforce_fields(row, location, MATTER_FIELDS)
        matter_id = parse_identifier(row["matter_id"], f"{location}.matter_id")
        if matter_id in matter_ids:
            raise InputError(f"{location}.matter_id is duplicated")
        matter_ids.add(matter_id)
        alert = require_object(row["internal_alert"], f"{location}.internal_alert")
        enforce_fields(alert, f"{location}.internal_alert", ALERT_FIELDS)
        recipients = parse_strings(alert["recipients"], f"{location}.internal_alert.recipients", allow_empty=True)
        invalid_recipients = sorted(set(recipients) - ALERT_RECIPIENTS)
        if invalid_recipients:
            raise InputError(f"{location}.internal_alert.recipients contains invalid values: {', '.join(invalid_recipients)}")
        acknowledged_at = parse_nullable_date(alert["acknowledged_at"], f"{location}.internal_alert.acknowledged_at")
        matters.append({
            "matter_id": matter_id,
            "severity": parse_enum(row["severity"], f"{location}.severity", MATTER_SEVERITIES),
            "summary": parse_string(row["summary"], f"{location}.summary"),
            "factual_basis_references": parse_strings(row["factual_basis_references"], f"{location}.factual_basis_references", allow_empty=False),
            "legal_basis_reference": parse_string(row["legal_basis_reference"], f"{location}.legal_basis_reference"),
            "estimated_impact_reference": parse_nullable_string(row["estimated_impact_reference"], f"{location}.estimated_impact_reference"),
            "protective_action_id": parse_identifier(row["protective_action_id"], f"{location}.protective_action_id"),
            "internal_alert": {
                "prepared": parse_bool(alert["prepared"], f"{location}.internal_alert.prepared"),
                "alert_reference": parse_nullable_string(alert["alert_reference"], f"{location}.internal_alert.alert_reference"),
                "alert_sha256": parse_nullable_sha256(alert["alert_sha256"], f"{location}.internal_alert.alert_sha256"),
                "recipients": recipients,
                "acknowledged": parse_bool(alert["acknowledged"], f"{location}.internal_alert.acknowledged"),
                "acknowledged_by": parse_nullable_string(alert["acknowledged_by"], f"{location}.internal_alert.acknowledged_by"),
                "acknowledged_at": acknowledged_at.isoformat() if acknowledged_at else None,
                "external_transmission": parse_bool(alert["external_transmission"], f"{location}.internal_alert.external_transmission"),
            },
        })

    controls = require_object(root["controls"], "input.controls")
    enforce_fields(controls, "input.controls", CONTROL_FIELDS)
    normalized_controls = {field: parse_bool(controls[field], f"input.controls.{field}") for field in sorted(CONTROL_FIELDS)}
    return {
        "schema_version": 1,
        "as_of_date": as_of.isoformat(),
        "case_reference": case_reference,
        "role_mode": role_mode,
        "favorable_actions": sorted(actions, key=lambda item: item["action_id"]),
        "adverse_matters": sorted(matters, key=lambda item: item["matter_id"]),
        "controls": normalized_controls,
    }


def evaluate_rules(root: dict[str, Any], catalog: dict[str, Any]) -> tuple[list[dict[str, Any]], list[str], list[str]]:
    refs = rule_sources(catalog)
    findings: list[dict[str, Any]] = []
    evaluated = sorted(EXPECTED_RULE_IDS)
    as_of = date.fromisoformat(root["as_of_date"])
    actions = root["favorable_actions"]
    if not actions:
        findings.append(finding("ML-LEH-001", "BLOCK", "favorable_actions", "Her vakada en az bir hukuka uygun mükellef lehine adım hazırlanmalıdır.", refs["ML-LEH-001"]))

    active_action_ids: list[str] = []
    for index, action in enumerate(actions):
        location = f"favorable_actions[{index}]"
        if not action["prepared"]:
            findings.append(finding("ML-LEH-002", "BLOCK", location, "Mükellef lehine adım yalnız taslak fikir olarak bırakılamaz; hazırlanmış olmalıdır.", refs["ML-LEH-002"], action_id=action["action_id"]))
        deadline = date.fromisoformat(action["deadline"]) if action["deadline"] else None
        if action["deadline_applicable"] and deadline is None:
            findings.append(finding("ML-SURE-001", "BLOCK", f"{location}.deadline", "Süreye bağlı lehe adımın son günü Python ile hesaplanıp kaydedilmelidir.", refs["ML-SURE-001"], action_id=action["action_id"]))
        expired = deadline is not None and deadline < as_of
        if expired:
            findings.append(finding("ML-SURE-002", "WARN", f"{location}.deadline", "Lehe adımın kayıtlı süresi as-of tarihinde geçmiştir; alternatif güncel adım gerekir.", refs["ML-SURE-002"], action_id=action["action_id"], deadline=deadline.isoformat(), as_of_date=as_of.isoformat()))
        if action["prepared"] and (not action["deadline_applicable"] or (deadline is not None and not expired)):
            active_action_ids.append(action["action_id"])
    if not active_action_ids:
        findings.append(finding("ML-LEH-003", "BLOCK", "favorable_actions", "Vakada as-of tarihinde uygulanabilir hazırlanmış bir mükellef koruma adımı yoktur.", refs["ML-LEH-003"]))

    for index, matter in enumerate(root["adverse_matters"]):
        location = f"adverse_matters[{index}]"
        alert = matter["internal_alert"]
        if not alert["prepared"] or alert["alert_reference"] is None or alert["alert_sha256"] is None:
            findings.append(finding("ML-ALEYH-001", "BLOCK", f"{location}.internal_alert", "Aleyhe husus için yerel iç bildirim hazırlanmalı ve dosya referansı verilmelidir.", refs["ML-ALEYH-001"], matter_id=matter["matter_id"]))
        if not alert["recipients"]:
            findings.append(finding("ML-ALICI-001", "BLOCK", f"{location}.internal_alert.recipients", "İç bildirimin alıcısı kullanıcı, SMMM veya YMM olmalıdır.", refs["ML-ALICI-001"], matter_id=matter["matter_id"]))
        acknowledged_at = date.fromisoformat(alert["acknowledged_at"]) if alert["acknowledged_at"] else None
        if (
            not alert["acknowledged"]
            or alert["acknowledged_by"] is None
            or acknowledged_at is None
            or acknowledged_at > as_of
        ):
            findings.append(finding("ML-ACK-001", "BLOCK", f"{location}.internal_alert", "Aleyhe husus kullanıcı veya meslek mensubu tarafından görüldü kaydıyla kabul edilmeden vaka kapanamaz.", refs["ML-ACK-001"], matter_id=matter["matter_id"]))
        if matter["protective_action_id"] not in active_action_ids:
            findings.append(finding("ML-KORUMA-001", "BLOCK", f"{location}.protective_action_id", "Her aleyhe husus uygulanabilir bir düzeltme, açıklama, itiraz veya başka koruma adımına bağlanmalıdır.", refs["ML-KORUMA-001"], matter_id=matter["matter_id"], protective_action_id=matter["protective_action_id"]))
        if alert["external_transmission"]:
            findings.append(finding("ML-DIS-001", "BLOCK", f"{location}.internal_alert.external_transmission", "İç istihbarat kaydı otomatik dış iletime açılamaz.", refs["ML-DIS-001"], matter_id=matter["matter_id"]))

    controls = root["controls"]
    control_rules = (
        ("local_processing_confirmed", True, "ML-YEREL-001", "Mükellef verisi ve iç bildirim yerelde işlenmelidir."),
        ("adverse_facts_suppressed", False, "ML-GIZLEME-001", "Aleyhe olgu, delil veya mevzuat iç analizden gizlenemez, küçültülemez ya da yok edilemez."),
        ("lawful_only", True, "ML-HUKUK-001", "Mükellef lehine adımlar yalnız hukuka uygun seçeneklerden hazırlanabilir."),
        ("independence_and_impartiality_preserved", True, "ML-BAGIMSIZLIK-001", "Vergi müfettişi ve YMM destek modlarında tarafsızlık, bağımsızlık ve doğru raporlama korunmalıdır."),
        ("human_review_required", True, "ML-INCELEME-001", "Dış gönderim, beyan, imza, tasdik veya resmî işlemden önce insan incelemesi zorunludur."),
        ("internal_alerts_private", True, "ML-OZELLIK-001", "İç bildirimler yalnız yetkili kullanıcı ve meslek mensuplarına özel tutulmalıdır."),
    )
    for field, expected, rule_id, message in control_rules:
        if controls[field] is not expected:
            findings.append(finding(rule_id, "BLOCK", f"controls.{field}", message, refs[rule_id], actual=controls[field], expected=expected))
    return findings, evaluated, sorted(active_action_ids)


def run_catalog_audit(catalog: dict[str, Any], catalog_sha256: str) -> dict[str, Any]:
    findings, summary = validate_catalog(catalog, catalog_sha256)
    evaluated = [
        "CAT-SCHEMA-001", "CAT-SCHEMA-002", "CAT-HASH-001", "CAT-DATE-001",
        "CAT-OPERATION-001", "CAT-ENUM-001", "CAT-SOURCE-001", "CAT-SOURCE-002",
        "CAT-SOURCE-003", "CAT-RULE-001", "CAT-RULE-002", "CAT-RULE-003",
        "CAT-RULE-004", "CAT-RULE-005", "CAT-RULE-006",
    ]
    return envelope("catalog-audit", {"catalog_sha256": catalog_sha256}, catalog, catalog_sha256, findings, summary, evaluated)


def run_validate(value: Any, catalog: dict[str, Any], catalog_sha256: str) -> dict[str, Any]:
    catalog_findings, _ = validate_catalog(catalog, catalog_sha256)
    if catalog_findings:
        raise CatalogError("installed taxpayer-interest catalog failed audit")
    root = validate_input(value, catalog)
    findings, evaluated, active_action_ids = evaluate_rules(root, catalog)
    adverse = root["adverse_matters"]
    alerts_acknowledged = all(
        row["internal_alert"]["prepared"]
        and row["internal_alert"]["acknowledged"]
        and row["internal_alert"]["acknowledged_by"] is not None
        and row["internal_alert"]["acknowledged_at"] is not None
        for row in adverse
    )
    result = {
        "case_reference": root["case_reference"],
        "role_mode": root["role_mode"],
        "output_status": "INTERNAL_TAXPAYER_PROTECTION_RECORD",
        "taxpayer_favorable_path_status": "PREPARED" if active_action_ids else "NOT_PREPARED",
        "active_favorable_action_ids": active_action_ids,
        "active_favorable_action_records": [
            {
                "action_id": row["action_id"],
                "reference": row["action_reference"],
                "sha256": row["action_sha256"],
            }
            for row in root["favorable_actions"] if row["action_id"] in active_action_ids
        ],
        "adverse_matter_ids": [row["matter_id"] for row in adverse],
        "internal_intelligence_status": "CLEAR" if not adverse else ("ACKNOWLEDGED" if alerts_acknowledged else "PENDING_ACKNOWLEDGEMENT"),
        "internal_alert_references": sorted(
            row["internal_alert"]["alert_reference"] for row in adverse
            if row["internal_alert"]["alert_reference"] is not None
        ),
        "internal_alert_records": [
            {
                "matter_id": row["matter_id"],
                "reference": row["internal_alert"]["alert_reference"],
                "sha256": row["internal_alert"]["alert_sha256"],
            }
            for row in adverse
        ],
        "external_transmission_permitted": False,
        "professional_act_permitted": False,
        "limitations": [
            "The record is internal decision material; it cannot file, sign, certify, or make an official determination.",
            "Taxpayer-protective means lawful rights, evidence, correction, explanation, objection, settlement, appeal, or payment planning; it never means concealment or falsification.",
            "Authorized inspector and licensed YMM support remain subject to statutory impartiality, independence, complete evidence, and truthful reporting.",
        ],
    }
    return envelope(OPERATION, root, catalog, catalog_sha256, findings, result, evaluated)


def example() -> dict[str, Any]:
    return {
        "schema_version": 1,
        "as_of_date": "2026-08-02",
        "case_reference": "MASKED-CASE",
        "role_mode": "accountant_advisory",
        "favorable_actions": [
            {
                "action_id": "ACTION-001",
                "action_type": "evidence_completion",
                "summary": "Eksik dayanak belgelerini tamamla ve mükellef açıklamasını çalışma kâğıdına bağla.",
                "legal_basis_reference": "Vaka tarihinde doğrulanan VUK ve ikincil mevzuat",
                "evidence_references": ["workpapers/evidence-matrix.json"],
                "action_reference": "workpapers/taxpayer-actions/ACTION-001.json",
                "action_sha256": "56231906acd4aa580be557a3812414ebe16b9e297c3775a98ef7a4eed9debfb1",
                "deadline_applicable": False,
                "deadline": None,
                "prepared": True,
            }
        ],
        "adverse_matters": [],
        "controls": {
            "local_processing_confirmed": True,
            "adverse_facts_suppressed": False,
            "lawful_only": True,
            "independence_and_impartiality_preserved": True,
            "human_review_required": True,
            "internal_alerts_private": True,
        },
    }


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
    validate = subparsers.add_parser(OPERATION)
    group = validate.add_mutually_exclusive_group(required=True)
    group.add_argument("--input", type=Path)
    group.add_argument("--example", action="store_true")
    validate.add_argument("--output", type=Path)
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
        elif args.example:
            write_output(example(), args.output)
            return 0
        else:
            output = run_validate(read_json(args.input), catalog, catalog_sha256)
        write_output(output, args.output)
        return 1 if output["decision"] == "BLOCK" else 0
    except (InputError, CatalogError, OSError) as exc:
        output_path = getattr(args, "output", None)
        write_output(error_envelope(operation, str(exc)), output_path)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

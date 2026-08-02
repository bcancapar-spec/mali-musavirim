#!/usr/bin/env python3
"""Deterministic MSUGT Tekdüzen Hesap Planı and VUK recording-rule engine.

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
import unicodedata
from collections import defaultdict
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Iterable


ENGINE_NAME = "muhasebecim-thp-vuk"
ENGINE_VERSION = "0.0.3"
DEFAULT_CATALOG = Path(__file__).with_name("data") / "thp_accounts.v1.json"
MONEY_RE = re.compile(r"^(?:0|[1-9]\d*)(?:\.\d+)?$")
ACCOUNT_RE = re.compile(r"^(\d{3})(?:[.\-/ ]([0-9A-Za-zÇĞİÖŞÜçğıöşü]+(?:[.\-/ ][0-9A-Za-zÇĞİÖŞÜçğıöşü]+)*))?$")
SEVERITY_ORDER = {"BLOCK": 0, "WARN": 1, "INFO": 2}
NORMAL_BALANCES = {"debit", "credit", "mixed"}
ALLOWED_COST_METHODS = {"7A", "7B", "none"}


class InputError(ValueError):
    """Raised for closed-schema or type errors (exit 2)."""


class CatalogError(ValueError):
    """Raised when the installed catalog cannot be interpreted (exit 2)."""


class JsonArgumentParser(argparse.ArgumentParser):
    """Convert command-line usage failures to the engine's JSON error contract."""

    def error(self, message: str) -> None:
        raise InputError(message)


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_value(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def decimal_text(value: Decimal) -> str:
    if value == 0:
        return "0"
    rendered = format(value, "f")
    if "." in rendered:
        rendered = rendered.rstrip("0").rstrip(".")
    return rendered


def require_object(value: Any, location: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise InputError(f"{location} must be an object")
    return value


def require_list(value: Any, location: str) -> list[Any]:
    if not isinstance(value, list):
        raise InputError(f"{location} must be an array")
    return value


def enforce_fields(
    value: dict[str, Any],
    location: str,
    allowed: set[str],
    required: set[str] | None = None,
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


def parse_money(value: Any, location: str) -> Decimal:
    if not isinstance(value, str):
        raise InputError(f"{location} must be a non-negative decimal string")
    if not MONEY_RE.fullmatch(value):
        raise InputError(f"{location} must use digits and an optional dot decimal separator")
    try:
        amount = Decimal(value)
    except InvalidOperation as exc:
        raise InputError(f"{location} is not a valid decimal") from exc
    if not amount.is_finite() or amount < 0:
        raise InputError(f"{location} must be finite and non-negative")
    return amount


def parse_bool(value: Any, location: str) -> bool:
    if not isinstance(value, bool):
        raise InputError(f"{location} must be boolean")
    return value


def normalize_name(value: str) -> str:
    translate = str.maketrans({"I": "ı", "İ": "i", "Ç": "ç", "Ğ": "ğ", "Ö": "ö", "Ş": "ş", "Ü": "ü"})
    normalized = unicodedata.normalize("NFKC", value).translate(translate).lower()
    normalized = re.sub(r"\(\s*-\s*\)", " ", normalized)
    normalized = re.sub(r"[^0-9a-zçğıöşü]+", " ", normalized)
    return " ".join(normalized.split())


def normalize_account_code(value: Any, location: str) -> tuple[str, str]:
    if not isinstance(value, str):
        raise InputError(f"{location} must be a string so leading zeroes cannot be lost")
    raw = value.strip()
    match = ACCOUNT_RE.fullmatch(raw)
    if not match:
        raise InputError(f"{location} must be a 3-digit code with optional delimited subaccounts")
    root = match.group(1)
    suffix = match.group(2)
    if suffix:
        segments = [part for part in re.split(r"[.\-/ ]+", suffix) if part]
        return root, ".".join([root, *segments])
    return root, root


def finding(
    rule_id: str,
    severity: str,
    location: str,
    message: str,
    source_refs: Iterable[str],
    **evidence: Any,
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
            SEVERITY_ORDER[item["severity"]],
            item["rule_id"],
            item["location"],
            item["message"],
            canonical_json(item.get("evidence", {})),
        ),
    )


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
    return value, hashlib.sha256(raw).hexdigest()


def catalog_index(catalog: dict[str, Any]) -> dict[str, dict[str, Any]]:
    row_schema = catalog.get("account_row_schema")
    if row_schema != ["code", "name", "normal_balance", "source_ref"]:
        raise CatalogError("unsupported account_row_schema")
    result: dict[str, dict[str, Any]] = {}
    rows = catalog.get("accounts")
    if not isinstance(rows, list):
        raise CatalogError("catalog accounts must be an array")
    for index, row in enumerate(rows):
        if not isinstance(row, list) or len(row) != 4 or not all(isinstance(item, str) for item in row):
            raise CatalogError(f"catalog accounts[{index}] must have four string fields")
        code, name, normal_balance, source_ref = row
        if code in result:
            raise CatalogError(f"duplicate catalog account: {code}")
        result[code] = {
            "code": code,
            "name": name,
            "normal_balance": normal_balance,
            "source_ref": source_ref,
            "custom": False,
        }
    return result


def validate_catalog(catalog: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    required = {
        "schema_version", "catalog_version", "verified_through", "framework", "sources",
        "sector_values", "classes", "groups", "account_row_schema", "accounts",
        "account_ranges", "aliases",
    }
    missing = sorted(required - set(catalog))
    if missing:
        findings.append(finding("CAT-SCHEMA-001", "BLOCK", "catalog", "Required catalog fields are missing.", [], missing=missing))
        return sort_findings(findings), {"account_count": 0, "range_count": 0, "source_count": 0}

    sources = catalog.get("sources") if isinstance(catalog.get("sources"), dict) else {}
    classes = catalog.get("classes") if isinstance(catalog.get("classes"), dict) else {}
    groups = catalog.get("groups") if isinstance(catalog.get("groups"), dict) else {}
    seen: set[str] = set()
    accounts = catalog.get("accounts") if isinstance(catalog.get("accounts"), list) else []
    schema_ok = catalog.get("account_row_schema") == ["code", "name", "normal_balance", "source_ref"]
    if not schema_ok:
        findings.append(finding("CAT-SCHEMA-002", "BLOCK", "account_row_schema", "Unsupported account row schema.", []))
    else:
        for index, row in enumerate(accounts):
            location = f"accounts[{index}]"
            if not isinstance(row, list) or len(row) != 4 or not all(isinstance(item, str) for item in row):
                findings.append(finding("CAT-ROW-001", "BLOCK", location, "Account row must contain four strings.", []))
                continue
            code, name, normal_balance, source_ref = row
            if not re.fullmatch(r"\d{3}", code):
                findings.append(finding("CAT-CODE-001", "BLOCK", location, "Account root must contain exactly three digits.", [], code=code))
            if code in seen:
                findings.append(finding("CAT-CODE-002", "BLOCK", location, "Account root is duplicated.", [], code=code))
            seen.add(code)
            if not name.strip():
                findings.append(finding("CAT-NAME-001", "BLOCK", location, "Account name must not be blank.", [], code=code))
            if normal_balance not in NORMAL_BALANCES:
                findings.append(finding("CAT-BALANCE-001", "BLOCK", location, "Unknown normal balance value.", [], value=normal_balance))
            if source_ref not in sources:
                findings.append(finding("CAT-SOURCE-001", "BLOCK", location, "Source reference is not defined.", [], source_ref=source_ref))
            if len(code) == 3 and code[:1] not in classes:
                findings.append(finding("CAT-CLASS-001", "BLOCK", location, "Account class is not defined.", [], code=code))
            if len(code) == 3 and code[:2] not in groups and code[0] not in {"8", "9"}:
                findings.append(finding("CAT-GROUP-001", "BLOCK", location, "Account group is not defined.", [], code=code))

    ranges = catalog.get("account_ranges") if isinstance(catalog.get("account_ranges"), list) else []
    for index, item in enumerate(ranges):
        location = f"account_ranges[{index}]"
        if not isinstance(item, dict):
            findings.append(finding("CAT-RANGE-001", "BLOCK", location, "Range must be an object.", []))
            continue
        required_range = {"start", "end", "canonical_code", "name", "normal_balance", "source_ref"}
        if set(item) != required_range:
            findings.append(finding("CAT-RANGE-002", "BLOCK", location, "Range fields do not match the closed schema.", [], fields=sorted(item)))
            continue
        if not all(isinstance(item[key], str) for key in required_range):
            findings.append(finding("CAT-RANGE-003", "BLOCK", location, "Range values must be strings.", []))
            continue
        if not (item["start"].isdigit() and item["end"].isdigit() and int(item["start"]) <= int(item["end"])):
            findings.append(finding("CAT-RANGE-004", "BLOCK", location, "Range boundaries are invalid.", []))
        if item["source_ref"] not in sources:
            findings.append(finding("CAT-SOURCE-001", "BLOCK", location, "Range source reference is not defined.", [], source_ref=item["source_ref"]))

    summary = {
        "account_count": len(accounts),
        "range_count": len(ranges),
        "source_count": len(sources),
        "class_count": len(classes),
        "group_count": len(groups),
    }
    return sort_findings(findings), summary


def find_account(root: str, catalog: dict[str, Any], index: dict[str, dict[str, Any]]) -> dict[str, Any] | None:
    if root in index:
        return index[root]
    for item in catalog.get("account_ranges", []):
        if int(item["start"]) <= int(root) <= int(item["end"]):
            return {
                "code": root,
                "canonical_code": item["canonical_code"],
                "name": item["name"],
                "normal_balance": item["normal_balance"],
                "source_ref": item["source_ref"],
                "custom": False,
                "range_member": True,
            }
    return None


def source_effective_date(account: dict[str, Any], catalog: dict[str, Any]) -> date | None:
    source = catalog.get("sources", {}).get(account["source_ref"], {})
    value = source.get("effective_from") if isinstance(source, dict) else None
    return date.fromisoformat(value) if isinstance(value, str) else None


def validate_entity(value: Any, catalog: dict[str, Any], operation: str) -> dict[str, Any]:
    entity = require_object(value, "entity")
    base_allowed = {"sector", "chart", "cost_method"}
    journal_allowed = base_allowed | {"ledger_currency", "language", "foreign_currency_permission", "permission_source"}
    allowed = journal_allowed if operation == "journal-validate" else base_allowed
    required = base_allowed | ({"ledger_currency", "language"} if operation == "journal-validate" else set())
    enforce_fields(entity, "entity", allowed, required)
    if entity["sector"] not in catalog.get("sector_values", []):
        raise InputError("entity.sector is not in the catalog's closed sector enum")
    if entity["chart"] != catalog.get("framework"):
        raise InputError(f"entity.chart must equal {catalog.get('framework')}")
    if entity["cost_method"] not in ALLOWED_COST_METHODS:
        raise InputError("entity.cost_method must be 7A, 7B, or none")
    if operation == "journal-validate":
        if not isinstance(entity["ledger_currency"], str) or not re.fullmatch(r"[A-Z]{3}", entity["ledger_currency"]):
            raise InputError("entity.ledger_currency must be a three-letter uppercase currency code")
        if entity["language"] not in {"tr", "other"}:
            raise InputError("entity.language must be tr or other")
        permission = entity.get("foreign_currency_permission", False)
        if not isinstance(permission, bool):
            raise InputError("entity.foreign_currency_permission must be boolean")
        if "permission_source" in entity and not isinstance(entity["permission_source"], str):
            raise InputError("entity.permission_source must be a string")
    return entity


def validate_options(value: Any, operation: str) -> dict[str, bool]:
    defaults: dict[str, bool] = {
        "allow_custom_8_9": True,
        "strict_normal_balance": False,
    }
    if operation == "journal-validate":
        defaults.update({"require_contiguous_line_numbers": True, "require_descriptions": True})
    if value is None:
        return defaults
    options = require_object(value, "options")
    enforce_fields(options, "options", set(defaults))
    for key, item in options.items():
        defaults[key] = parse_bool(item, f"options.{key}")
    return defaults


def account_rule_findings(
    code_value: Any,
    name_value: Any,
    location: str,
    as_of_date: date,
    entity: dict[str, Any],
    options: dict[str, bool],
    catalog: dict[str, Any],
    index: dict[str, dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any] | None, str]:
    root, normalized_code = normalize_account_code(code_value, f"{location}.account_code")
    if not isinstance(name_value, str):
        raise InputError(f"{location}.account_name must be a string")
    findings: list[dict[str, Any]] = []
    account = find_account(root, catalog, index)

    if entity["sector"] != "general":
        findings.append(finding(
            "THP-SCOPE-001", "BLOCK", location,
            "General MSUGT account plan cannot be applied automatically to this regulated sector.",
            ["GIB-SCOPE"], sector=entity["sector"], chart=entity["chart"],
        ))

    if account is None and root[0] in {"8", "9"}:
        if options["allow_custom_8_9"]:
            if not name_value.strip():
                findings.append(finding("THP-CUSTOM-002", "BLOCK", location, "Custom class 8/9 account requires a non-blank name.", ["MSUGT-1"], code=root))
            account = {
                "code": root,
                "name": name_value.strip(),
                "normal_balance": "mixed",
                "source_ref": "MSUGT-1",
                "custom": True,
            }
        else:
            findings.append(finding("THP-CUSTOM-001", "BLOCK", location, "Custom class 8/9 accounts are disabled by policy.", ["MSUGT-1"], code=root))
    elif account is None:
        findings.append(finding("THP-CODE-001", "BLOCK", location, "Account root is not present in the versioned THP catalog.", ["MSUGT-1"], code=root))

    if account is not None:
        source_metadata = catalog.get("sources", {}).get(account["source_ref"], {})
        if isinstance(source_metadata, dict) and str(source_metadata.get("role", "")).startswith("secondary"):
            findings.append(finding(
                "THP-SOURCE-001", "WARN", location,
                "Account is cataloged from a secondary professional cross-check; trace the primary amendment before external reliance.",
                [account["source_ref"]], code=root, source_role=source_metadata.get("role"),
            ))
        if not account.get("custom"):
            expected_names = [account["name"], *catalog.get("aliases", {}).get(account.get("canonical_code", root), [])]
            actual_normalized = normalize_name(name_value)
            expected_normalized = {normalize_name(item) for item in expected_names}
            range_member = bool(account.get("range_member")) and root != account.get("canonical_code")
            name_matches = bool(actual_normalized) if range_member else actual_normalized in expected_normalized
            if not name_matches:
                findings.append(finding(
                    "THP-NAME-001", "BLOCK", location,
                    "Account name does not match the catalog entry.",
                    [account["source_ref"], "ISMMMO-CROSSCHECK"],
                    code=root, supplied=name_value, expected=expected_names, range_member=range_member,
                ))
        effective = source_effective_date(account, catalog)
        if effective is not None and as_of_date < effective:
            findings.append(finding(
                "THP-EFFECTIVE-001", "BLOCK", location,
                "Account was not yet effective on the analysis date.",
                [account["source_ref"]], code=root, effective_from=effective.isoformat(), as_of_date=as_of_date.isoformat(),
            ))

        cost_method = entity["cost_method"]
        if root.startswith("7"):
            if root[:2] in {"70", "71", "72", "73", "74", "75", "76", "77", "78"} and cost_method != "7A":
                findings.append(finding("THP-COST-001", "BLOCK", location, "This class 7 account requires the 7/A cost option.", ["MSUGT-1"], code=root, cost_method=cost_method))
            if root[:2] == "79" and cost_method != "7B":
                findings.append(finding("THP-COST-002", "BLOCK", location, "This class 7 account requires the 7/B cost option.", ["MSUGT-1"], code=root, cost_method=cost_method))

    return findings, account, normalized_code


def base_input(
    data: Any,
    operation: str,
    catalog: dict[str, Any],
    allowed_root: set[str],
    collection_name: str,
) -> tuple[dict[str, Any], date, dict[str, Any], dict[str, bool], list[Any]]:
    root = require_object(data, "input")
    enforce_fields(root, "input", allowed_root, {"as_of_date", "entity", collection_name})
    if "schema_version" in root and root["schema_version"] != 1:
        raise InputError("input.schema_version must equal 1")
    as_of = parse_iso_date(root["as_of_date"], "as_of_date")
    entity = validate_entity(root["entity"], catalog, operation)
    options = validate_options(root.get("options"), operation)
    collection = require_list(root[collection_name], collection_name)
    if not collection:
        raise InputError(f"{collection_name} must contain at least one item")
    return root, as_of, entity, options, collection


def decision_for(findings: list[dict[str, Any]]) -> str:
    if any(item["severity"] == "BLOCK" for item in findings):
        return "BLOCK"
    if any(item["severity"] == "WARN" for item in findings):
        return "PASS_WITH_WARNINGS"
    return "PASS"


def envelope(
    operation: str,
    input_data: Any,
    catalog: dict[str, Any],
    catalog_sha256: str,
    findings: list[dict[str, Any]],
    result: dict[str, Any],
) -> dict[str, Any]:
    ordered = sort_findings(findings)
    decision = decision_for(ordered)
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
        "decision": decision,
        "summary": {
            "block_count": sum(item["severity"] == "BLOCK" for item in ordered),
            "warning_count": sum(item["severity"] == "WARN" for item in ordered),
            "info_count": sum(item["severity"] == "INFO" for item in ordered),
            "finding_count": len(ordered),
        },
        "evaluated_rule_ids": sorted({item["rule_id"] for item in ordered} | set(result.pop("_evaluated_rule_ids", []))),
        "findings": ordered,
        "result": result,
    }
    output["receipt_sha256"] = sha256_value(output)
    return output


def run_catalog_audit(catalog: dict[str, Any], catalog_sha256: str) -> dict[str, Any]:
    findings, summary = validate_catalog(catalog)
    input_data = {"catalog_sha256": catalog_sha256}
    result = {**summary, "_evaluated_rule_ids": [
        "CAT-SCHEMA-001", "CAT-SCHEMA-002", "CAT-ROW-001", "CAT-CODE-001", "CAT-CODE-002",
        "CAT-NAME-001", "CAT-BALANCE-001", "CAT-SOURCE-001", "CAT-CLASS-001", "CAT-GROUP-001",
        "CAT-RANGE-001", "CAT-RANGE-002", "CAT-RANGE-003", "CAT-RANGE-004",
    ]}
    return envelope("catalog-audit", input_data, catalog, catalog_sha256, findings, result)


def run_account_validate(data: Any, catalog: dict[str, Any], catalog_sha256: str) -> dict[str, Any]:
    root, as_of, entity, options, rows = base_input(
        data, "account-validate", catalog,
        {"schema_version", "as_of_date", "entity", "accounts", "options"}, "accounts",
    )
    index = catalog_index(catalog)
    findings: list[dict[str, Any]] = []
    normalized: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row_index, value in enumerate(rows):
        location = f"accounts[{row_index}]"
        row = require_object(value, location)
        enforce_fields(row, location, {"account_code", "account_name"}, {"account_code", "account_name"})
        row_findings, account, normalized_code = account_rule_findings(
            row["account_code"], row["account_name"], location, as_of, entity, options, catalog, index,
        )
        findings.extend(row_findings)
        if normalized_code in seen:
            findings.append(finding("THP-DUPLICATE-001", "BLOCK", location, "Account code is duplicated in the input.", ["MSUGT-1"], account_code=normalized_code))
        seen.add(normalized_code)
        normalized.append({
            "account_code": normalized_code,
            "root_code": normalized_code[:3],
            "account_name": row["account_name"],
            "catalog_name": account.get("name") if account else None,
            "normal_balance": account.get("normal_balance") if account else None,
            "custom": bool(account and account.get("custom")),
        })
    result = {
        "account_count": len(rows),
        "normalized_accounts": sorted(normalized, key=lambda item: item["account_code"]),
        "_evaluated_rule_ids": [
            "THP-SCOPE-001", "THP-CODE-001", "THP-NAME-001", "THP-EFFECTIVE-001",
            "THP-CUSTOM-001", "THP-CUSTOM-002", "THP-COST-001", "THP-COST-002", "THP-SOURCE-001",
            "THP-DUPLICATE-001",
        ],
    }
    return envelope("account-validate", root, catalog, catalog_sha256, findings, result)


JOURNAL_FIELDS = {
    "journal_no", "line_no", "transaction_date", "ledger_date", "voucher_date", "recording_basis",
    "account_code", "account_name", "description", "debit", "credit", "counterparty_relation",
    "document_type", "document_no", "document_currency", "try_equivalent_present", "foreign_customer",
    "turkish_record_present", "correction_of", "correction_method",
}
JOURNAL_REQUIRED = {
    "journal_no", "line_no", "transaction_date", "ledger_date", "recording_basis", "account_code",
    "account_name", "description", "debit", "credit", "counterparty_relation",
}


def run_journal_validate(data: Any, catalog: dict[str, Any], catalog_sha256: str) -> dict[str, Any]:
    root, as_of, entity, options, rows = base_input(
        data, "journal-validate", catalog,
        {"schema_version", "as_of_date", "entity", "entries", "options"}, "entries",
    )
    index = catalog_index(catalog)
    findings: list[dict[str, Any]] = []
    normalized: list[dict[str, Any]] = []
    journals: dict[str, dict[str, Any]] = defaultdict(lambda: {"debit": Decimal("0"), "credit": Decimal("0"), "line_nos": []})
    seen_keys: set[tuple[str, int]] = set()

    if entity["ledger_currency"] != "TRY":
        permission = entity.get("foreign_currency_permission", False)
        permission_source = entity.get("permission_source", "").strip()
        if not permission or not permission_source:
            findings.append(finding(
                "VUK-215-CURRENCY-001", "BLOCK", "entity",
                "Non-TRY bookkeeping requires explicit permission evidence; changing statutory thresholds are not hard-coded.",
                ["VUK-215"], ledger_currency=entity["ledger_currency"], permission=permission, permission_source=permission_source,
            ))

    for row_index, value in enumerate(rows):
        location = f"entries[{row_index}]"
        row = require_object(value, location)
        enforce_fields(row, location, JOURNAL_FIELDS, JOURNAL_REQUIRED)
        if not isinstance(row["journal_no"], (str, int)) or isinstance(row["journal_no"], bool):
            raise InputError(f"{location}.journal_no must be a string or integer")
        journal_no = str(row["journal_no"]).strip()
        if not journal_no:
            raise InputError(f"{location}.journal_no must not be blank")
        if not isinstance(row["line_no"], int) or isinstance(row["line_no"], bool) or row["line_no"] < 1:
            raise InputError(f"{location}.line_no must be a positive integer")
        line_no = row["line_no"]
        transaction_date = parse_iso_date(row["transaction_date"], f"{location}.transaction_date")
        ledger_date = parse_iso_date(row["ledger_date"], f"{location}.ledger_date")
        voucher_date = parse_iso_date(row["voucher_date"], f"{location}.voucher_date") if row.get("voucher_date") is not None else None
        if row["recording_basis"] not in {"direct_ledger", "authorized_voucher", "daily_required"}:
            raise InputError(f"{location}.recording_basis is outside the closed enum")
        if row["counterparty_relation"] not in {"third_party", "internal", "unknown"}:
            raise InputError(f"{location}.counterparty_relation is outside the closed enum")
        if not isinstance(row["description"], str):
            raise InputError(f"{location}.description must be a string")
        if options["require_descriptions"] and not row["description"].strip():
            findings.append(finding("THP-DESCRIPTION-001", "BLOCK", location, "Journal description is required by policy.", ["MSUGT-1"]))
        debit = parse_money(row["debit"], f"{location}.debit")
        credit = parse_money(row["credit"], f"{location}.credit")
        if (debit > 0 and credit > 0) or (debit == 0 and credit == 0):
            findings.append(finding("THP-LINE-001", "BLOCK", location, "Exactly one of debit or credit must be greater than zero.", ["MSUGT-1"], debit=decimal_text(debit), credit=decimal_text(credit)))

        row_findings, account, normalized_code = account_rule_findings(
            row["account_code"], row["account_name"], location, as_of, entity, options, catalog, index,
        )
        findings.extend(row_findings)

        key = (journal_no, line_no)
        if key in seen_keys:
            findings.append(finding("VUK-218-SEQUENCE-001", "BLOCK", location, "Journal and line number pair is duplicated.", ["VUK-218"], journal_no=journal_no, line_no=line_no))
        seen_keys.add(key)
        journals[journal_no]["debit"] += debit
        journals[journal_no]["credit"] += credit
        journals[journal_no]["line_nos"].append(line_no)

        if transaction_date > ledger_date:
            findings.append(finding("VUK-219-CHRONOLOGY-001", "BLOCK", location, "Ledger date cannot precede transaction date.", ["VUK-219"], transaction_date=transaction_date.isoformat(), ledger_date=ledger_date.isoformat()))
        delay_days = (ledger_date - transaction_date).days
        if row["recording_basis"] == "direct_ledger" and delay_days > 10:
            findings.append(finding("VUK-219-DIRECT-001", "BLOCK", location, "Direct ledger recording exceeds the 10-day limit.", ["VUK-219"], delay_days=delay_days, maximum_days=10))
        elif row["recording_basis"] == "authorized_voucher":
            if voucher_date is None:
                findings.append(finding("VUK-219-VOUCHER-001", "BLOCK", location, "Authorized-voucher basis requires voucher_date.", ["VUK-219"]))
            else:
                voucher_delay = (voucher_date - transaction_date).days
                if voucher_delay < 0 or voucher_date > ledger_date:
                    findings.append(finding("VUK-219-CHRONOLOGY-002", "BLOCK", location, "Voucher date must be between transaction and ledger dates.", ["VUK-219"], voucher_date=voucher_date.isoformat()))
                if voucher_delay > 10:
                    findings.append(finding("VUK-219-VOUCHER-002", "BLOCK", location, "Authorized voucher was not prepared within 10 days.", ["VUK-219"], delay_days=voucher_delay, maximum_days=10))
                if delay_days > 45:
                    findings.append(finding("VUK-219-VOUCHER-003", "BLOCK", location, "Transfer from authorized voucher to the main ledger exceeds 45 days.", ["VUK-219"], delay_days=delay_days, maximum_days=45))
        elif row["recording_basis"] == "daily_required" and delay_days != 0:
            findings.append(finding("VUK-219-DAILY-001", "BLOCK", location, "A daily-required record must be entered on the transaction date.", ["VUK-219"], delay_days=delay_days))

        if ledger_date > as_of:
            findings.append(finding("THP-DATE-001", "BLOCK", location, "Ledger date is after the analysis date.", ["MSUGT-1"], ledger_date=ledger_date.isoformat(), as_of_date=as_of.isoformat()))

        relation = row["counterparty_relation"]
        document_type = row.get("document_type")
        document_no = row.get("document_no")
        for field_name, field_value in (("document_type", document_type), ("document_no", document_no)):
            if field_value is not None and not isinstance(field_value, str):
                raise InputError(f"{location}.{field_name} must be a string")
        if relation == "third_party" and not (document_type and document_type.strip() and document_no and document_no.strip()):
            findings.append(finding("VUK-227-TEVSIK-001", "BLOCK", location, "Third-party transaction requires document type and document number.", ["VUK-227"]))
        if relation == "unknown":
            findings.append(finding("VUK-227-TEVSIK-002", "WARN", location, "Counterparty relation is unknown; document requirement needs professional review.", ["VUK-227"]))

        document_currency = row.get("document_currency", "TRY")
        if not isinstance(document_currency, str) or not re.fullmatch(r"[A-Z]{3}", document_currency):
            raise InputError(f"{location}.document_currency must be a three-letter uppercase currency code")
        try_equivalent = row.get("try_equivalent_present", False)
        foreign_customer = row.get("foreign_customer", False)
        if not isinstance(try_equivalent, bool) or not isinstance(foreign_customer, bool):
            raise InputError(f"{location}.try_equivalent_present and foreign_customer must be boolean")
        if document_currency != "TRY" and not try_equivalent and not foreign_customer:
            findings.append(finding("VUK-215-DOCUMENT-001", "BLOCK", location, "Foreign-currency document requires a TRY equivalent unless issued to a foreign customer.", ["VUK-215"], document_currency=document_currency))

        turkish_record = row.get("turkish_record_present", False)
        if not isinstance(turkish_record, bool):
            raise InputError(f"{location}.turkish_record_present must be boolean")
        if entity["language"] != "tr" and not turkish_record:
            findings.append(finding("VUK-215-LANGUAGE-001", "BLOCK", location, "Bookkeeping records must include Turkish records.", ["VUK-215"], language=entity["language"]))

        correction_of = row.get("correction_of")
        correction_method = row.get("correction_method")
        if correction_of is not None and not isinstance(correction_of, (str, int)):
            raise InputError(f"{location}.correction_of must be a string or integer")
        allowed_corrections = {"reversal_entry", "accounting_correction", "erase", "overwrite"}
        if correction_method is not None and correction_method not in allowed_corrections:
            raise InputError(f"{location}.correction_method is outside the closed enum")
        if correction_of is not None and correction_method not in {"reversal_entry", "accounting_correction"}:
            findings.append(finding("VUK-217-CORRECTION-001", "BLOCK", location, "Correction must use an auditable accounting correction or reversal entry.", ["VUK-217"], correction_method=correction_method))
        if correction_method in {"erase", "overwrite"}:
            findings.append(finding("VUK-217-CORRECTION-002", "BLOCK", location, "Erasing or unreadably overwriting a record is prohibited.", ["VUK-217"], correction_method=correction_method))
        if correction_method is not None and correction_of is None:
            findings.append(finding("VUK-217-CORRECTION-003", "BLOCK", location, "Correction method requires a reference to the corrected record.", ["VUK-217"]))

        normalized.append({
            "journal_no": journal_no,
            "line_no": line_no,
            "transaction_date": transaction_date.isoformat(),
            "ledger_date": ledger_date.isoformat(),
            "account_code": normalized_code,
            "root_code": normalized_code[:3],
            "account_name": row["account_name"],
            "normal_balance": account.get("normal_balance") if account else None,
            "debit": decimal_text(debit),
            "credit": decimal_text(credit),
            "recording_basis": row["recording_basis"],
        })

    journal_summaries: list[dict[str, Any]] = []
    for journal_no, totals in sorted(journals.items(), key=lambda item: item[0]):
        line_nos = sorted(totals["line_nos"])
        if options["require_contiguous_line_numbers"]:
            expected = list(range(1, max(line_nos) + 1))
            if line_nos != expected:
                findings.append(finding("VUK-218-SEQUENCE-002", "BLOCK", f"journal[{journal_no}]", "Journal line numbers must be unique and contiguous from 1.", ["VUK-218"], actual=line_nos, expected=expected))
        balanced = totals["debit"] == totals["credit"]
        if not balanced:
            findings.append(finding("THP-JOURNAL-BALANCE-001", "BLOCK", f"journal[{journal_no}]", "Journal debit and credit totals are not equal.", ["MSUGT-1"], debit=decimal_text(totals["debit"]), credit=decimal_text(totals["credit"]), difference=decimal_text(totals["debit"] - totals["credit"])))
        journal_summaries.append({
            "journal_no": journal_no,
            "line_count": len(line_nos),
            "debit": decimal_text(totals["debit"]),
            "credit": decimal_text(totals["credit"]),
            "balanced": balanced,
        })

    grand_debit = sum((item["debit"] for item in journals.values()), Decimal("0"))
    grand_credit = sum((item["credit"] for item in journals.values()), Decimal("0"))
    result = {
        "entry_count": len(rows),
        "journal_count": len(journals),
        "totals": {"debit": decimal_text(grand_debit), "credit": decimal_text(grand_credit), "balanced": grand_debit == grand_credit},
        "journals": journal_summaries,
        "normalized_entries": sorted(normalized, key=lambda item: (item["journal_no"], item["line_no"])),
        "limitations": [
            "VUK 218 line/page continuity control is limited to supplied journal_no and line_no values.",
            "Document presence is checked; document authenticity and substantive validity require evidence review.",
            "Account-code validity does not prove economic classification accuracy.",
        ],
        "_evaluated_rule_ids": [
            "THP-SCOPE-001", "THP-CODE-001", "THP-NAME-001", "THP-EFFECTIVE-001", "THP-CUSTOM-001",
            "THP-CUSTOM-002", "THP-COST-001", "THP-COST-002", "THP-SOURCE-001", "THP-DESCRIPTION-001", "THP-LINE-001",
            "THP-DATE-001", "THP-JOURNAL-BALANCE-001", "VUK-215-CURRENCY-001", "VUK-215-DOCUMENT-001",
            "VUK-215-LANGUAGE-001", "VUK-217-CORRECTION-001", "VUK-217-CORRECTION-002",
            "VUK-217-CORRECTION-003", "VUK-218-SEQUENCE-001", "VUK-218-SEQUENCE-002",
            "VUK-219-CHRONOLOGY-001", "VUK-219-CHRONOLOGY-002", "VUK-219-DIRECT-001",
            "VUK-219-VOUCHER-001", "VUK-219-VOUCHER-002", "VUK-219-VOUCHER-003", "VUK-219-DAILY-001",
            "VUK-227-TEVSIK-001", "VUK-227-TEVSIK-002",
        ],
    }
    return envelope("journal-validate", root, catalog, catalog_sha256, findings, result)


TRIAL_FIELDS = {
    "account_code", "account_name", "opening_debit", "opening_credit", "period_debit", "period_credit",
    "closing_debit", "closing_credit",
}


def run_trial_balance_validate(data: Any, catalog: dict[str, Any], catalog_sha256: str) -> dict[str, Any]:
    root, as_of, entity, options, rows = base_input(
        data, "trial-balance-validate", catalog,
        {"schema_version", "as_of_date", "entity", "accounts", "options"}, "accounts",
    )
    index = catalog_index(catalog)
    findings: list[dict[str, Any]] = []
    normalized: list[dict[str, Any]] = []
    seen: set[str] = set()
    totals = {key: Decimal("0") for key in ("opening_debit", "opening_credit", "period_debit", "period_credit", "closing_debit", "closing_credit")}

    for row_index, value in enumerate(rows):
        location = f"accounts[{row_index}]"
        row = require_object(value, location)
        enforce_fields(row, location, TRIAL_FIELDS, TRIAL_FIELDS)
        row_findings, account, normalized_code = account_rule_findings(
            row["account_code"], row["account_name"], location, as_of, entity, options, catalog, index,
        )
        findings.extend(row_findings)
        if normalized_code in seen:
            findings.append(finding("THP-DUPLICATE-001", "BLOCK", location, "Account code is duplicated in the trial balance.", ["MSUGT-1"], account_code=normalized_code))
        seen.add(normalized_code)
        amounts = {key: parse_money(row[key], f"{location}.{key}") for key in totals}
        for key, amount in amounts.items():
            totals[key] += amount
        for debit_key, credit_key, pair_name in (
            ("opening_debit", "opening_credit", "opening"),
            ("closing_debit", "closing_credit", "closing"),
        ):
            if amounts[debit_key] > 0 and amounts[credit_key] > 0:
                findings.append(finding("THP-TRIAL-SIDE-001", "BLOCK", location, "A balance cannot be shown on both debit and credit sides.", ["MSUGT-1"], pair=pair_name))

        expected_net = amounts["opening_debit"] - amounts["opening_credit"] + amounts["period_debit"] - amounts["period_credit"]
        actual_net = amounts["closing_debit"] - amounts["closing_credit"]
        if expected_net != actual_net:
            findings.append(finding(
                "THP-TRIAL-ROLLFORWARD-001", "BLOCK", location,
                "Closing balance does not reconcile to opening balance plus period movements.",
                ["MSUGT-1"], expected_net=decimal_text(expected_net), actual_net=decimal_text(actual_net), difference=decimal_text(actual_net - expected_net),
            ))
        if account and account["normal_balance"] in {"debit", "credit"} and actual_net != 0:
            anomalous = (account["normal_balance"] == "debit" and actual_net < 0) or (account["normal_balance"] == "credit" and actual_net > 0)
            if anomalous:
                severity = "BLOCK" if options["strict_normal_balance"] else "WARN"
                findings.append(finding(
                    "THP-NORMAL-BALANCE-001", severity, location,
                    "Closing balance is opposite to the catalog normal balance and requires review.",
                    [account["source_ref"]], normal_balance=account["normal_balance"], actual_net=decimal_text(actual_net),
                ))
        normalized.append({
            "account_code": normalized_code,
            "root_code": normalized_code[:3],
            "account_name": row["account_name"],
            "normal_balance": account.get("normal_balance") if account else None,
            **{key: decimal_text(amounts[key]) for key in totals},
            "expected_closing_net": decimal_text(expected_net),
            "actual_closing_net": decimal_text(actual_net),
        })

    balance_checks: dict[str, bool] = {}
    for label, debit_key, credit_key in (
        ("opening", "opening_debit", "opening_credit"),
        ("period", "period_debit", "period_credit"),
        ("closing", "closing_debit", "closing_credit"),
    ):
        balanced = totals[debit_key] == totals[credit_key]
        balance_checks[label] = balanced
        if not balanced:
            findings.append(finding(
                "THP-TRIAL-TOTAL-001", "BLOCK", f"totals.{label}",
                "Trial-balance debit and credit totals are not equal.",
                ["MSUGT-1"], debit=decimal_text(totals[debit_key]), credit=decimal_text(totals[credit_key]), difference=decimal_text(totals[debit_key] - totals[credit_key]),
            ))

    result = {
        "account_count": len(rows),
        "totals": {key: decimal_text(value) for key, value in totals.items()},
        "balance_checks": balance_checks,
        "normalized_accounts": sorted(normalized, key=lambda item: item["account_code"]),
        "_evaluated_rule_ids": [
            "THP-SCOPE-001", "THP-CODE-001", "THP-NAME-001", "THP-EFFECTIVE-001", "THP-CUSTOM-001",
            "THP-CUSTOM-002", "THP-COST-001", "THP-COST-002", "THP-SOURCE-001", "THP-DUPLICATE-001",
            "THP-TRIAL-SIDE-001",
            "THP-TRIAL-ROLLFORWARD-001", "THP-NORMAL-BALANCE-001", "THP-TRIAL-TOTAL-001",
        ],
    }
    return envelope("trial-balance-validate", root, catalog, catalog_sha256, findings, result)


def examples(operation: str) -> dict[str, Any]:
    entity = {"sector": "general", "chart": "MSUGT_THP_GENERAL", "cost_method": "7A"}
    if operation == "account-validate":
        return {"schema_version": 1, "as_of_date": "2026-08-02", "entity": entity, "accounts": [{"account_code": "100.01", "account_name": "Kasa"}]}
    if operation == "journal-validate":
        journal_entity = {**entity, "ledger_currency": "TRY", "language": "tr"}
        common = {
            "journal_no": "YEV-1", "transaction_date": "2026-08-01", "ledger_date": "2026-08-02",
            "recording_basis": "direct_ledger", "description": "Banka tahsilatı", "counterparty_relation": "third_party",
            "document_type": "banka dekontu", "document_no": "MASKELI-1",
        }
        return {
            "schema_version": 1, "as_of_date": "2026-08-02", "entity": journal_entity,
            "entries": [
                {**common, "line_no": 1, "account_code": "102", "account_name": "Bankalar", "debit": "1000.00", "credit": "0"},
                {**common, "line_no": 2, "account_code": "120", "account_name": "Alıcılar", "debit": "0", "credit": "1000.00"},
            ],
        }
    if operation == "trial-balance-validate":
        return {
            "schema_version": 1, "as_of_date": "2026-08-02", "entity": entity,
            "accounts": [
                {"account_code": "100", "account_name": "Kasa", "opening_debit": "0", "opening_credit": "0", "period_debit": "100", "period_credit": "0", "closing_debit": "100", "closing_credit": "0"},
                {"account_code": "500", "account_name": "Sermaye", "opening_debit": "0", "opening_credit": "0", "period_debit": "0", "period_credit": "100", "closing_debit": "0", "closing_credit": "100"},
            ],
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
    for operation in ("account-validate", "journal-validate", "trial-balance-validate"):
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
            if operation == "account-validate":
                output = run_account_validate(data, catalog, catalog_sha256)
            elif operation == "journal-validate":
                output = run_journal_validate(data, catalog, catalog_sha256)
            else:
                output = run_trial_balance_validate(data, catalog, catalog_sha256)
        write_output(output, args.output)
        return 1 if output["decision"] == "BLOCK" else 0
    except (InputError, CatalogError, OSError) as exc:
        output_path = getattr(args, "output", None)
        write_output(error_envelope(operation, str(exc)), output_path)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

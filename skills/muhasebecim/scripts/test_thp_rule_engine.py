#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path

import case_workflow
import ingest_sources
import muhasebecim_engine
import thp_rule_engine as thp


CATALOG, CATALOG_SHA256 = thp.load_catalog(thp.DEFAULT_CATALOG)


def entity(cost_method: str = "7A") -> dict[str, object]:
    return {"sector": "general", "chart": "MSUGT_THP_GENERAL", "cost_method": cost_method}


def journal_entity() -> dict[str, object]:
    return {**entity(), "ledger_currency": "TRY", "language": "tr"}


def journal_input() -> dict[str, object]:
    common = {
        "journal_no": "YEV-1",
        "transaction_date": "2026-08-01",
        "ledger_date": "2026-08-02",
        "recording_basis": "direct_ledger",
        "description": "Banka tahsilatı",
        "counterparty_relation": "third_party",
        "document_type": "banka dekontu",
        "document_no": "MASKELI-1",
    }
    return {
        "schema_version": 1,
        "as_of_date": "2026-08-02",
        "entity": journal_entity(),
        "entries": [
            {**common, "line_no": 1, "account_code": "102", "account_name": "Bankalar", "debit": "1000.00", "credit": "0"},
            {**common, "line_no": 2, "account_code": "120", "account_name": "Alıcılar", "debit": "0", "credit": "1000.00"},
        ],
    }


def trial_input() -> dict[str, object]:
    return {
        "schema_version": 1,
        "as_of_date": "2026-08-02",
        "entity": entity(),
        "accounts": [
            {
                "account_code": "100", "account_name": "Kasa",
                "opening_debit": "0", "opening_credit": "0", "period_debit": "100", "period_credit": "0",
                "closing_debit": "100", "closing_credit": "0",
            },
            {
                "account_code": "500", "account_name": "Sermaye",
                "opening_debit": "0", "opening_credit": "0", "period_debit": "0", "period_credit": "100",
                "closing_debit": "0", "closing_credit": "100",
            },
        ],
    }


def rule_ids(result: dict[str, object]) -> set[str]:
    return {item["rule_id"] for item in result["findings"]}  # type: ignore[index]


class CatalogAndAccountTests(unittest.TestCase):
    def test_catalog_audit_passes(self) -> None:
        result = thp.run_catalog_audit(CATALOG, CATALOG_SHA256)
        self.assertEqual(result["decision"], "PASS")
        self.assertGreaterEqual(result["result"]["account_count"], 270)

    def test_account_validation_is_byte_deterministic(self) -> None:
        data = {
            "schema_version": 1,
            "as_of_date": "2026-08-02",
            "entity": entity(),
            "accounts": [{"account_code": "100-01", "account_name": "Kasa"}],
        }
        first = thp.run_account_validate(copy.deepcopy(data), CATALOG, CATALOG_SHA256)
        second = thp.run_account_validate(copy.deepcopy(data), CATALOG, CATALOG_SHA256)
        self.assertEqual(thp.canonical_json(first), thp.canonical_json(second))
        self.assertEqual(first["decision"], "PASS")
        self.assertEqual(first["result"]["normalized_accounts"][0]["account_code"], "100.01")

    def test_unknown_code_is_fail_closed(self) -> None:
        data = {
            "as_of_date": "2026-08-02", "entity": entity(),
            "accounts": [{"account_code": "339", "account_name": "Diğer Çeşitli Borçlar"}],
        }
        result = thp.run_account_validate(data, CATALOG, CATALOG_SHA256)
        self.assertEqual(result["decision"], "BLOCK")
        self.assertIn("THP-CODE-001", rule_ids(result))

    def test_known_336_and_397_accounts_pass(self) -> None:
        data = {
            "as_of_date": "2026-08-02", "entity": entity(),
            "accounts": [
                {"account_code": "336", "account_name": "Diğer Çeşitli Borçlar"},
                {"account_code": "397", "account_name": "Sayım ve Tesellüm Fazlaları"},
            ],
        }
        self.assertEqual(thp.run_account_validate(data, CATALOG, CATALOG_SHA256)["decision"], "PASS")

    def test_secondary_only_account_source_warns(self) -> None:
        data = {
            "as_of_date": "2026-08-02", "entity": entity(),
            "accounts": [{"account_code": "524", "account_name": "Maliyet Bedeli Artışları Fonu"}],
        }
        result = thp.run_account_validate(data, CATALOG, CATALOG_SHA256)
        self.assertEqual(result["decision"], "PASS_WITH_WARNINGS")
        self.assertIn("THP-SOURCE-001", rule_ids(result))

    def test_account_name_mismatch_blocks(self) -> None:
        data = {
            "as_of_date": "2026-08-02", "entity": entity(),
            "accounts": [{"account_code": "100", "account_name": "Bankalar"}],
        }
        result = thp.run_account_validate(data, CATALOG, CATALOG_SHA256)
        self.assertIn("THP-NAME-001", rule_ids(result))

    def test_regulated_sector_blocks_general_chart(self) -> None:
        regulated = entity()
        regulated["sector"] = "bank"
        data = {
            "as_of_date": "2026-08-02", "entity": regulated,
            "accounts": [{"account_code": "100", "account_name": "Kasa"}],
        }
        result = thp.run_account_validate(data, CATALOG, CATALOG_SHA256)
        self.assertIn("THP-SCOPE-001", rule_ids(result))

    def test_7a_7b_mixing_blocks(self) -> None:
        data = {
            "as_of_date": "2026-08-02", "entity": entity("7A"),
            "accounts": [{"account_code": "790", "account_name": "İlk Madde ve Malzeme Giderleri"}],
        }
        result = thp.run_account_validate(data, CATALOG, CATALOG_SHA256)
        self.assertIn("THP-COST-002", rule_ids(result))

    def test_later_account_blocks_before_effective_date(self) -> None:
        data = {
            "as_of_date": "2003-01-01", "entity": entity(),
            "accounts": [{"account_code": "124", "account_name": "Kazanılmamış Finansal Kiralama Faiz Gelirleri (-)"}],
        }
        result = thp.run_account_validate(data, CATALOG, CATALOG_SHA256)
        self.assertIn("THP-EFFECTIVE-001", rule_ids(result))

    def test_custom_class_9_policy(self) -> None:
        data = {
            "as_of_date": "2026-08-02", "entity": entity(),
            "accounts": [{"account_code": "900.01", "account_name": "Verilen Teminat Mektupları"}],
        }
        self.assertEqual(thp.run_account_validate(data, CATALOG, CATALOG_SHA256)["decision"], "PASS")
        data["options"] = {"allow_custom_8_9": False}
        result = thp.run_account_validate(data, CATALOG, CATALOG_SHA256)
        self.assertIn("THP-CUSTOM-001", rule_ids(result))

    def test_money_and_account_codes_are_strings(self) -> None:
        data = {
            "as_of_date": "2026-08-02", "entity": entity(),
            "accounts": [{"account_code": 100, "account_name": "Kasa"}],
        }
        with self.assertRaises(thp.InputError):
            thp.run_account_validate(data, CATALOG, CATALOG_SHA256)

    def test_unknown_input_field_is_schema_error(self) -> None:
        data = {
            "as_of_date": "2026-08-02", "entity": entity(), "unexpected": True,
            "accounts": [{"account_code": "100", "account_name": "Kasa"}],
        }
        with self.assertRaises(thp.InputError):
            thp.run_account_validate(data, CATALOG, CATALOG_SHA256)


class JournalVukTests(unittest.TestCase):
    def test_positive_journal_passes(self) -> None:
        result = thp.run_journal_validate(journal_input(), CATALOG, CATALOG_SHA256)
        self.assertEqual(result["decision"], "PASS")
        self.assertTrue(result["result"]["totals"]["balanced"])

    def test_direct_recording_after_ten_days_blocks(self) -> None:
        data = journal_input()
        for row in data["entries"]:  # type: ignore[index]
            row["ledger_date"] = "2026-08-12"
        data["as_of_date"] = "2026-08-12"
        result = thp.run_journal_validate(data, CATALOG, CATALOG_SHA256)
        self.assertIn("VUK-219-DIRECT-001", rule_ids(result))

    def test_authorized_voucher_transfer_after_45_days_blocks(self) -> None:
        data = journal_input()
        for row in data["entries"]:  # type: ignore[index]
            row["recording_basis"] = "authorized_voucher"
            row["voucher_date"] = "2026-08-05"
            row["ledger_date"] = "2026-09-16"
        data["as_of_date"] = "2026-09-16"
        result = thp.run_journal_validate(data, CATALOG, CATALOG_SHA256)
        self.assertIn("VUK-219-VOUCHER-003", rule_ids(result))

    def test_daily_record_must_be_same_day(self) -> None:
        data = journal_input()
        for row in data["entries"]:  # type: ignore[index]
            row["recording_basis"] = "daily_required"
        result = thp.run_journal_validate(data, CATALOG, CATALOG_SHA256)
        self.assertIn("VUK-219-DAILY-001", rule_ids(result))

    def test_third_party_document_gate(self) -> None:
        data = journal_input()
        del data["entries"][0]["document_no"]  # type: ignore[index]
        result = thp.run_journal_validate(data, CATALOG, CATALOG_SHA256)
        self.assertIn("VUK-227-TEVSIK-001", rule_ids(result))

    def test_foreign_document_needs_try_equivalent(self) -> None:
        data = journal_input()
        data["entries"][0]["document_currency"] = "EUR"  # type: ignore[index]
        result = thp.run_journal_validate(data, CATALOG, CATALOG_SHA256)
        self.assertIn("VUK-215-DOCUMENT-001", rule_ids(result))

    def test_non_try_ledger_needs_permission_evidence(self) -> None:
        data = journal_input()
        data["entity"]["ledger_currency"] = "EUR"  # type: ignore[index]
        result = thp.run_journal_validate(data, CATALOG, CATALOG_SHA256)
        self.assertIn("VUK-215-CURRENCY-001", rule_ids(result))

    def test_erasure_correction_blocks(self) -> None:
        data = journal_input()
        data["entries"][0]["correction_of"] = "YEV-OLD-1"  # type: ignore[index]
        data["entries"][0]["correction_method"] = "erase"  # type: ignore[index]
        result = thp.run_journal_validate(data, CATALOG, CATALOG_SHA256)
        self.assertIn("VUK-217-CORRECTION-002", rule_ids(result))

    def test_duplicate_and_gap_line_numbers_block(self) -> None:
        data = journal_input()
        data["entries"][1]["line_no"] = 3  # type: ignore[index]
        result = thp.run_journal_validate(data, CATALOG, CATALOG_SHA256)
        self.assertIn("VUK-218-SEQUENCE-002", rule_ids(result))

    def test_unbalanced_journal_blocks(self) -> None:
        data = journal_input()
        data["entries"][1]["credit"] = "999"  # type: ignore[index]
        result = thp.run_journal_validate(data, CATALOG, CATALOG_SHA256)
        self.assertIn("THP-JOURNAL-BALANCE-001", rule_ids(result))

    def test_cli_exit_codes_are_pass_block_error(self) -> None:
        script = Path(thp.__file__).resolve()
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            valid_path = root / "valid.json"
            block_path = root / "block.json"
            error_path = root / "error.json"
            valid_path.write_text(json.dumps(journal_input(), ensure_ascii=False), encoding="utf-8")
            blocked = journal_input()
            blocked["entries"][1]["credit"] = "1"  # type: ignore[index]
            block_path.write_text(json.dumps(blocked, ensure_ascii=False), encoding="utf-8")
            invalid = journal_input()
            invalid["entries"][0]["debit"] = 1000.0  # type: ignore[index]
            error_path.write_text(json.dumps(invalid, ensure_ascii=False), encoding="utf-8")
            codes = []
            for path in (valid_path, block_path, error_path):
                process = subprocess.run(
                    [sys.executable, str(script), "journal-validate", "--input", str(path)],
                    capture_output=True, check=False,
                )
                json.loads(process.stdout.decode("utf-8"))
                codes.append(process.returncode)
            self.assertEqual(codes, [0, 1, 2])

    def test_cli_usage_error_is_json(self) -> None:
        process = subprocess.run(
            [sys.executable, str(Path(thp.__file__).resolve())],
            capture_output=True, check=False,
        )
        payload = json.loads(process.stdout.decode("utf-8"))
        self.assertEqual(process.returncode, 2)
        self.assertEqual(payload["decision"], "ERROR")


class TrialBalanceTests(unittest.TestCase):
    def test_positive_trial_balance_passes(self) -> None:
        result = thp.run_trial_balance_validate(trial_input(), CATALOG, CATALOG_SHA256)
        self.assertEqual(result["decision"], "PASS")
        self.assertEqual(result["result"]["balance_checks"], {"opening": True, "period": True, "closing": True})

    def test_rollforward_error_blocks(self) -> None:
        data = trial_input()
        data["accounts"][0]["closing_debit"] = "90"  # type: ignore[index]
        result = thp.run_trial_balance_validate(data, CATALOG, CATALOG_SHA256)
        self.assertIn("THP-TRIAL-ROLLFORWARD-001", rule_ids(result))

    def test_normal_balance_anomaly_warns_or_blocks_by_policy(self) -> None:
        data = trial_input()
        first = data["accounts"][0]  # type: ignore[index]
        second = data["accounts"][1]  # type: ignore[index]
        first.update({"period_debit": "0", "period_credit": "100", "closing_debit": "0", "closing_credit": "100"})
        second.update({"period_debit": "100", "period_credit": "0", "closing_debit": "100", "closing_credit": "0"})
        warning = thp.run_trial_balance_validate(copy.deepcopy(data), CATALOG, CATALOG_SHA256)
        self.assertEqual(warning["decision"], "PASS_WITH_WARNINGS")
        data["options"] = {"strict_normal_balance": True}
        blocked = thp.run_trial_balance_validate(data, CATALOG, CATALOG_SHA256)
        self.assertEqual(blocked["decision"], "BLOCK")


class WorkflowIntegrationTests(unittest.TestCase):
    def test_case_gate_accepts_only_valid_thp_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            case_dir = Path(temp_dir) / "case"
            case_workflow.init_case(case_dir, "thp-gate", "2026-08-02")
            case_path = case_dir / "case.json"
            case = json.loads(case_path.read_text(encoding="utf-8"))
            case["requires_thp_validation"] = True
            case_path.write_text(json.dumps(case, ensure_ascii=False), encoding="utf-8")
            output_path = case_dir / "outputs" / "thp-validation-result.json"
            result = thp.run_journal_validate(journal_input(), CATALOG, CATALOG_SHA256)
            output_path.write_text(json.dumps(result, ensure_ascii=False), encoding="utf-8")
            gate = next(item for item in case_workflow.check_case(case_dir)["gates"] if item["name"] == "thp_vuk_validation")
            self.assertTrue(gate["passed"])

            result["result"]["totals"]["debit"] = "999999"
            output_path.write_text(json.dumps(result, ensure_ascii=False), encoding="utf-8")
            tampered_gate = next(item for item in case_workflow.check_case(case_dir)["gates"] if item["name"] == "thp_vuk_validation")
            self.assertFalse(tampered_gate["passed"])
            self.assertFalse(tampered_gate["details"]["receipt_valid"])


class ReleaseVersionTests(unittest.TestCase):
    def test_all_component_versions_match_release(self) -> None:
        project_root = Path(thp.__file__).resolve().parents[3]
        project = tomllib.loads((project_root / "pyproject.toml").read_text(encoding="utf-8"))
        self.assertEqual(project["project"]["version"], "0.0.1")
        self.assertEqual(thp.ENGINE_VERSION, "0.0.1")
        self.assertEqual(muhasebecim_engine.ENGINE_VERSION, "0.0.1")
        self.assertEqual(case_workflow.VERSION, "0.0.1")
        self.assertEqual(ingest_sources.VERSION, "0.0.1")


if __name__ == "__main__":
    unittest.main()

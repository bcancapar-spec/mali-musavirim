#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import case_workflow
import taxpayer_interest_engine as interest


CATALOG, CATALOG_SHA256 = interest.load_catalog(interest.DEFAULT_CATALOG)


def rule_ids(result: dict[str, object]) -> set[str]:
    return {item["rule_id"] for item in result["findings"]}  # type: ignore[index]


def adverse_matter() -> dict[str, object]:
    return {
        "matter_id": "RISK-001",
        "severity": "high",
        "summary": "Belge ile kayıt arasında açıklanması gereken fark var.",
        "factual_basis_references": ["workpapers/reconciliation.json"],
        "legal_basis_reference": "Vaka tarihinde doğrulanan VUK hükümleri",
        "estimated_impact_reference": "calculations/result-impact.json",
        "protective_action_id": "ACTION-001",
        "internal_alert": {
            "prepared": True,
            "alert_reference": "workpapers/internal-intelligence/RISK-001.json",
            "alert_sha256": "a23e1d739d548dcc473059be782fce6dfe2eeafbfcb2c6445c187e5e3f6e5d16",
            "recipients": ["user", "smmm"],
            "acknowledged": True,
            "acknowledged_by": "SMMM-MASKED",
            "acknowledged_at": "2026-08-02",
            "external_transmission": False,
        },
    }


class TaxpayerInterestCatalogTests(unittest.TestCase):
    def test_catalog_audit_passes(self) -> None:
        result = interest.run_catalog_audit(CATALOG, CATALOG_SHA256)
        self.assertEqual(result["decision"], "PASS")
        self.assertEqual(result["result"]["rule_count"], 16)
        self.assertEqual(result["result"]["source_count"], 5)

    def test_catalog_tampering_blocks(self) -> None:
        catalog = copy.deepcopy(CATALOG)
        catalog["rules"].pop()
        result = interest.run_catalog_audit(catalog, interest.sha256_value(catalog))
        self.assertEqual(result["decision"], "BLOCK")
        self.assertTrue({"CAT-HASH-001", "CAT-RULE-006"}.issubset(rule_ids(result)))


class TaxpayerInterestValidationTests(unittest.TestCase):
    def test_favorable_path_passes_and_is_deterministic(self) -> None:
        data = interest.example()
        first = interest.run_validate(copy.deepcopy(data), CATALOG, CATALOG_SHA256)
        second = interest.run_validate(copy.deepcopy(data), CATALOG, CATALOG_SHA256)
        self.assertEqual(interest.canonical_json(first), interest.canonical_json(second))
        self.assertEqual(first["decision"], "PASS")
        self.assertEqual(first["result"]["taxpayer_favorable_path_status"], "PREPARED")
        self.assertEqual(first["result"]["internal_intelligence_status"], "CLEAR")
        self.assertFalse(first["result"]["external_transmission_permitted"])

    def test_missing_favorable_action_blocks(self) -> None:
        data = interest.example()
        data["favorable_actions"] = []
        result = interest.run_validate(data, CATALOG, CATALOG_SHA256)
        self.assertEqual(result["decision"], "BLOCK")
        self.assertTrue({"ML-LEH-001", "ML-LEH-003"}.issubset(rule_ids(result)))

    def test_expired_action_is_warning_and_no_active_path_blocks(self) -> None:
        data = interest.example()
        action = data["favorable_actions"][0]
        action["deadline_applicable"] = True
        action["deadline"] = "2026-08-01"
        result = interest.run_validate(data, CATALOG, CATALOG_SHA256)
        self.assertTrue({"ML-SURE-002", "ML-LEH-003"}.issubset(rule_ids(result)))

    def test_adverse_matter_requires_complete_internal_alert(self) -> None:
        data = interest.example()
        matter = adverse_matter()
        alert = matter["internal_alert"]
        alert.update({
            "prepared": False,
            "alert_reference": None,
            "recipients": [],
            "acknowledged": False,
            "acknowledged_by": None,
            "acknowledged_at": None,
            "external_transmission": True,
        })
        matter["protective_action_id"] = "MISSING-ACTION"
        data["adverse_matters"] = [matter]
        result = interest.run_validate(data, CATALOG, CATALOG_SHA256)
        self.assertEqual(result["decision"], "BLOCK")
        self.assertTrue({"ML-ALEYH-001", "ML-ALICI-001", "ML-ACK-001", "ML-KORUMA-001", "ML-DIS-001"}.issubset(rule_ids(result)))
        self.assertEqual(result["result"]["internal_intelligence_status"], "PENDING_ACKNOWLEDGEMENT")

    def test_adverse_matter_passes_only_after_acknowledged_local_alert(self) -> None:
        data = interest.example()
        data["adverse_matters"] = [adverse_matter()]
        result = interest.run_validate(data, CATALOG, CATALOG_SHA256)
        self.assertEqual(result["decision"], "PASS")
        self.assertEqual(result["result"]["internal_intelligence_status"], "ACKNOWLEDGED")
        self.assertEqual(result["result"]["adverse_matter_ids"], ["RISK-001"])

    def test_future_acknowledgement_date_blocks(self) -> None:
        data = interest.example()
        matter = adverse_matter()
        matter["internal_alert"]["acknowledged_at"] = "2026-08-03"
        data["adverse_matters"] = [matter]
        result = interest.run_validate(data, CATALOG, CATALOG_SHA256)
        self.assertIn("ML-ACK-001", rule_ids(result))

    def test_suppression_and_lost_independence_block(self) -> None:
        data = interest.example()
        data["controls"]["adverse_facts_suppressed"] = True
        data["controls"]["independence_and_impartiality_preserved"] = False
        result = interest.run_validate(data, CATALOG, CATALOG_SHA256)
        self.assertTrue({"ML-GIZLEME-001", "ML-BAGIMSIZLIK-001"}.issubset(rule_ids(result)))

    def test_unknown_input_field_is_schema_error(self) -> None:
        data = interest.example()
        data["unexpected"] = True
        with self.assertRaises(interest.InputError):
            interest.run_validate(data, CATALOG, CATALOG_SHA256)


class TaxpayerInterestCliAndWorkflowTests(unittest.TestCase):
    def test_cli_exit_codes_are_pass_block_error(self) -> None:
        script = Path(interest.__file__).resolve()
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            valid = interest.example()
            blocked = copy.deepcopy(valid)
            blocked["favorable_actions"] = []
            invalid = copy.deepcopy(valid)
            invalid["controls"]["lawful_only"] = "yes"
            codes = []
            for name, value in (("valid", valid), ("blocked", blocked), ("invalid", invalid)):
                path = root / f"{name}.json"
                path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")
                process = subprocess.run(
                    [sys.executable, str(script), interest.OPERATION, "--input", str(path)],
                    capture_output=True,
                    check=False,
                )
                json.loads(process.stdout.decode("utf-8"))
                codes.append(process.returncode)
            self.assertEqual(codes, [0, 1, 2])

    def test_case_workflow_requires_valid_taxpayer_interest_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            case_dir = Path(temp_dir) / "case"
            case_workflow.init_case(case_dir, "taxpayer-interest", "2026-08-02")
            case_path = case_dir / "case.json"
            case = json.loads(case_path.read_text(encoding="utf-8"))
            case["requires_taxpayer_interest_review"] = False
            case_workflow.write_json(case_path, case)
            initial = {row["name"]: row for row in case_workflow.check_case(case_dir)["gates"]}
            self.assertTrue(initial["taxpayer_interest_and_internal_alert"]["details"]["required"])
            self.assertFalse(initial["taxpayer_interest_and_internal_alert"]["passed"])

            result = interest.run_validate(interest.example(), CATALOG, CATALOG_SHA256)
            output = case_dir / "outputs" / "taxpayer-interest-result.json"
            action_path = case_dir / "workpapers" / "taxpayer-actions" / "ACTION-001.json"
            action_path.parent.mkdir(parents=True, exist_ok=True)
            action_path.write_bytes(b'{"action_id":"ACTION-001"}\n')
            case_workflow.write_json(output, result)
            passed = {row["name"]: row for row in case_workflow.check_case(case_dir)["gates"]}
            self.assertTrue(passed["taxpayer_interest_and_internal_alert"]["passed"])

            action_path.write_bytes(b'{"action_id":"ACTION-001","tampered":true}\n')
            missing_or_changed = {row["name"]: row for row in case_workflow.check_case(case_dir)["gates"]}
            self.assertFalse(missing_or_changed["taxpayer_interest_and_internal_alert"]["passed"])
            self.assertTrue(missing_or_changed["taxpayer_interest_and_internal_alert"]["details"]["artifact_errors"])
            action_path.write_bytes(b'{"action_id":"ACTION-001"}\n')

            result["result"]["internal_intelligence_status"] = "ACKNOWLEDGED"
            case_workflow.write_json(output, result)
            tampered = {row["name"]: row for row in case_workflow.check_case(case_dir)["gates"]}
            self.assertFalse(tampered["taxpayer_interest_and_internal_alert"]["passed"])
            self.assertFalse(tampered["taxpayer_interest_and_internal_alert"]["details"]["receipt_valid"])

    def test_case_workflow_verifies_physical_adverse_alert(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            case_dir = Path(temp_dir) / "case"
            case_workflow.init_case(case_dir, "adverse-alert", "2026-08-02")
            action_path = case_dir / "workpapers" / "taxpayer-actions" / "ACTION-001.json"
            alert_path = case_dir / "workpapers" / "internal-intelligence" / "RISK-001.json"
            action_path.parent.mkdir(parents=True, exist_ok=True)
            alert_path.parent.mkdir(parents=True, exist_ok=True)
            action_path.write_bytes(b'{"action_id":"ACTION-001"}\n')
            alert_path.write_bytes(b'{"matter_id":"RISK-001"}\n')
            data = interest.example()
            data["adverse_matters"] = [adverse_matter()]
            result = interest.run_validate(data, CATALOG, CATALOG_SHA256)
            case_workflow.write_json(case_dir / "outputs" / "taxpayer-interest-result.json", result)
            gate = next(row for row in case_workflow.check_case(case_dir)["gates"] if row["name"] == "taxpayer_interest_and_internal_alert")
            self.assertTrue(gate["passed"])


if __name__ == "__main__":
    unittest.main(verbosity=2)

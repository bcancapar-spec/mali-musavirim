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
import professional_role_engine as roles


CATALOG, CATALOG_SHA256 = roles.load_catalog(roles.DEFAULT_CATALOG)


def rule_ids(result: dict[str, object]) -> set[str]:
    return {item["rule_id"] for item in result["findings"]}  # type: ignore[index]


class ProfessionalRoleCatalogTests(unittest.TestCase):
    def test_catalog_audit_passes(self) -> None:
        result = roles.run_catalog_audit(CATALOG, CATALOG_SHA256)
        self.assertEqual(result["decision"], "PASS")
        self.assertEqual(result["result"]["operation_count"], 2)
        self.assertGreaterEqual(result["result"]["rule_count"], 45)
        self.assertGreaterEqual(result["result"]["source_count"], 15)

    def test_missing_baseline_rule_blocks_catalog(self) -> None:
        catalog = copy.deepcopy(CATALOG)
        catalog["rules"]["inspection-readiness-validate"].pop()
        result = roles.run_catalog_audit(catalog, roles.sha256_value(catalog))
        self.assertEqual(result["decision"], "BLOCK")
        self.assertIn("CAT-RULE-011", rule_ids(result))


class InspectionReadinessTests(unittest.TestCase):
    def test_taxpayer_readiness_passes_and_is_deterministic(self) -> None:
        data = roles.examples("inspection-readiness-validate")
        first = roles.run_validate(copy.deepcopy(data), "inspection-readiness-validate", CATALOG, CATALOG_SHA256)
        second = roles.run_validate(copy.deepcopy(data), "inspection-readiness-validate", CATALOG, CATALOG_SHA256)
        self.assertEqual(roles.canonical_json(first), roles.canonical_json(second))
        self.assertEqual(first["decision"], "PASS")
        self.assertEqual(first["result"]["output_status"], "DRAFT_TAXPAYER_READINESS_ONLY")
        self.assertFalse(first["result"]["professional_act_permitted"])

    def test_authorized_mode_requires_authority_assignment_and_notice(self) -> None:
        data = roles.examples("inspection-readiness-validate")
        data["engagement"]["mode"] = "authorized_inspector_support"
        result = roles.run_validate(data, "inspection-readiness-validate", CATALOG, CATALOG_SHA256)
        self.assertEqual(result["decision"], "BLOCK")
        self.assertTrue({"VI-YETKI-001", "VI-GOREV-001", "VI-BASLAMA-001", "VI-BASLAMA-002"}.issubset(rule_ids(result)))

    def test_external_customer_data_blocks(self) -> None:
        data = roles.examples("inspection-readiness-validate")
        data["engagement"]["data_location"] = "external"
        result = roles.run_validate(data, "inspection-readiness-validate", CATALOG, CATALOG_SHA256)
        self.assertIn("VI-YEREL-001", rule_ids(result))

    def test_unknown_input_field_is_schema_error(self) -> None:
        data = roles.examples("inspection-readiness-validate")
        data["unexpected"] = True
        with self.assertRaises(roles.InputError):
            roles.run_validate(data, "inspection-readiness-validate", CATALOG, CATALOG_SHA256)


class YmmCertificationTests(unittest.TestCase):
    def test_pre_certification_readiness_does_not_require_license(self) -> None:
        data = roles.examples("ymm-certification-validate")
        result = roles.run_validate(data, "ymm-certification-validate", CATALOG, CATALOG_SHA256)
        self.assertEqual(result["decision"], "PASS")
        self.assertEqual(result["result"]["output_status"], "DRAFT_READINESS_ONLY")
        self.assertNotIn("YMM-RUHSAT-001", result["evaluated_rule_ids"])

    def test_licensed_mode_requires_license_list_and_seal(self) -> None:
        data = roles.examples("ymm-certification-validate")
        data["engagement"]["mode"] = "licensed_ymm_support"
        result = roles.run_validate(data, "ymm-certification-validate", CATALOG, CATALOG_SHA256)
        self.assertEqual(result["decision"], "BLOCK")
        self.assertTrue({"YMM-RUHSAT-001", "YMM-RUHSAT-002", "YMM-LISTE-001", "YMM-MUHUR-001"}.issubset(rule_ids(result)))

    def test_licensed_mode_passes_with_evidence_but_remains_draft(self) -> None:
        data = roles.examples("ymm-certification-validate")
        data["engagement"].update({
            "mode": "licensed_ymm_support",
            "licensed_ymm_confirmed": True,
            "license_evidence": "workpapers/ymm-license-check.json",
            "working_list_confirmed": True,
            "seal_available": True,
        })
        result = roles.run_validate(data, "ymm-certification-validate", CATALOG, CATALOG_SHA256)
        self.assertEqual(result["decision"], "PASS")
        self.assertEqual(result["result"]["output_status"], "DRAFT_FOR_LICENSED_YMM")
        self.assertFalse(result["result"]["professional_act_permitted"])

    def test_independence_relationship_and_bookkeeping_fail_closed(self) -> None:
        data = roles.examples("ymm-certification-validate")
        data["engagement"].update({
            "independence_confirmed": False,
            "prohibited_relationship_absent": False,
            "bookkeeping_separation_confirmed": False,
        })
        result = roles.run_validate(data, "ymm-certification-validate", CATALOG, CATALOG_SHA256)
        self.assertTrue({"YMM-BAGIMSIZLIK-001", "YMM-ILISKI-001", "YMM-DEFTER-001"}.issubset(rule_ids(result)))


class ProfessionalRoleCliAndWorkflowTests(unittest.TestCase):
    def test_cli_exit_codes_are_pass_block_error(self) -> None:
        script = Path(roles.__file__).resolve()
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            valid = roles.examples("ymm-certification-validate")
            blocked = copy.deepcopy(valid)
            blocked["engagement"]["independence_confirmed"] = False
            invalid = copy.deepcopy(valid)
            invalid["engagement"]["written_contract_present"] = "yes"
            paths = []
            for name, value in (("valid", valid), ("blocked", blocked), ("invalid", invalid)):
                path = root / f"{name}.json"
                path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")
                paths.append(path)
            codes = []
            for path in paths:
                process = subprocess.run(
                    [sys.executable, str(script), "ymm-certification-validate", "--input", str(path)],
                    capture_output=True,
                    check=False,
                )
                json.loads(process.stdout.decode("utf-8"))
                codes.append(process.returncode)
            self.assertEqual(codes, [0, 1, 2])

    def test_case_workflow_accepts_only_valid_professional_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            case_dir = Path(temp_dir) / "case"
            case_workflow.init_case(case_dir, "professional-gates", "2026-08-02")
            case_path = case_dir / "case.json"
            case = json.loads(case_path.read_text(encoding="utf-8"))
            case["requires_inspection_readiness"] = True
            case["requires_ymm_certification"] = True
            case_workflow.write_json(case_path, case)

            inspection = roles.run_validate(
                roles.examples("inspection-readiness-validate"),
                "inspection-readiness-validate", CATALOG, CATALOG_SHA256,
            )
            ymm = roles.run_validate(
                roles.examples("ymm-certification-validate"),
                "ymm-certification-validate", CATALOG, CATALOG_SHA256,
            )
            case_workflow.write_json(case_dir / "outputs" / "inspection-readiness-result.json", inspection)
            case_workflow.write_json(case_dir / "outputs" / "ymm-certification-result.json", ymm)
            gates = {item["name"]: item for item in case_workflow.check_case(case_dir)["gates"]}
            self.assertTrue(gates["inspection_readiness"]["passed"])
            self.assertTrue(gates["ymm_certification"]["passed"])

            ymm["result"]["output_status"] = "CERTIFIED"
            case_workflow.write_json(case_dir / "outputs" / "ymm-certification-result.json", ymm)
            tampered = {item["name"]: item for item in case_workflow.check_case(case_dir)["gates"]}
            self.assertFalse(tampered["ymm_certification"]["passed"])
            self.assertFalse(tampered["ymm_certification"]["details"]["receipt_valid"])


if __name__ == "__main__":
    unittest.main(verbosity=2)

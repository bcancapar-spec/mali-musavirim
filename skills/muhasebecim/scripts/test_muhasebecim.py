#!/usr/bin/env python3
from __future__ import annotations

import json
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

import ingest_sources
import muhasebecim_engine as engine
import query_corpus
import case_workflow
import prepare_2026_tfrs_manifest


class EngineTests(unittest.TestCase):
    def test_journal_balanced(self) -> None:
        result = engine.journal_check(
            {
                "entries": [
                    {"account": "100", "debit": "120.00", "credit": "0"},
                    {"account": "600", "debit": "0", "credit": "100.00"},
                    {"account": "391", "debit": "0", "credit": "20.00"},
                ]
            }
        )
        self.assertTrue(result["balanced"])
        self.assertEqual(result["total_debit"], Decimal("120.00"))

    def test_float_is_rejected(self) -> None:
        with self.assertRaises(engine.InputError):
            engine.vat({"amount": 100.5, "rate": "0.20"})

    def test_straight_line_rounding_closes(self) -> None:
        result = engine.straight_line_depreciation(
            {"cost": "1000", "residual_value": "100", "life_periods": 3}
        )
        self.assertEqual([row["depreciation"] for row in result["schedule"]], [Decimal("300.00")] * 3)
        self.assertTrue(result["invariants"]["closing_equals_residual_value"])

    def test_present_value(self) -> None:
        result = engine.present_value({"rate": "0.10", "cashflows": [{"period": 1, "amount": "110"}]})
        self.assertEqual(result["present_value"], Decimal("100.00"))

    def test_weighted_average_inventory(self) -> None:
        result = engine.weighted_average_inventory(
            {
                "opening_quantity": "10",
                "opening_unit_cost": "100",
                "transactions": [
                    {"type": "purchase", "quantity": "10", "unit_cost": "120"},
                    {"type": "sale", "quantity": "5"},
                ],
            }
        )
        self.assertEqual(result["cost_of_goods_sold"], Decimal("550.00"))
        self.assertEqual(result["ending_inventory_cost"], Decimal("1650.00"))

    def test_fifo_inventory(self) -> None:
        result = engine.fifo_inventory(
            {
                "opening_layers": [{"quantity": "10", "unit_cost": "100"}],
                "transactions": [
                    {"type": "purchase", "quantity": "10", "unit_cost": "120"},
                    {"type": "sale", "quantity": "12"},
                ],
            }
        )
        self.assertEqual(result["cost_of_goods_sold"], Decimal("1240.00"))
        self.assertEqual(result["ending_inventory_cost"], Decimal("960.00"))

    def test_vat_inclusive(self) -> None:
        result = engine.vat({"amount": "120", "rate": "0.20", "inclusive": True})
        self.assertEqual(result["net_amount"], Decimal("100.00"))
        self.assertEqual(result["tax_amount"], Decimal("20.00"))
        self.assertTrue(result["invariants"]["net_plus_tax_equals_gross"])

    def test_tax_reconciliation(self) -> None:
        result = engine.tax_reconciliation(
            {
                "accounting_profit": "1000",
                "additions": [{"description": "A", "amount": "100"}],
                "deductions": [{"description": "B", "amount": "50"}],
                "loss_carryforwards_used": "0",
                "tax_rate": "0.25",
                "tax_credits": "0",
            }
        )
        self.assertEqual(result["taxable_income"], Decimal("1050.00"))
        self.assertEqual(result["net_tax"], Decimal("262.50"))

    def test_day_count(self) -> None:
        result = engine.day_count({"start_date": "2026-01-01", "end_date": "2026-02-01"})
        self.assertEqual(result["day_count"], 31)


class IngestTests(unittest.TestCase):
    def test_manifest_download_timeout_validation(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            manifest = root / "manifest.json"
            payload = {
                "as_of_date": "2026-08-02",
                "download_timeout_seconds": 300,
                "documents": [
                    {
                        "uri": "source.txt",
                        "authority": "Test",
                        "title": "Zaman aşımı testi",
                        "document_type": "working_paper",
                        "publication_date": None,
                        "effective_from": None,
                        "effective_to": None,
                        "status": "unknown",
                        "tags": ["test"],
                        "scope": "case",
                    }
                ],
            }
            manifest.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
            self.assertEqual(ingest_sources.load_manifest(manifest)["download_timeout_seconds"], 300)
            payload["download_timeout_seconds"] = 0
            manifest.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
            with self.assertRaises(ingest_sources.IngestError):
                ingest_sources.load_manifest(manifest)

    def test_local_ingest_duplicate_audit_and_mask(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "source.txt"
            source.write_text("VUK amortisman örneği 12345678901\n", encoding="utf-8")
            manifest = root / "manifest.json"
            manifest.write_text(
                json.dumps(
                    {
                        "as_of_date": "2026-07-21",
                        "documents": [
                            {
                                "uri": "source.txt",
                                "authority": "Test",
                                "title": "Yerel test",
                                "document_type": "working_paper",
                                "publication_date": None,
                                "effective_from": None,
                                "effective_to": None,
                                "status": "unknown",
                                "tags": ["test"],
                                "scope": "case",
                            }
                        ],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            corpus = root / "corpus"
            first = ingest_sources.command_ingest(manifest, corpus)
            second = ingest_sources.command_ingest(manifest, corpus)
            audit = ingest_sources.command_audit(corpus)
            self.assertTrue(first["ok"])
            self.assertEqual(first["ingested"], 1)
            self.assertEqual(second["duplicates"], 1)
            self.assertTrue(audit["ok"])
            self.assertEqual(audit["latest_uri_count"], 1)
            self.assertEqual(audit["latest_extraction_status_counts"], {"low_text": 1})
            self.assertEqual(query_corpus.mask("12345678901"), "[MASKED_TCKN]")

    def test_new_as_of_date_creates_verification_version(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "source.txt"
            source.write_text("Aynı resmî belge içeriği\n", encoding="utf-8")
            manifest = root / "manifest.json"
            payload = {
                "as_of_date": "2026-07-21",
                "documents": [
                    {
                        "uri": "source.txt",
                        "authority": "Test",
                        "title": "Sürüm testi",
                        "document_type": "law",
                        "publication_date": None,
                        "effective_from": None,
                        "effective_to": None,
                        "status": "in_force",
                        "tags": ["test"],
                        "scope": "case",
                    }
                ],
            }
            manifest.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
            corpus = root / "corpus"
            first = ingest_sources.command_ingest(manifest, corpus)
            payload["as_of_date"] = "2026-08-02"
            manifest.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
            second = ingest_sources.command_ingest(manifest, corpus)
            records = ingest_sources.load_index(corpus / "index.jsonl")
            self.assertEqual(first["ingested"], 1)
            self.assertEqual(second["ingested"], 1)
            self.assertEqual(records[0]["blob_sha256"], records[1]["blob_sha256"])
            self.assertEqual(records[1]["supersedes"], records[0]["record_id"])
            self.assertEqual(records[1]["as_of_date"], "2026-08-02")

    def test_new_extraction_creates_enriched_version(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "source.bin"
            source.write_bytes(b"binary source")
            manifest = root / "manifest.json"
            payload = {
                "as_of_date": "2026-08-02",
                "documents": [
                    {
                        "uri": "source.bin",
                        "authority": "Test",
                        "title": "Çıkarım testi",
                        "document_type": "working_paper",
                        "publication_date": None,
                        "effective_from": None,
                        "effective_to": None,
                        "status": "unknown",
                        "tags": ["test"],
                        "scope": "case",
                    }
                ],
            }
            manifest.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
            corpus = root / "corpus"
            first = ingest_sources.command_ingest(manifest, corpus)
            original_extract = ingest_sources.extract_text
            try:
                ingest_sources.extract_text = lambda data, extension, content_type: (
                    "Yerel çıkarılmış metin\n",
                    "extracted",
                    "test-extractor",
                )
                second = ingest_sources.command_ingest(manifest, corpus)
            finally:
                ingest_sources.extract_text = original_extract
            records = ingest_sources.load_index(corpus / "index.jsonl")
            self.assertEqual(first["results"][0]["extraction_status"], "unsupported")
            self.assertEqual(second["ingested"], 1)
            self.assertEqual(records[1]["supersedes"], records[0]["record_id"])
            self.assertIsNotNone(records[1]["text_sha256"])

    def test_local_xlsx_is_extracted_without_formula_execution(self) -> None:
        try:
            from openpyxl import Workbook  # type: ignore
        except ImportError:
            self.skipTest("openpyxl is not installed")
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "mizan.xlsx"
            workbook = Workbook()
            sheet = workbook.active
            sheet.title = "Mizan"
            sheet.append(["Hesap", "Borç", "Alacak", "Kontrol"])
            sheet.append(["100", "1250.50", "0", "=B2-C2"])
            workbook.save(source)
            manifest = root / "manifest.json"
            manifest.write_text(
                json.dumps(
                    {
                        "as_of_date": "2026-08-02",
                        "documents": [
                            {
                                "uri": "mizan.xlsx",
                                "authority": "Müşteri",
                                "title": "Mizan",
                                "document_type": "trial_balance",
                                "publication_date": None,
                                "effective_from": None,
                                "effective_to": None,
                                "status": "unknown",
                                "tags": ["mizan"],
                                "scope": "case",
                            }
                        ],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            corpus = root / "corpus"
            result = ingest_sources.command_ingest(manifest, corpus)
            record = ingest_sources.load_index(corpus / "index.jsonl")[0]
            extracted = (corpus / record["text_path"]).read_text(encoding="utf-8")
            self.assertTrue(result["ok"])
            self.assertEqual(record["extractor"], "openpyxl-no-formula-evaluation")
            self.assertIn("=B2-C2", extracted)
            self.assertIn("1250.50", extracted)

    def test_case_scope_rejects_network(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            document = {
                "uri": "https://example.com/test.pdf",
                "scope": "case",
            }
            with self.assertRaises(ingest_sources.IngestError):
                ingest_sources.fetch_document(document, root, {"example.com"})


class WorkflowTests(unittest.TestCase):
    def test_case_gates_and_finalize(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            case_dir = Path(temp_dir) / "case"
            case_workflow.init_case(case_dir, "ornek-vaka", "2026-07-21")
            initial = case_workflow.check_case(case_dir)
            self.assertFalse(initial["ready_for_professional_review"])

            facts = json.loads((case_dir / "facts.json").read_text(encoding="utf-8"))
            facts.update(
                {
                    "period_start": "2026-01-01",
                    "period_end": "2026-12-31",
                    "entity_type": "limited_company",
                    "purpose": "period_end",
                    "reporting_framework": "MSUGT",
                    "materiality": "1000",
                }
            )
            case_workflow.write_json(case_dir / "facts.json", facts)
            case_workflow.write_json(
                case_dir / "sources.json",
                {
                    "sources": [
                        {
                            "authority": "GİB",
                            "title": "Test kaynak",
                            "url": "https://gib.gov.tr/",
                            "status": "in_force",
                            "accessed_at": "2026-07-21",
                            "pinpoint": "Madde 1",
                            "supports_conclusion": True,
                        }
                    ]
                },
            )
            (case_dir / "workpapers" / "analysis.md").write_text("# Analysis\n\nOlgu → hüküm → değerlendirme → sonuç.\n", encoding="utf-8")
            calculation = engine.envelope("vat", {"amount": "120", "rate": "0.20", "inclusive": True}, engine.vat({"amount": "120", "rate": "0.20", "inclusive": True}))
            case_workflow.write_json(case_dir / "calculations" / "result-vat.json", calculation)
            final = case_workflow.finalize_case(case_dir)
            self.assertTrue(final["finalized"])
            self.assertEqual(json.loads((case_dir / "case.json").read_text(encoding="utf-8"))["status"], "ready_for_professional_review")


class StandardManifestTests(unittest.TestCase):
    def test_selected_2026_standards_have_official_urls(self) -> None:
        result = prepare_2026_tfrs_manifest.build_manifest(
            ["TMS-16", "TFRS 15", "TMS_2", "TMS-16"],
            "2026-08-02",
        )
        documents = result["documents"]
        self.assertEqual(len(documents), 3)
        self.assertTrue(all(item["authority"] == "KGK" for item in documents))
        self.assertTrue(all(item["uri"].startswith("https://www.kgk.gov.tr/") for item in documents))
        self.assertTrue(any(item["uri"].endswith("TMS%2016.pdf") for item in documents))

    def test_unknown_2026_standard_is_rejected(self) -> None:
        with self.assertRaises(prepare_2026_tfrs_manifest.CatalogError):
            prepare_2026_tfrs_manifest.build_manifest(["TMS-99"], "2026-08-02")


if __name__ == "__main__":
    unittest.main(verbosity=2)

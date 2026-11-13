import tempfile
import unittest
from pathlib import Path

from pypdf import PdfReader
from pypdf.errors import PdfReadError

from planner.assumptions import Assumptions
from planner.projection.scenario_projection_workflow import ScenarioProjectionApplication
from planner.reporting.report_pack import export_report_pack
from planner.reporting.report_suite import export_report_suite


class Sprint300ReportArtefactIntegrityTests(unittest.TestCase):
    def _suite(self, directory):
        workflow = ScenarioProjectionApplication(Assumptions()).run_report_workflow(
            allocations={"Aviva": 1.0},
            fund_returns={"Aviva": [0.05, 0.05, 0.05]},
        )
        return export_report_suite(
            assumptions=Assumptions(),
            scenario_result=workflow,
            allocations={"Aviva": 1.0},
            fund_returns={"Aviva": [0.05, 0.05, 0.05]},
            directory=directory,
            monte_carlo_iterations=2,
            monte_carlo_seed=1,
        )

    def _normalise(self, value):
        return " ".join(value.split())

    def test_real_report_suite_contains_five_valid_nonempty_searchable_pdfs(self):
        expected = {
            "scenario_projection": "retirement_scenario_projection.pdf",
            "strategy_comparison": "retirement_strategy_comparison.pdf",
            "recommendation": "retirement_recommendation.pdf",
            "health_check": "retirement_health_check.pdf",
            "retirement_goals": "retirement_goals.pdf",
        }
        with tempfile.TemporaryDirectory() as directory:
            suite = self._suite(directory)

            self.assertEqual(tuple(suite.paths), tuple(expected))
            for key, filename in expected.items():
                with self.subTest(report=key):
                    path = suite.paths[key]
                    self.assertEqual(path.name, filename)
                    self.assertTrue(path.is_file())
                    self.assertGreater(path.stat().st_size, 1000)
                    self.assertTrue(path.read_bytes().startswith(b"%PDF-"))

                    reader = PdfReader(path)
                    self.assertGreater(len(reader.pages), 0)
                    extracted = self._normalise(
                        " ".join(page.extract_text() or "" for page in reader.pages)
                    )
                    self.assertTrue(extracted, f"{filename} contains no searchable text")

    def test_real_report_pack_preserves_content_from_every_source_report(self):
        with tempfile.TemporaryDirectory() as directory:
            suite = self._suite(directory)
            source_text = {}
            source_pages = 0
            for key, path in suite.paths.items():
                reader = PdfReader(path)
                source_pages += len(reader.pages)
                source_text[key] = self._normalise(
                    " ".join(page.extract_text() or "" for page in reader.pages)
                )
                self.assertTrue(source_text[key])

            output = Path(directory) / "RetirementPlanner_Report_Pack.pdf"
            result = export_report_pack(suite, output)
            self.assertEqual(result.path, output)
            self.assertTrue(output.is_file())
            self.assertGreater(output.stat().st_size, 1000)
            self.assertTrue(output.read_bytes().startswith(b"%PDF-"))

            packed = PdfReader(output)
            self.assertEqual(len(packed.pages), source_pages + 1)
            packed_text = self._normalise(
                " ".join(page.extract_text() or "" for page in packed.pages)
            )
            for key, text in source_text.items():
                with self.subTest(report=key):
                    # The first 100 extracted characters are a stable content
                    # fingerprint without coupling the test to full report wording.
                    self.assertIn(text[:100], packed_text)

            self.assertFalse(output.with_name(f".{output.name}.tmp").exists())

    def test_corrupt_source_pdf_prevents_report_pack_publication(self):
        with tempfile.TemporaryDirectory() as directory:
            suite = self._suite(directory)
            suite.paths["health_check"].write_bytes(b"not a valid PDF")

            output = Path(directory) / "must_not_be_published.pdf"
            with self.assertRaises(PdfReadError):
                export_report_pack(suite, output)

            self.assertFalse(output.exists())
            self.assertFalse(output.with_name(f".{output.name}.tmp").exists())


if __name__ == "__main__":
    unittest.main()

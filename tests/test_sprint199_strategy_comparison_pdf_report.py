import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from pypdf import PdfReader

from planner.assumptions import Assumptions
from planner.scenario_engine import ScenarioEngine
from reports.strategy_comparison_pdf_report import StrategyComparisonPDFReport


class Sprint199StrategyComparisonPDFReportTests(unittest.TestCase):
    def make_results(self):
        return ScenarioEngine(assumptions=Assumptions()).compare_strategies()

    def test_pdf_contains_both_precomputed_strategies_and_key_fields(self):
        with tempfile.TemporaryDirectory() as directory:
            path = StrategyComparisonPDFReport().create(
                self.make_results(), Path(directory) / "comparison.pdf"
            )
            text = "\n".join(page.extract_text() or "" for page in PdfReader(path).pages)

        self.assertIn("Strategy Comparison Report", text)
        self.assertIn("PENSION_FIRST", text)
        self.assertIn("ISA_FIRST", text)
        self.assertIn("Ending assets", text)
        self.assertIn("Lifetime Tax", text)
        self.assertIn("Year-by-Year Strategy Detail", text)
        self.assertIn("2054", text)

    def test_pdf_renderer_uses_supplied_results_without_recalculation(self):
        results = self.make_results()
        expected = {result.name: dict(result.summary) for result in results}
        with tempfile.TemporaryDirectory() as directory:
            StrategyComparisonPDFReport().create(results, Path(directory) / "comparison.pdf")
        self.assertEqual(expected, {result.name: result.summary for result in results})


    def test_compare_cli_can_export_the_same_computed_results_to_pdf(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "comparison.pdf"
            completed = subprocess.run(
                [sys.executable, "compare.py", "--pdf", str(path)],
                capture_output=True,
                text=True,
                timeout=60,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertIn("PDF comparison report exported", completed.stdout)
            self.assertTrue(path.exists())
            text = "\n".join(page.extract_text() or "" for page in PdfReader(path).pages)
            self.assertIn("PENSION_FIRST", text)
            self.assertIn("ISA_FIRST", text)

    def test_invalid_comparison_inputs_are_rejected(self):
        report = StrategyComparisonPDFReport()
        with self.assertRaises(ValueError):
            report.create([])
        with self.assertRaises(TypeError):
            report.create([object()])


if __name__ == "__main__":
    unittest.main()

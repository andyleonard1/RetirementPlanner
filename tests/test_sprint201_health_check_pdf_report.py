import copy
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from pypdf import PdfReader

from reports.health_check_pdf_report import HealthCheckPDFReport


class Sprint201HealthCheckPDFReportTests(unittest.TestCase):
    def setUp(self):
        self.health = {
            "score": 8.7,
            "rating": "VERY GOOD",
            "reasons": ["Pension fund remains positive", "Cash savings remain positive"],
        }
        self.recommendation = {"strategy": "PENSION_FIRST", "confidence": "HIGH"}
        self.monte_carlo = SimpleNamespace(
            iterations=5000,
            minimum=125000,
            percentile_5=280000,
            median=650000,
            percentile_95=1100000,
            maximum=1450000,
            success_rate=97.4,
        )
        self.summary = {
            "ending_assets": 650000,
            "ending_pension": 200000,
            "ending_isa": 300000,
            "ending_savings": 150000,
            "total_tax": 72000,
        }

    def test_pdf_contains_dashboard_and_outcome_sections(self):
        with tempfile.TemporaryDirectory() as directory:
            path = HealthCheckPDFReport().create(
                self.health,
                self.recommendation,
                self.monte_carlo,
                self.summary,
                Path(directory) / "health.pdf",
            )
            text = "\n".join(page.extract_text() or "" for page in PdfReader(path).pages)
        self.assertIn("Health Check Report", text)
        self.assertIn("Executive Dashboard", text)
        self.assertIn("Projected Position", text)
        self.assertIn("Monte Carlo Outcome Range", text)
        self.assertIn("Key Strengths / Findings", text)
        self.assertIn("97.4%", text)

    def test_pdf_renderer_does_not_mutate_supplied_data(self):
        before = (repr(copy.deepcopy(self.health)), repr(copy.deepcopy(self.recommendation)), repr(self.monte_carlo), repr(copy.deepcopy(self.summary)))
        with tempfile.TemporaryDirectory() as directory:
            HealthCheckPDFReport().create(
                self.health, self.recommendation, self.monte_carlo, self.summary,
                Path(directory) / "health.pdf",
            )
        after = (repr(self.health), repr(self.recommendation), repr(self.monte_carlo), repr(self.summary))
        self.assertEqual(before, after)

    def test_health_check_cli_can_export_pdf(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "health.pdf"
            completed = subprocess.run(
                [sys.executable, "health_check.py", "--pdf", str(path)],
                capture_output=True,
                text=True,
                timeout=120,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertIn("PDF health report exported", completed.stdout)
            self.assertTrue(path.exists())
            self.assertGreater(len(PdfReader(path).pages), 0)


if __name__ == "__main__":
    unittest.main()

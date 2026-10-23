import copy
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from pypdf import PdfReader

from reports.goal_pdf_report import GoalPDFReport


class Sprint202GoalPDFReportTests(unittest.TestCase):
    def setUp(self):
        self.goals = [
            {"name": "Estate value", "passed": True, "target": 500000, "actual": 650000},
            {"name": "Monte Carlo success", "passed": True, "target": 90.0, "actual": 97.4},
            {"name": "Pension remains positive", "passed": False, "target": 0, "actual": -12000},
        ]

    def test_pdf_contains_goal_summary_and_detail(self):
        with tempfile.TemporaryDirectory() as directory:
            path = GoalPDFReport().create(self.goals, Path(directory) / "goals.pdf")
            text = "\n".join(page.extract_text() or "" for page in PdfReader(path).pages)
        self.assertIn("Retirement Goals Report", text)
        self.assertIn("Goals Summary", text)
        self.assertIn("Goal Status", text)
        self.assertIn("Estate value", text)
        self.assertIn("ACHIEVED", text)
        self.assertIn("NOT ACHIEVED", text)
        self.assertIn("2 of 3 goals achieved", text)

    def test_pdf_renderer_does_not_mutate_supplied_goals(self):
        before = copy.deepcopy(self.goals)
        with tempfile.TemporaryDirectory() as directory:
            GoalPDFReport().create(self.goals, Path(directory) / "goals.pdf")
        self.assertEqual(self.goals, before)

    def test_health_check_cli_can_export_goals_pdf(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "goals.pdf"
            completed = subprocess.run(
                [sys.executable, "health_check.py", "--goals-pdf", str(path)],
                capture_output=True,
                text=True,
                timeout=120,
                cwd=Path(__file__).resolve().parents[1],
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertIn("PDF goals report exported", completed.stdout)
            self.assertTrue(path.exists())
            self.assertGreater(len(PdfReader(path).pages), 0)


if __name__ == "__main__":
    unittest.main()

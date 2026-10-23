import copy
import tempfile
import unittest
from pathlib import Path

from pypdf import PdfReader

from reports.goal_pdf_report import GoalPDFReport


class Sprint222GoalConstraintReportTests(unittest.TestCase):
    def test_pdf_presents_explicit_goal_operator(self):
        goals = [
            {
                "name": "Estate value",
                "passed": True,
                "target": 500000,
                "actual": 650000,
                "operator": ">=",
                "enabled": True,
            },
            {
                "name": "Pension threshold",
                "passed": False,
                "target": 100000,
                "actual": 90000,
                "operator": "<",
                "enabled": True,
            },
        ]
        with tempfile.TemporaryDirectory() as directory:
            path = GoalPDFReport().create(goals, Path(directory) / "goals.pdf")
            extracted = "\n".join(page.extract_text() or "" for page in PdfReader(path).pages)
        self.assertIn("Constraint", extracted)
        self.assertIn(">=", extracted)
        self.assertIn("<", extracted)

    def test_legacy_goal_result_without_operator_remains_renderable(self):
        goals = [{"name": "Legacy goal", "passed": True, "target": 10, "actual": 10}]
        with tempfile.TemporaryDirectory() as directory:
            path = GoalPDFReport().create(goals, Path(directory) / "goals.pdf")
            self.assertTrue(path.exists())

    def test_goal_report_does_not_recalculate_constraint(self):
        goals = [{"name": "Custom", "passed": True, "target": 10, "actual": 3, "operator": "!=", "enabled": True}]
        before = copy.deepcopy(goals)
        with tempfile.TemporaryDirectory() as directory:
            GoalPDFReport().create(goals, Path(directory) / "goals.pdf")
        self.assertEqual(goals, before)

    def test_empty_goal_result_keeps_safe_table_shape(self):
        with tempfile.TemporaryDirectory() as directory:
            path = GoalPDFReport().create([], Path(directory) / "goals.pdf")
            extracted = "\n".join(page.extract_text() or "" for page in PdfReader(path).pages)
        self.assertIn("No goals were evaluated.", extracted)


if __name__ == "__main__":
    unittest.main()

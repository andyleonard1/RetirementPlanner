import io
import unittest
from contextlib import redirect_stdout

from reports.goal_report import GoalReport


class Sprint223GoalConstraintConsoleTests(unittest.TestCase):
    def _render(self, goals):
        output = io.StringIO()
        with redirect_stdout(output):
            GoalReport().print(goals)
        return output.getvalue()

    def test_console_presents_explicit_operator(self):
        output = self._render([{
            "name": "Estate value",
            "passed": True,
            "target": 500000,
            "actual": 650000,
            "operator": ">=",
            "enabled": True,
        }])
        self.assertIn("Constraint: >= 500000", output)

    def test_console_supports_all_custom_operator_text(self):
        for operator in (">", "<", "<=", "==", "!="):
            output = self._render([{
                "name": "Constraint",
                "passed": True,
                "target": 10,
                "actual": 10,
                "operator": operator,
            }])
            self.assertIn(f"Constraint: {operator} 10", output)

    def test_legacy_goal_without_operator_remains_renderable(self):
        output = self._render([{
            "name": "Legacy goal",
            "passed": True,
            "target": 10,
            "actual": 10,
        }])
        self.assertIn("Target    : 10", output)
        self.assertIn("Actual    : 10", output)
        self.assertNotIn("Constraint:  10", output)


if __name__ == "__main__":
    unittest.main()

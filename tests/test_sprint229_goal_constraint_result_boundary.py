import math
import unittest

from planner.goal_engine import GoalEngine


class TestSprint229GoalConstraintResultBoundary(unittest.TestCase):
    def _engine(self, goals):
        class AssumptionsStub:
            def __init__(self):
                self.data = {
                    "goals": goals,
                    "retirement_age": 63,
                    "spending_phase_3": 28000,
                }

            def get(self, key):
                return self.data[key]

        return GoalEngine(AssumptionsStub())

    def test_non_numeric_estate_actual_has_clear_error(self):
        goal = {"name": "Estate", "type": "estate", "target": 500000}
        with self.assertRaisesRegex(ValueError, r"goals\[0\] actual value must be a finite number"):
            self._engine([goal]).evaluate({"ending_assets": "600000"}, None, [])

    def test_non_finite_estate_actual_has_clear_error(self):
        goal = {"name": "Estate", "type": "estate", "target": 500000}
        with self.assertRaisesRegex(ValueError, r"goals\[0\] actual value must be a finite number"):
            self._engine([goal]).evaluate({"ending_assets": math.inf}, None, [])

    def test_boolean_estate_actual_has_clear_error(self):
        goal = {"name": "Estate", "type": "estate", "target": 500000}
        with self.assertRaisesRegex(ValueError, r"goals\[0\] actual value must be a finite number"):
            self._engine([goal]).evaluate({"ending_assets": True}, None, [])

    def test_non_numeric_monte_carlo_actual_has_clear_error(self):
        goal = {"name": "Success", "type": "monte_carlo", "target": 90}
        class MonteCarlo:
            success_rate = "90"
        with self.assertRaisesRegex(ValueError, r"goals\[0\] actual value must be a finite number"):
            self._engine([goal]).evaluate({}, MonteCarlo(), [])

    def test_empty_timeline_spending_goal_has_clear_error(self):
        goal = {"name": "Spending", "type": "spending", "target": 28000}
        with self.assertRaisesRegex(ValueError, r"goals\[0\] spending goal requires a non-empty timeline"):
            self._engine([goal]).evaluate({}, None, [])

    def test_valid_numeric_actuals_remain_unchanged(self):
        goals = [
            {"name": "Estate", "type": "estate", "target": 500000},
            {"name": "Spending", "type": "spending", "target": 28000},
        ]
        timeline = [type("Year", (), {"target_spending": 28000})()]
        result = self._engine(goals).evaluate({"ending_assets": 600000}, None, timeline)
        self.assertEqual(result[0]["actual"], 600000)
        self.assertEqual(result[1]["actual"], 28000)


if __name__ == "__main__":
    unittest.main()

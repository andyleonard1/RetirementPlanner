import unittest

from planner.goal_engine import GoalEngine


class TestSprint227GoalConstraintEvaluationBoundary(unittest.TestCase):
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

    def test_required_estate_target_is_validated_at_engine_boundary(self):
        with self.assertRaisesRegex(ValueError, "target is required"):
            self._engine([{"name": "Estate", "type": "estate"}]).evaluate(
                {"ending_assets": 500000}, None, []
            )

    def test_required_monte_carlo_target_is_validated_at_engine_boundary(self):
        with self.assertRaisesRegex(ValueError, "target is required"):
            self._engine([{"name": "Success", "type": "monte_carlo"}]).evaluate(
                {}, type("MC", (), {"success_rate": 95})(), []
            )

    def test_invalid_direct_call_operator_has_clear_error(self):
        goal = {
            "name": "Estate",
            "type": "estate",
            "target": 500000,
            "operator": "~",
        }
        with self.assertRaisesRegex(ValueError, "operator must be one of"):
            self._engine([goal]).evaluate({"ending_assets": 500000}, None, [])

    def test_invalid_direct_call_target_has_clear_error(self):
        goal = {
            "name": "Minimum pension",
            "type": "pension_positive",
            "target": "10000",
        }
        with self.assertRaisesRegex(ValueError, "target must be a finite number"):
            self._engine([goal]).evaluate({"ending_pension": 12000}, None, [])

    def test_valid_existing_goal_configuration_is_unchanged(self):
        goals = [
            {"name": "Estate", "type": "estate", "target": 500000},
            {"name": "Pension", "type": "pension_positive"},
        ]
        result = self._engine(goals).evaluate(
            {"ending_assets": 600000, "ending_pension": 1}, None, []
        )
        self.assertEqual(result[0]["operator"], ">=")
        self.assertEqual(result[0]["target"], 500000)
        self.assertEqual(result[1]["target"], 0)

    def test_disabled_invalid_goal_remains_skipped(self):
        goal = {
            "name": "Disabled",
            "type": "estate",
            "enabled": False,
            "operator": "~",
        }
        self.assertEqual(
            self._engine([goal]).evaluate({"ending_assets": 1}, None, []), []
        )


if __name__ == "__main__":
    unittest.main()

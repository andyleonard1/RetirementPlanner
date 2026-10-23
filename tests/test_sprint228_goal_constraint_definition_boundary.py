import unittest

from planner.goal_engine import GoalEngine


class TestSprint228GoalConstraintDefinitionBoundary(unittest.TestCase):
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

    def test_non_object_goal_has_clear_error(self):
        with self.assertRaisesRegex(ValueError, r"goals\[0\] must be an object"):
            self._engine(["bad"]).evaluate({"ending_assets": 1}, None, [])

    def test_missing_name_has_clear_error(self):
        goal = {"type": "estate", "target": 500000}
        with self.assertRaisesRegex(ValueError, r"goals\[0\]\.name must be a non-empty string"):
            self._engine([goal]).evaluate({"ending_assets": 600000}, None, [])

    def test_blank_name_has_clear_error(self):
        goal = {"name": "  ", "type": "estate", "target": 500000}
        with self.assertRaisesRegex(ValueError, r"goals\[0\]\.name must be a non-empty string"):
            self._engine([goal]).evaluate({"ending_assets": 600000}, None, [])

    def test_missing_type_has_clear_error(self):
        goal = {"name": "Estate", "target": 500000}
        with self.assertRaisesRegex(ValueError, r"goals\[0\]\.type must be a non-empty string"):
            self._engine([goal]).evaluate({"ending_assets": 600000}, None, [])

    def test_invalid_enabled_has_clear_error(self):
        goal = {"name": "Estate", "type": "estate", "target": 500000, "enabled": "yes"}
        with self.assertRaisesRegex(ValueError, r"goals\[0\]\.enabled must be a boolean"):
            self._engine([goal]).evaluate({"ending_assets": 600000}, None, [])

    def test_valid_unknown_type_remains_skipped(self):
        goal = {"name": "Future goal", "type": "future_constraint"}
        self.assertEqual(
            self._engine([goal]).evaluate({"ending_assets": 600000}, None, []),
            [],
        )

    def test_disabled_well_formed_unknown_type_remains_skipped(self):
        goal = {"name": "Disabled", "type": "future_constraint", "enabled": False}
        self.assertEqual(
            self._engine([goal]).evaluate({"ending_assets": 600000}, None, []),
            [],
        )


if __name__ == "__main__":
    unittest.main()

import unittest

from planner.goal_engine import GoalEngine


class TestSprint226GoalConstraintTargetSemantics(unittest.TestCase):
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

    def test_retirement_age_goal_honours_explicit_target(self):
        goals = [{"name": "Retire at 65", "type": "retirement_age", "target": 65}]
        result = self._engine(goals).evaluate({}, None, [])
        self.assertEqual(result[0]["target"], 65)
        self.assertFalse(result[0]["passed"])
        self.assertEqual(result[0]["operator"], "==")

    def test_retirement_age_goal_without_target_preserves_legacy_target(self):
        goals = [{"name": "Retire at planned age", "type": "retirement_age"}]
        result = self._engine(goals).evaluate({}, None, [])
        self.assertEqual(result[0]["target"], 63)
        self.assertTrue(result[0]["passed"])

    def test_pension_positive_goal_honours_explicit_target(self):
        goals = [{"name": "Minimum pension", "type": "pension_positive", "target": 10000, "operator": ">="}]
        result = self._engine(goals).evaluate({"ending_pension": 12000}, None, [])
        self.assertEqual(result[0]["target"], 10000)
        self.assertTrue(result[0]["passed"])

    def test_spending_goal_honours_explicit_target(self):
        class Year:
            target_spending = 30000

        goals = [{"name": "Minimum spending", "type": "spending", "target": 31000}]
        result = self._engine(goals).evaluate({}, None, [Year()])
        self.assertEqual(result[0]["target"], 31000)
        self.assertFalse(result[0]["passed"])

    def test_existing_default_targets_remain_unchanged(self):
        class Year:
            target_spending = 30000

        goals = [
            {"name": "Pension positive", "type": "pension_positive"},
            {"name": "Spending", "type": "spending"},
        ]
        result = self._engine(goals).evaluate({"ending_pension": 1}, None, [Year()])
        self.assertEqual(result[0]["target"], 0)
        self.assertEqual(result[1]["target"], 28000)


if __name__ == "__main__":
    unittest.main()

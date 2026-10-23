import unittest
from types import SimpleNamespace

from planner.assumptions import Assumptions
from planner.assumptions_schema import AssumptionsSchema
from planner.goal_engine import GoalEngine


class TestSprint221GoalConstraints(unittest.TestCase):
    def _engine(self, goals):
        a = Assumptions()
        a.set("goals", goals)
        return GoalEngine(a)

    def test_default_goal_operator_preserves_legacy_estate_semantics(self):
        result = self._engine([{"name": "Estate", "type": "estate", "target": 100}]).evaluate(
            {"ending_assets": 100}, SimpleNamespace(success_rate=0), [],
        )
        self.assertTrue(result[0]["passed"])
        self.assertEqual(result[0]["operator"], ">=")

    def test_custom_less_than_operator_is_applied(self):
        result = self._engine([{"name": "Estate", "type": "estate", "target": 100, "operator": "<"}]).evaluate(
            {"ending_assets": 90}, SimpleNamespace(success_rate=0), [],
        )
        self.assertTrue(result[0]["passed"])

    def test_custom_equality_operator_is_applied(self):
        result = self._engine([{"name": "Estate", "type": "estate", "target": 100, "operator": "=="}]).evaluate(
            {"ending_assets": 100}, SimpleNamespace(success_rate=0), [],
        )
        self.assertTrue(result[0]["passed"])

    def test_disabled_goal_is_not_evaluated(self):
        result = self._engine([{"name": "Estate", "type": "estate", "target": 100000, "enabled": False}]).evaluate(
            {"ending_assets": 0}, SimpleNamespace(success_rate=0), [],
        )
        self.assertEqual(result, [])

    def test_enabled_goal_is_explicit_in_result(self):
        result = self._engine([{"name": "Estate", "type": "estate", "target": 100, "enabled": True}]).evaluate(
            {"ending_assets": 100}, SimpleNamespace(success_rate=0), [],
        )
        self.assertTrue(result[0]["enabled"])

    def test_schema_rejects_non_boolean_enabled(self):
        a = Assumptions().data
        a["goals"][0]["enabled"] = "yes"
        with self.assertRaisesRegex(ValueError, r"goals\[0\]\.enabled"):
            AssumptionsSchema.validate(a)

    def test_schema_rejects_invalid_operator(self):
        a = Assumptions().data
        a["goals"][0]["operator"] = "~="
        with self.assertRaisesRegex(ValueError, r"goals\[0\]\.operator"):
            AssumptionsSchema.validate(a)

    def test_legacy_goal_without_new_fields_remains_compatible(self):
        result = self._engine([{"name": "Pension", "type": "pension_positive"}]).evaluate(
            {"ending_pension": 1}, SimpleNamespace(success_rate=0), [],
        )
        self.assertTrue(result[0]["passed"])
        self.assertEqual(result[0]["operator"], ">")


if __name__ == "__main__":
    unittest.main()

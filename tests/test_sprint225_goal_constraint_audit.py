import unittest

from planner.audit_catalog import description, has_description


class TestSprint225GoalConstraintAudit(unittest.TestCase):
    def test_enabled_goal_path_has_explicit_audit_description(self):
        path = "goals[0].enabled"
        self.assertTrue(has_description(path))
        self.assertEqual(
            description(path),
            "Retirement goal enabled setting changed for this projection.",
        )

    def test_operator_goal_path_has_explicit_audit_description(self):
        path = "goals[0].operator"
        self.assertTrue(has_description(path))
        self.assertEqual(
            description(path),
            "Retirement goal comparison operator changed for this projection.",
        )

    def test_legacy_goal_paths_remain_covered(self):
        for field in ("target", "name", "type"):
            self.assertTrue(has_description(f"goals[2].{field}"))

    def test_unknown_nested_goal_path_remains_generic(self):
        path = "goals[1].future_field"
        self.assertFalse(has_description(path))
        self.assertEqual(
            description(path),
            "Retirement goal configuration changed for this projection.",
        )

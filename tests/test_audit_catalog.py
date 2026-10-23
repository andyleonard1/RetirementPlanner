import unittest

from planner.audit_catalog import DESCRIPTIONS, description, has_description, schema_paths


class TestAuditCatalog(unittest.TestCase):
    def test_every_schema_required_key_has_explicit_description(self):
        missing = [path for path in schema_paths() if not has_description(path)]
        self.assertEqual(missing, [])

    def test_catalog_is_stable_and_sorted_by_path(self):
        self.assertEqual(tuple(sorted(DESCRIPTIONS)), tuple(DESCRIPTIONS))

    def test_goal_paths_are_described(self):
        for path in ("goals[0].name", "goals[1].type", "goals[2].target"):
            self.assertTrue(has_description(path))
            self.assertNotIn("Assumption '", description(path))

    def test_unknown_nested_goal_path_has_safe_fallback(self):
        self.assertEqual(
            description("goals[0].future_setting"),
            "Retirement goal configuration changed for this projection.",
        )

    def test_unknown_top_level_path_has_safe_fallback(self):
        self.assertEqual(
            description("future_setting"),
            "Assumption 'future_setting' changed for this projection.",
        )

    def test_retirement_age_context_remains_specialised(self):
        self.assertIn("scenario analysis", description("retirement_age", "scenario"))
        self.assertIn("recommendation solver", description("retirement_age", "recommendation"))
        self.assertIn("analytical comparison", description("retirement_age", "analysis"))

    def test_user_context_uses_catalogue_description(self):
        self.assertEqual(
            description("target_net_income", "user"),
            DESCRIPTIONS["target_net_income"],
        )

    def test_catalogue_does_not_change_schema(self):
        self.assertGreaterEqual(len(schema_paths()), 40)


if __name__ == "__main__":
    unittest.main()

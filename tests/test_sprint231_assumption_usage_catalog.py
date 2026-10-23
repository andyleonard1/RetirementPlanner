import unittest

from planner.assumption_usage_catalog import ROLES, role, schema_paths, unclassified_schema_paths


class Sprint231AssumptionUsageCatalogTests(unittest.TestCase):
    def test_every_schema_assumption_has_an_explicit_role(self):
        self.assertEqual(unclassified_schema_paths(), ())
        self.assertEqual(set(schema_paths()), set(ROLES))

    def test_legacy_aliases_are_explicitly_classified(self):
        self.assertEqual(role("inflation"), "legacy_compatibility")
        self.assertEqual(role("savings_interest"), "legacy_compatibility")
        self.assertEqual(role("pension_growth"), "legacy_compatibility")

    def test_stochastic_and_auxiliary_inputs_are_distinguished(self):
        self.assertEqual(role("expected_return"), "monte_carlo")
        self.assertEqual(role("investment_volatility"), "monte_carlo")
        self.assertEqual(role("inflation_volatility"), "monte_carlo")
        self.assertEqual(role("target_net_income"), "auxiliary")

    def test_goals_are_classified_as_a_domain_boundary(self):
        self.assertEqual(role("goals"), "goals")
        self.assertEqual(role("goals[0].operator"), "goals")


if __name__ == "__main__":
    unittest.main()

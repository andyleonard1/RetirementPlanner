import unittest

from planner.funds.portfolio_scenario_selection import PortfolioScenarioSelector


class PortfolioScenarioSelectionTests(unittest.TestCase):
    def setUp(self):
        self.selector = PortfolioScenarioSelector()
        self.metrics = {"annualised_return": 0.06, "volatility": 0.10}
        self.allocation = (
            ("GB00BRDCMN86:GBP", 0.75),
            ("SKY_NEW_DRAWDOWN_LIFESTYLE", 0.25),
        )

    def test_central_scenario_is_selected(self):
        result = self.selector.build(665000, self.metrics, "central", self.allocation)
        self.assertEqual(result.scenario_name, "central")
        self.assertAlmostEqual(result.expected_return, 0.06)

    def test_conservative_scenario_is_selected(self):
        result = self.selector.build(665000, self.metrics, "conservative", self.allocation)
        self.assertAlmostEqual(result.expected_return, -0.04)

    def test_optimistic_scenario_is_selected(self):
        result = self.selector.build(665000, self.metrics, "optimistic", self.allocation)
        self.assertAlmostEqual(result.expected_return, 0.16)

    def test_scenario_selection_is_case_insensitive(self):
        result = self.selector.build(665000, self.metrics, " CENTRAL ", self.allocation)
        self.assertEqual(result.scenario_name, "central")

    def test_unknown_scenario_is_rejected(self):
        with self.assertRaises(ValueError):
            self.selector.build(665000, self.metrics, "best_case", self.allocation)

    def test_unavailable_scenario_is_rejected(self):
        metrics = {"annualised_return": 0.06, "volatility": None}
        with self.assertRaises(ValueError):
            self.selector.build(665000, metrics, "optimistic", self.allocation)

    def test_central_remains_available_without_volatility(self):
        metrics = {"annualised_return": 0.06, "volatility": None}
        result = self.selector.build(665000, metrics, "central", self.allocation)
        self.assertAlmostEqual(result.expected_return, 0.06)

    def test_available_scenarios_reflect_data(self):
        result = self.selector.available_scenarios(self.metrics)
        self.assertEqual(
            tuple(s.name for s in result),
            ("conservative", "central", "optimistic"),
        )

    def test_available_scenarios_only_central_without_volatility(self):
        result = self.selector.available_scenarios(
            {"annualised_return": 0.06, "volatility": None}
        )
        self.assertEqual(tuple(s.name for s in result), ("central",))

    def test_starting_pension_is_preserved(self):
        result = self.selector.build(660000, self.metrics, "central", self.allocation)
        self.assertEqual(result.starting_pension, 660000)

    def test_allocation_is_preserved(self):
        result = self.selector.build(665000, self.metrics, "central", self.allocation)
        self.assertEqual(result.fund_allocation, self.allocation)

    def test_missing_metric_is_rejected(self):
        with self.assertRaises(ValueError):
            self.selector.build(
                665000,
                {"annualised_return": 0.06},
                "central",
                self.allocation,
            )

    def test_missing_return_is_rejected(self):
        with self.assertRaises(ValueError):
            self.selector.build(
                665000,
                {"annualised_return": None, "volatility": 0.10},
                "central",
                self.allocation,
            )

    def test_allocation_validation_is_preserved(self):
        with self.assertRaises(ValueError):
            self.selector.build(
                665000,
                self.metrics,
                "central",
                (("AVIVA", 0.70), ("SKY", 0.20)),
            )

    def test_no_assumption_mutation_is_required(self):
        metrics = dict(self.metrics)
        self.selector.build(665000, metrics, "central", self.allocation)
        self.assertEqual(metrics, self.metrics)

    def test_negative_starting_pension_is_rejected(self):
        with self.assertRaises(ValueError):
            self.selector.build(-1, self.metrics, "central", self.allocation)

    def test_selected_input_is_enabled(self):
        result = self.selector.build(665000, self.metrics, "central", self.allocation)
        self.assertTrue(result.enabled)


if __name__ == "__main__":
    unittest.main()

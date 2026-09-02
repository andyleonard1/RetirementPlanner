import unittest

from planner.funds.fund_informed_projection_inputs import (
    FundInformedProjectionInputBuilder,
)
from planner.funds.portfolio_risk_return_scenarios import (
    PortfolioRiskReturnScenario,
)
from planner.funds.projection_engine_integration import (
    ProjectionEngineIntegration,
)


class ProjectionEngineIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.integration = ProjectionEngineIntegration()
        self.builder = FundInformedProjectionInputBuilder()
        self.scenario = PortfolioRiskReturnScenario(
            "central", 0.06, 0.10, "historical annualised return"
        )
        self.allocation = (
            ("GB00BRDCMN86:GBP", 0.75),
            ("SKY_NEW_DRAWDOWN_LIFESTYLE", 0.25),
        )

    def test_legacy_path_preserves_existing_return(self):
        result = self.integration.select_return(0.04)
        self.assertAlmostEqual(result.expected_return, 0.04)
        self.assertFalse(result.fund_informed)

    def test_disabled_fund_path_preserves_existing_return(self):
        disabled = self.builder.build_disabled(665000)
        result = self.integration.select_return(0.04, disabled)
        self.assertAlmostEqual(result.expected_return, 0.04)
        self.assertFalse(result.fund_informed)

    def test_enabled_fund_path_uses_selected_scenario_return(self):
        fund_input = self.builder.build(665000, self.scenario, self.allocation)
        result = self.integration.select_return(0.04, fund_input)
        self.assertAlmostEqual(result.expected_return, 0.06)
        self.assertTrue(result.fund_informed)

    def test_enabled_fund_path_identifies_scenario(self):
        fund_input = self.builder.build(665000, self.scenario, self.allocation)
        result = self.integration.select_return(0.04, fund_input)
        self.assertIn("central", result.source)

    def test_legacy_source_is_explicit(self):
        result = self.integration.select_return(0.04)
        self.assertEqual(result.source, "legacy projection return")

    def test_conservative_scenario_can_be_selected(self):
        scenario = PortfolioRiskReturnScenario(
            "conservative", -0.04, 0.10,
            "historical annualised return minus one historical volatility",
        )
        fund_input = self.builder.build(665000, scenario, self.allocation)
        result = self.integration.select_return(0.04, fund_input)
        self.assertAlmostEqual(result.expected_return, -0.04)

    def test_optimistic_scenario_can_be_selected(self):
        scenario = PortfolioRiskReturnScenario(
            "optimistic", 0.16, 0.10,
            "historical annualised return plus one historical volatility",
        )
        fund_input = self.builder.build(665000, scenario, self.allocation)
        result = self.integration.select_return(0.04, fund_input)
        self.assertAlmostEqual(result.expected_return, 0.16)

    def test_zero_legacy_return_is_preserved(self):
        result = self.integration.select_return(0.0)
        self.assertEqual(result.expected_return, 0.0)

    def test_negative_legacy_return_is_preserved(self):
        result = self.integration.select_return(-0.02)
        self.assertAlmostEqual(result.expected_return, -0.02)

    def test_integration_does_not_require_fund_input(self):
        result = self.integration.select_return(0.05, None)
        self.assertEqual(result.expected_return, 0.05)

    def test_fund_input_is_not_mutated(self):
        fund_input = self.builder.build(665000, self.scenario, self.allocation)
        before = fund_input
        self.integration.select_return(0.04, fund_input)
        self.assertEqual(fund_input, before)

    def test_starting_pension_does_not_change_selected_return(self):
        fund_input = self.builder.build(999999, self.scenario, self.allocation)
        result = self.integration.select_return(0.04, fund_input)
        self.assertAlmostEqual(result.expected_return, 0.06)

    def test_allocation_does_not_change_selected_scenario(self):
        fund_input = self.builder.build(665000, self.scenario, self.allocation)
        result = self.integration.select_return(0.04, fund_input)
        self.assertEqual(result.expected_return, self.scenario.expected_return)

    def test_fund_informed_flag_is_boolean(self):
        result = self.integration.select_return(0.04)
        self.assertIsInstance(result.fund_informed, bool)

    def test_decision_is_immutable(self):
        result = self.integration.select_return(0.04)
        with self.assertRaises(AttributeError):
            result.expected_return = 0.99

    def test_legacy_engine_boundary_remains_explicit(self):
        result = self.integration.select_return(0.0475)
        self.assertEqual(result.source, "legacy projection return")
        self.assertAlmostEqual(result.expected_return, 0.0475)


if __name__ == "__main__":
    unittest.main()

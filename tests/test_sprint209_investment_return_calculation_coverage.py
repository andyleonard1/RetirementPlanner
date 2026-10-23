import unittest
from unittest.mock import patch

from planner.assumptions import Assumptions
from planner.investment_return import InvestmentReturnResolver
from planner.monte_carlo_engine import MonteCarloEngine
from planner.pension_engine import PensionEngine
from planner.planner import RetirementPlanner
from planner.models import RetirementYear


class Sprint209InvestmentReturnCalculationCoverageTests(unittest.TestCase):
    def make_assumptions(self):
        assumptions = Assumptions()
        assumptions.set("starting_pension", 100000.0)
        assumptions.set("expected_investment_return", 0.0475)
        assumptions.set("expected_return", 0.04)
        assumptions.set("platform_charge", 0.0025)
        assumptions.set("fund_charge", 0.0025)
        return assumptions

    def make_year(self):
        year = RetirementYear(age=65, calendar_year=2030, spouse_age=63)
        year.pension_withdrawal = 0.0
        return year

    def test_net_projection_return_subtracts_both_configured_charges(self):
        config = InvestmentReturnResolver.resolve(self.make_assumptions())
        self.assertAlmostEqual(config.net_projection_return, 0.0425)

    def test_expected_investment_return_changes_projection_growth(self):
        assumptions = self.make_assumptions()
        assumptions.set("expected_investment_return", 0.0575)
        year = self.make_year()
        PensionEngine(assumptions).apply([year])
        self.assertAlmostEqual(year.pension_growth, 5250.00)

    def test_platform_charge_changes_projection_growth(self):
        low = self.make_assumptions()
        high = self.make_assumptions()
        high.set("platform_charge", 0.0125)
        low_year = self.make_year()
        high_year = self.make_year()
        PensionEngine(low).apply([low_year])
        PensionEngine(high).apply([high_year])
        self.assertAlmostEqual(low_year.pension_growth, 4250.00)
        self.assertAlmostEqual(high_year.pension_growth, 3250.00)
        self.assertNotEqual(low_year.closing_pension, high_year.closing_pension)

    def test_fund_charge_changes_projection_growth(self):
        low = self.make_assumptions()
        high = self.make_assumptions()
        high.set("fund_charge", 0.0125)
        low_year = self.make_year()
        high_year = self.make_year()
        PensionEngine(low).apply([low_year])
        PensionEngine(high).apply([high_year])
        self.assertAlmostEqual(low_year.pension_growth, 4250.00)
        self.assertAlmostEqual(high_year.pension_growth, 3250.00)

    def test_monte_carlo_mean_uses_expected_return_less_charges(self):
        assumptions = self.make_assumptions()
        with patch("planner.monte_carlo_engine.random.Random.gauss", return_value=0.035) as gauss:
            with patch("planner.monte_carlo_engine.RetirementPlanner") as planner_cls:
                result = type("Result", (), {"summary": {"ending_assets": 100.0}})()
                planner_cls.return_value.run.return_value = result
                MonteCarloEngine(assumptions).run(iterations=1, seed=1)
                gauss.assert_called_once_with(0.035, 0.10)
                config = InvestmentReturnResolver.resolve(assumptions)
                self.assertAlmostEqual(config.net_monte_carlo_expected_return, 0.035)

    def test_negative_charges_are_rejected(self):
        assumptions = self.make_assumptions()
        assumptions.set("platform_charge", -0.001)
        with self.assertRaisesRegex(ValueError, "platform_charge cannot be negative"):
            assumptions.validate()

    def test_end_to_end_projection_responds_to_expected_investment_return(self):
        low = self.make_assumptions()
        high = self.make_assumptions()
        low.set("expected_investment_return", 0.0375)
        high.set("expected_investment_return", 0.0575)
        low_result = RetirementPlanner(low, audit_context="test").run()
        high_result = RetirementPlanner(high, audit_context="test").run()
        self.assertLess(
            low_result.timeline[0].pension_growth,
            high_result.timeline[0].pension_growth,
        )
        self.assertNotEqual(
            low_result.summary["ending_assets"],
            high_result.summary["ending_assets"],
        )


if __name__ == "__main__":
    unittest.main()

import unittest
from unittest.mock import patch

from planner.assumption_resolver import AssumptionResolver
from planner.assumptions import Assumptions
from planner.inflation_engine import InflationEngine
from planner.savings_engine import SavingsEngine
from planner.investment_return import InvestmentReturnResolver


class TestSprint220AssumptionConsolidation(unittest.TestCase):
    def test_canonical_inflation_wins_over_legacy(self):
        a = Assumptions()
        a.set("inflation_rate", 0.025)
        a.set("inflation", 0.04)
        self.assertEqual(AssumptionResolver(a).inflation_rate(), 0.025)

    def test_legacy_inflation_is_fallback(self):
        a = Assumptions()
        a.data.pop("inflation_rate")
        self.assertEqual(AssumptionResolver(a).inflation_rate(), a.get("inflation"))

    def test_canonical_savings_rate_wins(self):
        a = Assumptions()
        a.set("savings_interest_rate", 0.03)
        a.set("savings_interest", 0.07)
        self.assertEqual(AssumptionResolver(a).savings_interest_rate(), 0.03)

    def test_legacy_savings_rate_is_fallback(self):
        a = Assumptions()
        a.data.pop("savings_interest_rate")
        self.assertEqual(AssumptionResolver(a).savings_interest_rate(), a.get("savings_interest"))

    def test_canonical_investment_return_wins(self):
        a = Assumptions()
        a.set("expected_investment_return", 0.05)
        a.set("pension_growth", 0.09)
        self.assertEqual(AssumptionResolver(a).expected_investment_return(), 0.05)

    def test_legacy_investment_return_fallback(self):
        a = Assumptions()
        a.data.pop("expected_investment_return")
        self.assertEqual(InvestmentReturnResolver.resolve(a).gross_projection_return, a.get("pension_growth"))

    def test_monte_carlo_return_remains_distinct(self):
        a = Assumptions()
        a.set("expected_investment_return", 0.05)
        a.set("expected_return", 0.04)
        self.assertEqual(InvestmentReturnResolver.resolve(a).monte_carlo_expected_return, 0.04)

    def test_live_engines_use_canonical_boundaries(self):
        a = Assumptions()
        a.set("inflation_rate", 0.02)
        a.set("inflation", 0.08)
        a.set("savings_interest_rate", 0.03)
        a.set("savings_interest", 0.09)
        self.assertEqual(AssumptionResolver(a).inflation_rate(), 0.02)
        self.assertEqual(AssumptionResolver(a).savings_interest_rate(), 0.03)


if __name__ == "__main__":
    unittest.main()

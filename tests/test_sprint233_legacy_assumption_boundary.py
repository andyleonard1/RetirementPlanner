import unittest
from pathlib import Path

from planner.assumption_resolver import AssumptionResolver
from planner.planner import RetirementPlanner
from planner.funds.portfolio_historical_statistics import PortfolioHistoricalStatistics


class Sprint233LegacyAssumptionBoundaryTests(unittest.TestCase):
    def test_portfolio_projection_uses_canonical_return_with_legacy_fallback(self):
        assumptions = {
            "expected_investment_return": 0.0475,
            "pension_growth": 0.04,
        }
        self.assertAlmostEqual(
            AssumptionResolver(assumptions).expected_investment_return(),
            0.0475,
        )

    def test_portfolio_projection_falls_back_to_legacy_return(self):
        assumptions = {"pension_growth": 0.04}
        self.assertAlmostEqual(
            AssumptionResolver(assumptions).expected_investment_return(),
            0.04,
        )

    def test_planner_has_no_direct_legacy_return_read(self):
        source = Path("planner/planner.py").read_text(encoding="utf-8")
        self.assertNotIn('assumptions.get("pension_growth")', source)
        self.assertIn("AssumptionResolver", source)

    def test_zero_and_negative_explicit_legacy_returns_remain_unchanged(self):
        resolver = AssumptionResolver({"expected_investment_return": 0.0, "pension_growth": -0.01})
        self.assertAlmostEqual(resolver.expected_investment_return(), 0.0)
        resolver = AssumptionResolver({"pension_growth": -0.01})
        self.assertAlmostEqual(resolver.expected_investment_return(), -0.01)


if __name__ == "__main__":
    unittest.main()

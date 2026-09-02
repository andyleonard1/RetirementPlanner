import unittest

from planner.assumptions import Assumptions
from planner.funds.portfolio_historical_statistics import PortfolioHistoricalStatisticsCalculator
from planner.planner import RetirementPlanner


class Sprint96FullPortfolioProjectionTests(unittest.TestCase):
    def setUp(self):
        self.assumptions = Assumptions()
        self.allocations = {"Aviva": 0.75, "Sky": 0.25}
        self.returns = {
            "Aviva": [0.10, 0.10, 0.10],
            "Sky": [0.20, 0.20, 0.20],
        }
        self.statistics = PortfolioHistoricalStatisticsCalculator().calculate(
            self.allocations, self.returns
        )

    def test_central_portfolio_scenario_runs_full_projection(self):
        planner = RetirementPlanner(self.assumptions)
        result = planner.run_with_portfolio_statistics(self.statistics, "central")
        self.assertGreater(len(result.timeline), 0)
        self.assertTrue(planner.projection_return_decision.fund_informed)

    def test_full_projection_uses_central_portfolio_return(self):
        planner = RetirementPlanner(self.assumptions)
        result = planner.run_with_portfolio_statistics(self.statistics, "central")
        expected = self.statistics.annualised_return
        self.assertAlmostEqual(planner.projection_return_decision.expected_return, expected)
        self.assertAlmostEqual(
            result.timeline[0].pension_growth,
            result.timeline[0].opening_pension * expected,
            places=1,
        )

    def test_full_projection_compounds_central_return(self):
        planner = RetirementPlanner(self.assumptions)
        result = planner.run_with_portfolio_statistics(self.statistics, "central")
        for previous, current in zip(result.timeline, result.timeline[1:]):
            self.assertAlmostEqual(previous.closing_pension, current.opening_pension, places=2)
            self.assertAlmostEqual(
                current.pension_growth,
                current.opening_pension * self.statistics.annualised_return,
                places=1,
            )

    def test_conservative_full_projection_uses_selected_return(self):
        planner = RetirementPlanner(self.assumptions)
        result = planner.run_with_portfolio_statistics(self.statistics, "conservative")
        rate = self.statistics.annualised_return - self.statistics.volatility
        self.assertAlmostEqual(planner.projection_return_decision.expected_return, rate)
        self.assertAlmostEqual(result.timeline[0].pension_growth, result.timeline[0].opening_pension * rate, places=2)

    def test_optimistic_full_projection_uses_selected_return(self):
        planner = RetirementPlanner(self.assumptions)
        result = planner.run_with_portfolio_statistics(self.statistics, "optimistic")
        rate = self.statistics.annualised_return + self.statistics.volatility
        self.assertAlmostEqual(planner.projection_return_decision.expected_return, rate)
        self.assertAlmostEqual(result.timeline[0].pension_growth, result.timeline[0].opening_pension * rate, places=2)

    def test_withdrawals_still_reduce_closing_pension_after_growth(self):
        planner = RetirementPlanner(self.assumptions)
        result = planner.run_with_portfolio_statistics(self.statistics, "central")
        first = result.timeline[0]
        self.assertAlmostEqual(
            first.closing_pension,
            first.opening_pension + first.pension_growth - first.pension_withdrawal,
            places=1,
        )

    def test_starting_pension_comes_from_assumptions(self):
        planner = RetirementPlanner(self.assumptions)
        result = planner.run_with_portfolio_statistics(self.statistics, "central")
        self.assertAlmostEqual(result.timeline[0].opening_pension, self.assumptions.get("starting_pension"), places=2)

    def test_statistics_are_not_mutated_by_full_projection(self):
        before = self.statistics
        planner = RetirementPlanner(self.assumptions)
        planner.run_with_portfolio_statistics(self.statistics, "central")
        self.assertEqual(before, self.statistics)

    def test_legacy_projection_still_runs_without_statistics(self):
        planner = RetirementPlanner(self.assumptions)
        result = planner.run()
        self.assertFalse(planner.projection_return_decision is not None and planner.projection_return_decision.fund_informed)
        self.assertGreater(len(result.timeline), 0)

    def test_custom_legacy_return_is_preserved_as_fallback_metadata(self):
        planner = RetirementPlanner(self.assumptions)
        planner.run_with_portfolio_statistics(self.statistics, "central", legacy_return=0.123)
        self.assertAlmostEqual(planner.projection_return_decision.expected_return, self.statistics.annualised_return)

    def test_missing_volatility_allows_only_central_full_projection(self):
        stats = PortfolioHistoricalStatisticsCalculator().calculate(
            self.allocations,
            {"Aviva": [0.10], "Sky": [0.20]},
        )
        planner = RetirementPlanner(self.assumptions)
        result = planner.run_with_portfolio_statistics(stats, "central")
        self.assertGreater(len(result.timeline), 0)
        with self.assertRaises(ValueError):
            RetirementPlanner(self.assumptions).run_with_portfolio_statistics(stats, "optimistic")

    def test_invalid_statistics_type_is_rejected(self):
        with self.assertRaises(TypeError):
            RetirementPlanner(self.assumptions).run_with_portfolio_statistics({"annualised_return": 0.06}, "central")


if __name__ == "__main__":
    unittest.main()

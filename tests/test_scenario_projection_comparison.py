import unittest

from planner.assumptions import Assumptions
from planner.funds.portfolio_historical_statistics import PortfolioHistoricalStatisticsCalculator
from planner.projection.scenario_projection_comparison import ScenarioProjectionComparisonRunner


class ScenarioProjectionComparisonTests(unittest.TestCase):
    def setUp(self):
        self.assumptions = Assumptions()
        self.statistics = PortfolioHistoricalStatisticsCalculator().calculate(
            {"Aviva": 0.75, "Sky": 0.25},
            {"Aviva": [0.10, 0.02, 0.08], "Sky": [0.20, 0.04, 0.16]},
        )
        self.runner = ScenarioProjectionComparisonRunner()

    def run_all(self):
        return self.runner.run(assumptions=self.assumptions, statistics=self.statistics)

    def test_all_three_supported_scenarios_are_returned(self):
        result = self.run_all()
        self.assertEqual(result.scenario_names, ("conservative", "central", "optimistic"))

    def test_each_scenario_contains_full_timeline(self):
        result = self.run_all()
        lengths = {len(p.years) for p in result.projections}
        self.assertEqual(len(lengths), 1)
        self.assertGreater(next(iter(lengths)), 0)

    def test_scenario_ending_balances_are_exposed(self):
        result = self.run_all()
        self.assertEqual(set(result.ending_balances), {"conservative", "central", "optimistic"})

    def test_optimistic_ends_above_central(self):
        result = self.run_all()
        self.assertGreater(result.get("optimistic").ending_balance, result.get("central").ending_balance)

    def test_central_ends_above_conservative(self):
        result = self.run_all()
        self.assertGreater(result.get("central").ending_balance, result.get("conservative").ending_balance)

    def test_spread_is_highest_minus_lowest(self):
        result = self.run_all()
        self.assertAlmostEqual(
            result.ending_balance_spread,
            result.highest_ending_balance - result.lowest_ending_balance,
        )

    def test_starting_pension_is_consistent_across_scenarios(self):
        result = self.run_all()
        self.assertEqual({p.starting_pension for p in result.projections}, {self.assumptions.get("starting_pension")})

    def test_scenario_return_is_preserved(self):
        result = self.run_all()
        self.assertAlmostEqual(result.get("central").annual_return, self.statistics.annualised_return)

    def test_provenance_is_preserved(self):
        result = self.run_all()
        for projection in result.projections:
            self.assertIn("fund-informed scenario:", projection.source)

    def test_year_rows_preserve_balance_continuity(self):
        result = self.run_all()
        for projection in result.projections:
            for previous, current in zip(projection.years, projection.years[1:]):
                self.assertAlmostEqual(previous.ending_balance, current.starting_balance, places=2)

    def test_growth_and_withdrawals_are_exposed(self):
        result = self.run_all()
        for projection in result.projections:
            self.assertTrue(all(hasattr(row, "investment_growth") for row in projection.years))
            self.assertTrue(all(hasattr(row, "withdrawals") for row in projection.years))

    def test_custom_subset_can_be_requested(self):
        result = self.runner.run(
            assumptions=self.assumptions,
            statistics=self.statistics,
            scenarios=("central", "optimistic"),
        )
        self.assertEqual(result.scenario_names, ("central", "optimistic"))

    def test_duplicate_scenario_names_are_deduplicated(self):
        result = self.runner.run(
            assumptions=self.assumptions,
            statistics=self.statistics,
            scenarios=("central", "CENTRAL", "central"),
        )
        self.assertEqual(result.scenario_names, ("central",))

    def test_empty_scenario_list_is_rejected(self):
        with self.assertRaises(ValueError):
            self.runner.run(assumptions=self.assumptions, statistics=self.statistics, scenarios=())

    def test_invalid_statistics_type_is_rejected(self):
        with self.assertRaises(TypeError):
            self.runner.run(assumptions=self.assumptions, statistics={"annualised_return": 0.06})

    def test_missing_volatility_prevents_risk_scenarios(self):
        statistics = PortfolioHistoricalStatisticsCalculator().calculate(
            {"Aviva": 0.75, "Sky": 0.25},
            {"Aviva": [0.10], "Sky": [0.20]},
        )
        with self.assertRaises(ValueError):
            self.runner.run(assumptions=self.assumptions, statistics=statistics)

    def test_missing_volatility_still_allows_central_only(self):
        statistics = PortfolioHistoricalStatisticsCalculator().calculate(
            {"Aviva": 0.75, "Sky": 0.25},
            {"Aviva": [0.10], "Sky": [0.20]},
        )
        result = self.runner.run(
            assumptions=self.assumptions, statistics=statistics, scenarios=("central",)
        )
        self.assertEqual(result.scenario_names, ("central",))

    def test_statistics_are_not_mutated(self):
        before = self.statistics
        self.run_all()
        self.assertEqual(before, self.statistics)

    def test_result_is_immutable(self):
        result = self.run_all()
        with self.assertRaises(AttributeError):
            result.projections = ()

    def test_get_unknown_scenario_raises_key_error(self):
        with self.assertRaises(KeyError):
            self.run_all().get("unknown")

    def test_each_projection_has_same_year_labels(self):
        result = self.run_all()
        expected = tuple(row.year for row in result.projections[0].years)
        for projection in result.projections[1:]:
            self.assertEqual(tuple(row.year for row in projection.years), expected)


if __name__ == "__main__":
    unittest.main()

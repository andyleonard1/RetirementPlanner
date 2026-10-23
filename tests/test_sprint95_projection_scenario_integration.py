import unittest

from planner.funds.fund_informed_projection import FundInformedProjection
from planner.funds.portfolio_historical_statistics import (
    PortfolioHistoricalStatisticsCalculator,
)
from planner.funds.portfolio_scenario_selection import PortfolioScenarioSelector


class Sprint95ProjectionScenarioIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.allocations = {"Aviva": 0.75, "Sky": 0.25}
        self.returns = {
            "Aviva": [0.10, 0.10, 0.10],
            "Sky": [0.20, 0.20, 0.20],
        }
        self.statistics = PortfolioHistoricalStatisticsCalculator().calculate(
            self.allocations, self.returns
        )
        self.projection = FundInformedProjection()

    def test_statistics_are_typed_boundary(self):
        self.assertAlmostEqual(self.statistics.annualised_return, 0.125)
        self.assertIsNotNone(self.statistics.volatility)

    def test_central_selection_uses_typed_statistics(self):
        r = self.projection.build_from_statistics(
            665000, 0.04, self.statistics, "central"
        )
        self.assertAlmostEqual(r.projection_return.expected_return, 0.125)
        self.assertTrue(r.projection_return.fund_informed)

    def test_conservative_selection_uses_typed_statistics(self):
        r = self.projection.build_from_statistics(
            665000, 0.04, self.statistics, "conservative"
        )
        self.assertAlmostEqual(
            r.projection_return.expected_return,
            0.125 - self.statistics.volatility,
        )

    def test_optimistic_selection_uses_typed_statistics(self):
        r = self.projection.build_from_statistics(
            665000, 0.04, self.statistics, "optimistic"
        )
        self.assertAlmostEqual(
            r.projection_return.expected_return,
            0.125 + self.statistics.volatility,
        )

    def test_allocation_is_taken_from_statistics(self):
        r = self.projection.build_from_statistics(
            665000, 0.04, self.statistics, "central"
        )
        self.assertEqual(
            r.fund_input.fund_allocation,
            (("Aviva", 0.75), ("Sky", 0.25)),
        )

    def test_starting_pension_is_preserved(self):
        r = self.projection.build_from_statistics(
            712345.67, 0.04, self.statistics, "central"
        )
        self.assertEqual(r.fund_input.starting_pension, 712345.67)

    def test_legacy_return_is_ignored_when_fund_mode_enabled(self):
        r = self.projection.build_from_statistics(
            665000, 0.40, self.statistics, "central"
        )
        self.assertAlmostEqual(r.projection_return.expected_return, 0.125)

    def test_legacy_path_is_unchanged(self):
        r = self.projection.build_legacy(0.04)
        self.assertEqual(r.expected_return, 0.04)
        self.assertFalse(r.fund_informed)

    def test_one_year_central_growth_is_correct(self):
        r = self.projection.build_from_statistics(
            665000, 0.04, self.statistics, "central"
        )
        self.assertAlmostEqual(
            665000 * (1 + r.projection_return.expected_return),
            748125.0,
        )

    def test_three_year_growth_compounds(self):
        rate = self.projection.build_from_statistics(
            665000, 0.04, self.statistics, "central"
        ).projection_return.expected_return
        self.assertAlmostEqual(665000 * (1 + rate) ** 3, 946845.703125)

    def test_missing_volatility_only_allows_central(self):
        stats = PortfolioHistoricalStatisticsCalculator().calculate(
            {"Aviva": 0.75, "Sky": 0.25},
            {"Aviva": [0.10], "Sky": [0.20]},
        )
        self.assertEqual(
            tuple(s.name for s in PortfolioScenarioSelector().available_scenarios_from_statistics(stats)),
            ("central",),
        )

    def test_missing_volatility_rejects_conservative(self):
        stats = PortfolioHistoricalStatisticsCalculator().calculate(
            {"Aviva": 0.75, "Sky": 0.25},
            {"Aviva": [0.10], "Sky": [0.20]},
        )
        with self.assertRaises(ValueError):
            self.projection.build_from_statistics(665000, 0.04, stats, "conservative")

    def test_missing_volatility_rejects_optimistic(self):
        stats = PortfolioHistoricalStatisticsCalculator().calculate(
            {"Aviva": 0.75, "Sky": 0.25},
            {"Aviva": [0.10], "Sky": [0.20]},
        )
        with self.assertRaises(ValueError):
            self.projection.build_from_statistics(665000, 0.04, stats, "optimistic")

    def test_invalid_scenario_is_rejected(self):
        with self.assertRaises(ValueError):
            self.projection.build_from_statistics(665000, 0.04, self.statistics, "invalid")

    def test_negative_starting_pension_is_rejected(self):
        with self.assertRaises(ValueError):
            self.projection.build_from_statistics(-1, 0.04, self.statistics, "central")

    def test_non_statistics_input_is_rejected(self):
        with self.assertRaises(TypeError):
            self.projection.build_from_statistics(665000, 0.04, {"annualised_return": 0.06}, "central")

    def test_scenario_provenance_survives(self):
        r = self.projection.build_from_statistics(665000, 0.04, self.statistics, "central")
        self.assertEqual(r.fund_input.source, "historical annualised return")

    def test_statistics_object_is_not_mutated(self):
        before = self.statistics
        self.projection.build_from_statistics(665000, 0.04, self.statistics, "central")
        self.assertEqual(before, self.statistics)

    def test_legacy_projection_does_not_require_statistics(self):
        self.assertEqual(self.projection.build_legacy(0.07).expected_return, 0.07)

    def test_central_return_is_geometric_annualised_return(self):
        r = self.projection.build_from_statistics(665000, 0.04, self.statistics, "central")
        self.assertAlmostEqual(r.fund_input.expected_return, self.statistics.annualised_return)

    def test_allocation_weights_sum_to_one(self):
        r = self.projection.build_from_statistics(665000, 0.04, self.statistics, "central")
        self.assertAlmostEqual(sum(w for _, w in r.fund_input.fund_allocation), 1.0)


if __name__ == "__main__":
    unittest.main()

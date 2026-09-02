import unittest

from planner.assumptions import Assumptions
from planner.funds.portfolio_historical_statistics import PortfolioHistoricalStatisticsCalculator
from planner.projection.scenario_projection_comparison import ScenarioProjectionComparisonRunner
from planner.projection.scenario_projection_view_model import (
    ScenarioCard,
    ScenarioProjectionViewModel,
    ScenarioYearRow,
)


class ScenarioProjectionViewModelTests(unittest.TestCase):
    def setUp(self):
        statistics = PortfolioHistoricalStatisticsCalculator().calculate(
            {"Aviva": 0.75, "Sky": 0.25},
            {"Aviva": [0.10, 0.02, 0.08], "Sky": [0.20, 0.04, 0.16]},
        )
        comparison = ScenarioProjectionComparisonRunner().run(
            assumptions=Assumptions(), statistics=statistics
        )
        self.comparison = comparison
        self.view = ScenarioProjectionViewModel.from_comparison(comparison)

    def test_has_three_scenario_cards(self):
        self.assertEqual(len(self.view.scenario_cards), 3)

    def test_card_order_matches_comparison(self):
        self.assertEqual(self.view.scenario_names, self.comparison.scenario_names)

    def test_cards_are_immutable_dataclasses(self):
        self.assertIsInstance(self.view.scenario_cards[0], ScenarioCard)
        with self.assertRaises(Exception):
            self.view.scenario_cards[0].name = "changed"

    def test_year_rows_are_immutable_dataclasses(self):
        self.assertIsInstance(self.view.year_rows[0], ScenarioYearRow)
        with self.assertRaises(Exception):
            self.view.year_rows[0].year = 9999

    def test_year_row_count_matches_report(self):
        expected = sum(len(projection.years) for projection in self.comparison.projections)
        self.assertEqual(len(self.view.year_rows), expected)

    def test_year_rows_preserve_scenario_order(self):
        names = [row.scenario for row in self.view.year_rows]
        first_count = len(self.comparison.get("conservative").years)
        self.assertEqual(names[:first_count], ["conservative"] * first_count)

    def test_ending_balance_series_preserves_values(self):
        expected = tuple(
            (name, self.comparison.get(name).ending_balance)
            for name in self.comparison.scenario_names
        )
        self.assertEqual(self.view.ending_balance_series(), expected)

    def test_spread_values_are_preserved(self):
        self.assertEqual(self.view.lowest_ending_balance, self.comparison.lowest_ending_balance)
        self.assertEqual(self.view.highest_ending_balance, self.comparison.highest_ending_balance)
        self.assertEqual(self.view.ending_balance_spread, self.comparison.ending_balance_spread)

    def test_card_values_are_preserved(self):
        for card in self.view.scenario_cards:
            source = self.comparison.get(card.name)
            self.assertEqual(card.ending_balance, source.ending_balance)
            self.assertEqual(card.annual_return, source.annual_return)
            self.assertEqual(card.starting_pension, source.starting_pension)

    def test_build_is_deterministic(self):
        other = ScenarioProjectionViewModel.from_comparison(self.comparison)
        self.assertEqual(self.view, other)

    def test_rejects_wrong_comparison_type(self):
        with self.assertRaises(TypeError):
            ScenarioProjectionViewModel.from_comparison(object())

    def test_does_not_mutate_comparison(self):
        before = self.comparison
        ScenarioProjectionViewModel.from_comparison(self.comparison)
        self.assertEqual(before, self.comparison)


if __name__ == "__main__":
    unittest.main()

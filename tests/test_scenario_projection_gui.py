import unittest

from planner.assumptions import Assumptions
from planner.funds.portfolio_historical_statistics import PortfolioHistoricalStatisticsCalculator
from planner.gui.scenario_projection_window import format_currency, format_percent, ScenarioProjectionWindow
from planner.projection.scenario_projection_comparison import ScenarioProjectionComparisonRunner
from planner.projection.scenario_projection_view_model import ScenarioProjectionViewModel


class ScenarioProjectionGuiTests(unittest.TestCase):
    def setUp(self):
        statistics = PortfolioHistoricalStatisticsCalculator().calculate(
            {"Aviva": 0.75, "Sky": 0.25},
            {"Aviva": [0.10, 0.02, 0.08], "Sky": [0.20, 0.04, 0.16]},
        )
        comparison = ScenarioProjectionComparisonRunner().run(
            assumptions=Assumptions(), statistics=statistics
        )
        self.view = ScenarioProjectionViewModel.from_comparison(comparison)

    def test_currency_format(self):
        self.assertEqual(format_currency(123456.7), "£123,457")

    def test_percent_format(self):
        self.assertEqual(format_percent(0.1234), "12.3%")

    def test_window_requires_view_model(self):
        with self.assertRaises(TypeError):
            ScenarioProjectionWindow(object())

    def test_window_retains_view_model_without_calculation(self):
        window = ScenarioProjectionWindow(self.view)
        self.assertIs(window.view_model, self.view)

    def test_gui_exposes_all_scenarios(self):
        window = ScenarioProjectionWindow(self.view)
        self.assertEqual(window.view_model.scenario_names, ("conservative", "central", "optimistic"))

    def test_gui_exposes_all_year_rows(self):
        window = ScenarioProjectionWindow(self.view)
        self.assertEqual(len(window.view_model.year_rows), len(self.view.year_rows))

    def test_gui_does_not_mutate_view_model(self):
        before = self.view
        window = ScenarioProjectionWindow(self.view)
        self.assertIs(window.view_model, before)
        self.assertEqual(window.view_model, before)

    def test_view_model_is_still_immutable(self):
        with self.assertRaises(Exception):
            self.view.scenario_cards = ()


if __name__ == "__main__":
    unittest.main()

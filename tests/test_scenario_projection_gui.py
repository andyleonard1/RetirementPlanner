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

class _FakeVar:
    def __init__(self, value):
        self.value = value

    def get(self):
        return self.value

    def set(self, value):
        self.value = value


class ScenarioProjectionGuiInteractionTests(unittest.TestCase):
    def _application(self):
        from planner.gui.scenario_projection_application import ScenarioProjectionApplication
        return ScenarioProjectionApplication(Assumptions())

    def _window(self):
        from planner.gui.scenario_projection_window import ScenarioProjectionWindow
        app = self._application()
        view = app.build_view_model(
            allocations={"Aviva": 0.75, "Sky": 0.25},
            fund_returns={"Aviva": [0.10, 0.02, 0.08], "Sky": [0.20, 0.04, 0.16]},
        )
        return ScenarioProjectionWindow(
            view,
            application=app,
            allocations={"Aviva": 0.75, "Sky": 0.25},
            fund_returns={"Aviva": [0.10, 0.02, 0.08], "Sky": [0.20, 0.04, 0.16]},
        )

    def test_parse_inputs_accepts_currency_formatting(self):
        from planner.gui.scenario_projection_window import ScenarioProjectionWindow
        inputs = ScenarioProjectionWindow.parse_inputs("£700,000", "64", "92", ("central",))
        self.assertEqual(inputs.starting_pension, 700000.0)
        self.assertEqual(inputs.retirement_age, 64)
        self.assertEqual(inputs.projection_end_age, 92)
        self.assertEqual(inputs.scenarios, ("central",))

    def test_parse_inputs_rejects_non_numeric_values(self):
        from planner.gui.scenario_projection_window import ScenarioProjectionWindow
        with self.assertRaises(ValueError):
            ScenarioProjectionWindow.parse_inputs("not-money", "64", "92", ("central",))

    def test_parse_inputs_rejects_unsupported_scenario(self):
        from planner.gui.scenario_projection_window import ScenarioProjectionWindow
        with self.assertRaises(ValueError):
            ScenarioProjectionWindow.parse_inputs("700000", "64", "92", ("central", "extreme"))

    def test_parse_inputs_rejects_no_selected_scenarios(self):
        from planner.gui.scenario_projection_window import ScenarioProjectionWindow
        with self.assertRaises(ValueError):
            ScenarioProjectionWindow.parse_inputs("700000", "64", "92", ())

    def test_application_requires_data_for_editable_window(self):
        from planner.gui.scenario_projection_window import ScenarioProjectionWindow
        with self.assertRaises(ValueError):
            ScenarioProjectionWindow(self._window().view_model, application=self._application())

    def test_application_rejects_wrong_type(self):
        from planner.gui.scenario_projection_window import ScenarioProjectionWindow
        with self.assertRaises(TypeError):
            ScenarioProjectionWindow(self._window().view_model, application=object(), allocations={}, fund_returns={})

    def test_current_input_strings_use_application_defaults(self):
        window = self._window()
        self.assertEqual(window._current_input_strings(), ("660000.0", "63", "90", ("conservative", "central", "optimistic")))

    def test_run_projection_applies_edits_and_refreshes_view(self):
        window = self._window()
        window._pension_var = _FakeVar("700000")
        window._retirement_age_var = _FakeVar("64")
        window._end_age_var = _FakeVar("92")
        window._scenario_vars = {
            "conservative": _FakeVar(False),
            "central": _FakeVar(True),
            "optimistic": _FakeVar(False),
        }
        refreshed = []
        window._refresh_results = lambda: refreshed.append(True)
        window._run_projection()
        self.assertEqual(window.application.assumptions.get("starting_pension"), 700000.0)
        self.assertEqual(window.application.assumptions.get("retirement_age"), 64)
        self.assertEqual(window.application.assumptions.get("projection_end_age"), 92)
        self.assertEqual(window.view_model.scenario_names, ("central",))
        self.assertEqual(refreshed, [True])

    def test_run_projection_keeps_assumptions_unsaved(self):
        window = self._window()
        window._pension_var = _FakeVar("700000")
        window._retirement_age_var = _FakeVar("64")
        window._end_age_var = _FakeVar("92")
        window._scenario_vars = {name: _FakeVar(name == "central") for name in ("conservative", "central", "optimistic")}
        window._refresh_results = lambda: None
        window._run_projection()
        self.assertTrue(window.application.assumptions.has_changes())

    def test_window_accepts_all_supported_scenarios_as_selected(self):
        window = self._window()
        window._pension_var = _FakeVar("660000")
        window._retirement_age_var = _FakeVar("63")
        window._end_age_var = _FakeVar("90")
        window._scenario_vars = {name: _FakeVar(True) for name in ("conservative", "central", "optimistic")}
        selected = window._current_input_strings()[3]
        self.assertEqual(selected, ("conservative", "central", "optimistic"))

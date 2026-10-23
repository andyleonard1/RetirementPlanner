import unittest
from types import MappingProxyType
from pathlib import Path

from planner.assumptions import Assumptions
import planner.gui.scenario_projection_window as scenario_projection_window
from planner.funds.portfolio_historical_statistics import PortfolioHistoricalStatisticsCalculator
from planner.gui.scenario_projection_window import (
    WORKFLOW_ACTION_PRESENTATION,
    WorkflowActionPresentation,
    WorkflowActionBinding,
    ScenarioProjectionWindow,
    format_currency,
    format_percent,
)
from planner.gui.workflow_state import WORKFLOW_ACTIONS
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



class ScenarioProjectionGuiDensityTests(unittest.TestCase):
    def setUp(self):
        statistics = PortfolioHistoricalStatisticsCalculator().calculate(
            {"Aviva": 0.75, "Sky": 0.25},
            {"Aviva": [0.10, 0.02, 0.08], "Sky": [0.20, 0.04, 0.16]},
        )
        comparison = ScenarioProjectionComparisonRunner().run(
            assumptions=Assumptions(), statistics=statistics
        )
        self.view = ScenarioProjectionViewModel.from_comparison(comparison)

    def test_view_model_scenario_count_is_available_for_dense_summary(self):
        self.assertEqual(len(self.view.scenario_cards), 3)

    def test_year_rows_preserve_order_for_dense_table(self):
        self.assertEqual([row.year for row in self.view.year_rows[:3]], [2027, 2028, 2029])

    def test_scenario_names_are_stable_for_card_layout(self):
        self.assertEqual(self.view.scenario_names, ("conservative", "central", "optimistic"))

    def test_ending_balance_series_preserves_card_order(self):
        series = self.view.ending_balance_series()
        self.assertEqual(tuple(name for name, _ in series), self.view.scenario_names)

    def test_gui_window_keeps_scrollable_result_contract(self):
        self.assertGreater(len(self.view.year_rows), 0)

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
        window._pension_var = _FakeVar("710000")
        window._retirement_age_var = _FakeVar("65")
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

class ScenarioProjectionGuiWorkflowActionTests(unittest.TestCase):
    def _window(self):
        from planner.gui.scenario_projection_application import ScenarioProjectionApplication
        app = ScenarioProjectionApplication(Assumptions())
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

    def _buttons(self, window):
        window._run_button = _FakeButton()
        window._save_button = _FakeButton()
        window._reset_button = _FakeButton()
        window._reload_button = _FakeButton()


    def test_workflow_action_presentation_descriptors_are_immutable_named_records(self):
        self.assertTrue(all(isinstance(item, WorkflowActionPresentation) for item in WORKFLOW_ACTION_PRESENTATION))
        descriptor = WORKFLOW_ACTION_PRESENTATION[0]
        self.assertEqual(descriptor.action, "run")
        self.assertEqual(descriptor.handler_name, "_run_projection")
        self.assertEqual(descriptor.button_name, "_run_button")
        with self.assertRaises(AttributeError):
            descriptor.action = "save"

    def test_workflow_action_presentation_descriptors_have_unique_canonical_actions(self):
        actions = tuple(item.action for item in WORKFLOW_ACTION_PRESENTATION)
        self.assertEqual(actions, WORKFLOW_ACTIONS)
        self.assertEqual(len(actions), len(set(actions)))

    def test_workflow_action_contract_rejects_descriptor_vocabulary_drift(self):
        window = self._window()
        original = scenario_projection_window.WORKFLOW_ACTION_PRESENTATION
        try:
            scenario_projection_window.WORKFLOW_ACTION_PRESENTATION = (
                WorkflowActionPresentation("run", "_run_projection", "_run_button"),
                WorkflowActionPresentation("save", "_save_assumptions", "_save_button"),
                WorkflowActionPresentation("reload", "_reload_saved_assumptions", "_reload_button"),
                WorkflowActionPresentation("reset", "_reset_inputs", "_reset_button"),
            )
            with self.assertRaisesRegex(RuntimeError, "out of sync with canonical actions"):
                window._workflow_action_contract()
        finally:
            scenario_projection_window.WORKFLOW_ACTION_PRESENTATION = original

    def test_workflow_action_contract_returns_immutable_resolved_bindings(self):
        window = self._window()
        self._buttons(window)
        contract = window._workflow_action_contract()
        self.assertTrue(all(isinstance(binding, WorkflowActionBinding) for binding in contract))
        with self.assertRaises(Exception):
            contract[0].action = "save"

    def test_workflow_action_binding_exposes_named_runtime_fields(self):
        window = self._window()
        self._buttons(window)
        binding = window._workflow_action_contract()[0]
        self.assertEqual(binding.action, "run")
        self.assertEqual(binding.handler, window._run_projection)
        self.assertIs(binding.button, window._run_button)

    def test_workflow_action_contract_binding_order_matches_canonical_actions(self):
        window = self._window()
        self._buttons(window)
        contract = window._workflow_action_contract()
        self.assertEqual(tuple(binding.action for binding in contract), WORKFLOW_ACTIONS)

    def test_workflow_action_contract_preserves_canonical_descriptor_order(self):
        window = self._window()
        contract = window._workflow_action_contract()
        self.assertEqual(tuple(binding.action for binding in contract), WORKFLOW_ACTIONS)

    def test_workflow_action_contract_rejects_duplicate_handler_bindings(self):
        window = self._window()
        original = scenario_projection_window.WORKFLOW_ACTION_PRESENTATION
        try:
            scenario_projection_window.WORKFLOW_ACTION_PRESENTATION = (
                WorkflowActionPresentation("run", "_run_projection", "_run_button"),
                WorkflowActionPresentation("save", "_run_projection", "_save_button"),
                WorkflowActionPresentation("reset", "_reset_inputs", "_reset_button"),
                WorkflowActionPresentation("reload", "_reload_saved_assumptions", "_reload_button"),
            )
            with self.assertRaisesRegex(RuntimeError, "duplicate handler bindings"):
                window._workflow_action_contract()
        finally:
            scenario_projection_window.WORKFLOW_ACTION_PRESENTATION = original

    def test_workflow_action_contract_rejects_duplicate_button_bindings(self):
        window = self._window()
        original = scenario_projection_window.WORKFLOW_ACTION_PRESENTATION
        try:
            scenario_projection_window.WORKFLOW_ACTION_PRESENTATION = (
                WorkflowActionPresentation("run", "_run_projection", "_run_button"),
                WorkflowActionPresentation("save", "_save_assumptions", "_run_button"),
                WorkflowActionPresentation("reset", "_reset_inputs", "_reset_button"),
                WorkflowActionPresentation("reload", "_reload_saved_assumptions", "_reload_button"),
            )
            with self.assertRaisesRegex(RuntimeError, "duplicate button bindings"):
                window._workflow_action_contract()
        finally:
            scenario_projection_window.WORKFLOW_ACTION_PRESENTATION = original

    def test_workflow_action_contract_rejects_missing_or_noncallable_binding(self):
        window = self._window()
        original = scenario_projection_window.WORKFLOW_ACTION_PRESENTATION
        try:
            scenario_projection_window.WORKFLOW_ACTION_PRESENTATION = (
                WorkflowActionPresentation("run", "_missing_handler", "_run_button"),
                WorkflowActionPresentation("save", "_save_assumptions", "_save_button"),
                WorkflowActionPresentation("reset", "_reset_inputs", "_reset_button"),
                WorkflowActionPresentation("reload", "_reload_saved_assumptions", "_reload_button"),
            )
            with self.assertRaisesRegex(RuntimeError, "missing binding for run"):
                window._workflow_action_contract()
        finally:
            scenario_projection_window.WORKFLOW_ACTION_PRESENTATION = original

    def test_workflow_action_contract_rejects_invalid_descriptor_field_types(self):
        window = self._window()
        original = scenario_projection_window.WORKFLOW_ACTION_PRESENTATION
        try:
            scenario_projection_window.WORKFLOW_ACTION_PRESENTATION = (
                WorkflowActionPresentation("run", None, "_run_button"),
                WorkflowActionPresentation("save", "_save_assumptions", "_save_button"),
                WorkflowActionPresentation("reset", "_reset_inputs", "_reset_button"),
                WorkflowActionPresentation("reload", "_reload_saved_assumptions", "_reload_button"),
            )
            with self.assertRaisesRegex(RuntimeError, "invalid handler binding for run"):
                window._workflow_action_contract()
        finally:
            scenario_projection_window.WORKFLOW_ACTION_PRESENTATION = original

    def test_workflow_action_contract_rejects_nonconfigurable_button(self):
        window = self._window()
        window._run_button = object()
        with self.assertRaisesRegex(RuntimeError, "button is not configurable for run"):
            window._workflow_action_contract()

    def test_workflow_action_contract_allows_optional_none_button(self):
        window = self._window()
        window._run_button = None
        contract = window._workflow_action_contract()
        self.assertIsNone(contract[0].button)

    def test_workflow_action_presentation_contract_follows_canonical_action_order(self):
        self.assertEqual(tuple(item.action for item in WORKFLOW_ACTION_PRESENTATION), WORKFLOW_ACTIONS)
        self.assertEqual(
            tuple(item.handler_name for item in WORKFLOW_ACTION_PRESENTATION),
            ("_run_projection", "_save_assumptions", "_reset_inputs", "_reload_saved_assumptions"),
        )
        self.assertEqual(
            tuple(item.button_name for item in WORKFLOW_ACTION_PRESENTATION),
            ("_run_button", "_save_button", "_reset_button", "_reload_button"),
        )

    def test_workflow_action_binding_registry_is_immutable_and_canonical(self):
        window = self._window()
        self._buttons(window)
        bindings = window._workflow_action_bindings()
        self.assertEqual(tuple(bindings), WORKFLOW_ACTIONS)
        self.assertTrue(all(isinstance(binding, WorkflowActionBinding) for binding in bindings.values()))
        with self.assertRaises(TypeError):
            bindings["run"] = bindings["save"]

    def test_workflow_action_button_and_handler_maps_derive_from_binding_registry(self):
        window = self._window()
        self._buttons(window)
        registry = window._workflow_action_bindings()
        buttons = window._workflow_action_buttons()
        handlers = window._workflow_action_handlers()
        for action, binding in registry.items():
            self.assertIs(buttons[action], binding.button)
            self.assertEqual(handlers[action], binding.handler)

    def test_workflow_action_binding_cache_rebuilds_when_cached_registry_keys_drift(self):
        window = self._window()
        self._buttons(window)
        first = window._workflow_action_bindings()
        window._workflow_action_binding_registry = MappingProxyType({"run": first["run"]})

        rebuilt = window._workflow_action_bindings()

        self.assertIsNot(rebuilt, first)
        self.assertEqual(tuple(rebuilt), WORKFLOW_ACTIONS)

    def test_workflow_action_binding_cache_rebuilds_when_cached_binding_action_drifts(self):
        window = self._window()
        self._buttons(window)
        first = window._workflow_action_bindings()
        window._workflow_action_binding_registry = MappingProxyType(
            dict(first, run=WorkflowActionBinding("save", first["run"].handler, first["run"].button))
        )

        rebuilt = window._workflow_action_bindings()

        self.assertIsNot(rebuilt, first)
        self.assertEqual(tuple(rebuilt), WORKFLOW_ACTIONS)
        self.assertEqual(rebuilt["run"].action, "run")

    def test_workflow_action_binding_registry_is_resolved_once_and_reused(self):
        window = self._window()
        self._buttons(window)
        first = window._workflow_action_bindings()
        second = window._workflow_action_bindings()
        self.assertIs(first, second)

    def test_workflow_action_maps_consume_the_same_cached_registry(self):
        window = self._window()
        self._buttons(window)
        registry = window._workflow_action_bindings()
        buttons = window._workflow_action_buttons()
        handlers = window._workflow_action_handlers()
        self.assertIs(window._workflow_action_bindings(), registry)
        self.assertEqual(tuple(buttons), WORKFLOW_ACTIONS)
        self.assertEqual(tuple(handlers), WORKFLOW_ACTIONS)

    def test_workflow_action_binding_cache_invalidation_clears_registry_and_derived_maps(self):
        window = self._window()
        self._buttons(window)
        registry = window._workflow_action_bindings()
        buttons = window._workflow_action_buttons()
        handlers = window._workflow_action_handlers()
        self.assertIsNotNone(registry)
        self.assertIsNotNone(buttons)
        self.assertIsNotNone(handlers)

        window._invalidate_workflow_action_bindings()

        self.assertIsNone(window._workflow_action_binding_registry)
        self.assertIsNone(window._workflow_action_button_map)
        self.assertIsNone(window._workflow_action_handler_map)

    def test_workflow_action_binding_cache_invalidation_rebuilds_all_views_together(self):
        window = self._window()
        self._buttons(window)
        first_registry = window._workflow_action_bindings()
        first_buttons = window._workflow_action_buttons()
        first_handlers = window._workflow_action_handlers()

        window._invalidate_workflow_action_bindings()

        second_registry = window._workflow_action_bindings()
        second_buttons = window._workflow_action_buttons()
        second_handlers = window._workflow_action_handlers()
        self.assertIsNot(second_registry, first_registry)
        self.assertIsNot(second_buttons, first_buttons)
        self.assertIsNot(second_handlers, first_handlers)
        self.assertEqual(tuple(second_registry), WORKFLOW_ACTIONS)
        self.assertEqual(tuple(second_buttons), WORKFLOW_ACTIONS)
        self.assertEqual(tuple(second_handlers), WORKFLOW_ACTIONS)
        for action, binding in second_registry.items():
            self.assertIs(second_buttons[action], binding.button)
            self.assertEqual(second_handlers[action], binding.handler)

    def test_workflow_action_cache_invalidation_is_idempotent(self):
        window = self._window()
        window._invalidate_workflow_action_bindings()
        window._invalidate_workflow_action_bindings()
        self.assertIsNone(window._workflow_action_binding_registry)
        self.assertIsNone(window._workflow_action_button_map)
        self.assertIsNone(window._workflow_action_handler_map)

    def test_close_invalidates_cached_workflow_action_bindings(self):
        window = self._window()
        self._buttons(window)
        window._workflow_action_bindings()
        window._workflow_action_buttons()
        window._workflow_action_handlers()

        window.close()

        self.assertTrue(window.is_closed)
        self.assertIsNone(window._workflow_action_binding_registry)
        self.assertIsNone(window._workflow_action_button_map)
        self.assertIsNone(window._workflow_action_handler_map)

    def test_closed_refresh_does_not_rehydrate_released_workflow_action_cache(self):
        window = self._window()
        self._buttons(window)
        window._workflow_action_bindings()
        window._workflow_action_buttons()
        window._workflow_action_handlers()
        window.close()

        window._refresh_status()

        self.assertIsNone(window._workflow_action_binding_registry)
        self.assertIsNone(window._workflow_action_button_map)
        self.assertIsNone(window._workflow_action_handler_map)

    def test_closed_dispatch_does_not_rehydrate_released_workflow_action_cache(self):
        window = self._window()
        self._buttons(window)
        window._workflow_action_bindings()
        window._workflow_action_buttons()
        window._workflow_action_handlers()
        window.close()

        self.assertFalse(window._dispatch_workflow_action("run"))

        self.assertIsNone(window._workflow_action_binding_registry)
        self.assertIsNone(window._workflow_action_button_map)
        self.assertIsNone(window._workflow_action_handler_map)

    def test_closed_dispatch_short_circuits_before_state_refresh(self):
        window = self._window()
        window.close()
        calls = []
        window._refresh_status = lambda: calls.append("refresh")

        self.assertFalse(window._dispatch_workflow_action("run"))
        self.assertEqual(calls, [])

    def test_dispatch_remains_terminal_when_handler_closes_window(self):
        window = self._window()
        window._pension_var = _FakeVar("700000")
        window._retirement_age_var = _FakeVar("64")
        window._end_age_var = _FakeVar("92")
        window._scenario_vars = {
            name: _FakeVar(name == "central")
            for name in ("conservative", "central", "optimistic")
        }
        calls = []

        def handler():
            calls.append("run")
            window.close()

        self.assertTrue(window._dispatch_workflow_action("run", handler))
        self.assertEqual(calls, ["run"])
        self.assertTrue(window.is_closed)
        self.assertIsNone(window._workflow_action_binding_registry)
        self.assertIsNone(window._workflow_action_button_map)
        self.assertIsNone(window._workflow_action_handler_map)

    def test_closed_workflow_action_accessors_return_empty_immutable_maps(self):
        window = self._window()
        self._buttons(window)
        window._workflow_action_bindings()
        window._workflow_action_buttons()
        window._workflow_action_handlers()
        window.close()

        bindings = window._workflow_action_bindings()
        buttons = window._workflow_action_buttons()
        handlers = window._workflow_action_handlers()
        self.assertEqual(tuple(bindings), ())
        self.assertEqual(tuple(buttons), ())
        self.assertEqual(tuple(handlers), ())
        self.assertIs(bindings, buttons)
        self.assertIs(buttons, handlers)

    def test_closed_workflow_action_accessors_do_not_repopulate_cache(self):
        window = self._window()
        self._buttons(window)
        window._workflow_action_bindings()
        window._workflow_action_buttons()
        window._workflow_action_handlers()
        window.close()

        window._workflow_action_bindings()
        window._workflow_action_buttons()
        window._workflow_action_handlers()

        self.assertIsNone(window._workflow_action_binding_registry)
        self.assertIsNone(window._workflow_action_button_map)
        self.assertIsNone(window._workflow_action_handler_map)

    def test_close_is_idempotent_after_workflow_action_cache_invalidation(self):
        window = self._window()
        self._buttons(window)
        window._workflow_action_bindings()
        window._workflow_action_buttons()
        window._workflow_action_handlers()
        window.close()

        window.close()

        self.assertTrue(window.is_closed)
        self.assertIsNone(window._workflow_action_binding_registry)
        self.assertIsNone(window._workflow_action_button_map)
        self.assertIsNone(window._workflow_action_handler_map)

    def test_workflow_action_button_map_rebuilds_after_registry_invalidation(self):
        window = self._window()
        self._buttons(window)
        first = window._workflow_action_buttons()
        window._workflow_action_binding_registry = None
        second = window._workflow_action_buttons()
        self.assertIsNot(second, first)
        self.assertEqual(tuple(second), WORKFLOW_ACTIONS)
        for action in WORKFLOW_ACTIONS:
            self.assertIs(second[action], getattr(window, f"_{action}_button"))

    def test_workflow_action_handler_map_rebuilds_after_registry_invalidation(self):
        window = self._window()
        first = window._workflow_action_handlers()
        window._workflow_action_binding_registry = None
        second = window._workflow_action_handlers()
        self.assertIsNot(second, first)
        self.assertEqual(tuple(second), WORKFLOW_ACTIONS)
        expected = {
            "run": "_run_projection",
            "save": "_save_assumptions",
            "reset": "_reset_inputs",
            "reload": "_reload_saved_assumptions",
        }
        for action, handler in second.items():
            self.assertEqual(handler.__self__, window)
            self.assertEqual(handler.__func__, getattr(window, expected[action]).__func__)

    def test_workflow_action_registry_rebuilds_when_cached_handler_drifts(self):
        from types import MappingProxyType

        window = self._window()
        registry = window._workflow_action_bindings()
        drifted = dict(registry)
        drifted["run"] = WorkflowActionBinding("run", lambda: None, registry["run"].button)
        window._workflow_action_binding_registry = MappingProxyType(drifted)
        cached = window._workflow_action_binding_registry

        rebuilt = window._workflow_action_bindings()

        self.assertIsNot(rebuilt, cached)
        self.assertEqual(rebuilt["run"].handler.__self__, window)
        self.assertEqual(rebuilt["run"].handler.__func__, window._run_projection.__func__)

    def test_workflow_action_registry_drift_clears_derived_button_cache_before_rebuild(self):
        from types import MappingProxyType

        window = self._window()
        self._buttons(window)
        first_registry = window._workflow_action_bindings()
        first_map = window._workflow_action_buttons()
        drifted = dict(first_registry)
        drifted["run"] = WorkflowActionBinding("run", lambda: None, first_registry["run"].button)
        window._workflow_action_binding_registry = MappingProxyType(drifted)

        rebuilt_registry = window._workflow_action_bindings()

        self.assertIsNot(rebuilt_registry, first_registry)
        self.assertIsNone(window._workflow_action_button_map)
        self.assertIsNone(window._workflow_action_button_map_source)
        rebuilt_map = window._workflow_action_buttons()
        self.assertIsNot(rebuilt_map, first_map)
        self.assertIs(window._workflow_action_button_map_source, rebuilt_registry)

    def test_workflow_action_registry_drift_clears_derived_handler_cache_before_rebuild(self):
        from types import MappingProxyType

        window = self._window()
        first_registry = window._workflow_action_bindings()
        first_map = window._workflow_action_handlers()
        drifted = dict(first_registry)
        drifted["run"] = WorkflowActionBinding("run", lambda: None, first_registry["run"].button)
        window._workflow_action_binding_registry = MappingProxyType(drifted)

        rebuilt_registry = window._workflow_action_bindings()

        self.assertIsNot(rebuilt_registry, first_registry)
        self.assertIsNone(window._workflow_action_handler_map)
        self.assertIsNone(window._workflow_action_handler_map_source)
        rebuilt_map = window._workflow_action_handlers()
        self.assertIsNot(rebuilt_map, first_map)
        self.assertIs(window._workflow_action_handler_map_source, rebuilt_registry)

    def test_workflow_action_registry_rebuilds_when_cached_button_drifts(self):
        from types import MappingProxyType

        window = self._window()
        self._buttons(window)
        registry = window._workflow_action_bindings()
        drifted = dict(registry)
        drifted["run"] = WorkflowActionBinding("run", registry["run"].handler, None)
        window._workflow_action_binding_registry = MappingProxyType(drifted)
        cached = window._workflow_action_binding_registry

        rebuilt = window._workflow_action_bindings()

        self.assertIsNot(rebuilt, cached)
        self.assertIs(rebuilt["run"].button, window._run_button)

    def test_workflow_action_registry_rebuilds_when_cached_registry_has_invalid_type(self):
        window = self._window()
        window._workflow_action_binding_registry = object()

        rebuilt = window._workflow_action_bindings()

        self.assertEqual(tuple(rebuilt), WORKFLOW_ACTIONS)
        self.assertIsInstance(rebuilt, MappingProxyType)

    def test_workflow_action_registry_rebuilds_when_cached_registry_is_mutable_dict(self):
        window = self._window()
        original = window._workflow_action_bindings()
        window._workflow_action_binding_registry = dict(original)

        rebuilt = window._workflow_action_bindings()

        self.assertIsInstance(rebuilt, MappingProxyType)
        self.assertEqual(tuple(rebuilt), WORKFLOW_ACTIONS)

    def test_workflow_action_registry_rebuilds_when_cached_registry_is_mutable_mapping(self):
        from collections import UserDict

        window = self._window()
        original = window._workflow_action_bindings()
        window._workflow_action_binding_registry = UserDict(original)

        rebuilt = window._workflow_action_bindings()

        self.assertIsInstance(rebuilt, MappingProxyType)
        self.assertEqual(tuple(rebuilt), WORKFLOW_ACTIONS)

    def test_workflow_action_registry_failed_rebuild_does_not_publish_partial_cache(self):
        window = self._window()
        window._workflow_action_bindings()
        window._workflow_action_buttons()
        window._workflow_action_handlers()

        def fail_map(_values):
            raise RuntimeError("registry publication failed")

        window._workflow_action_binding_registry = object()
        window._immutable_workflow_action_map = fail_map

        with self.assertRaisesRegex(RuntimeError, "registry publication failed"):
            window._workflow_action_bindings()

        self.assertIsNone(window._workflow_action_binding_registry)
        self.assertIsNone(window._workflow_action_button_map)
        self.assertIsNone(window._workflow_action_handler_map)
        self.assertIsNone(window._workflow_action_button_map_source)
        self.assertIsNone(window._workflow_action_handler_map_source)

    def test_workflow_action_button_map_failed_rebuild_does_not_publish_partial_cache(self):
        window = self._window()
        self._buttons(window)
        registry = window._workflow_action_bindings()
        window._workflow_action_buttons()

        def fail_map(_values):
            raise RuntimeError("button map publication failed")

        window._workflow_action_button_map = object()
        window._immutable_workflow_action_map = fail_map

        with self.assertRaisesRegex(RuntimeError, "button map publication failed"):
            window._workflow_action_buttons()

        self.assertIs(window._workflow_action_binding_registry, registry)
        self.assertIsNone(window._workflow_action_button_map)
        self.assertIsNone(window._workflow_action_button_map_source)

    def test_workflow_action_registry_rebuilds_when_cached_mapping_raises_during_validation(self):
        from collections.abc import Mapping

        class BrokenMapping(Mapping):
            def __getitem__(self, key):
                raise RuntimeError("broken cache")

            def __iter__(self):
                raise RuntimeError("broken cache")

            def __len__(self):
                return 0

        window = self._window()
        window._workflow_action_binding_registry = BrokenMapping()

        rebuilt = window._workflow_action_bindings()

        self.assertEqual(tuple(rebuilt), WORKFLOW_ACTIONS)
        self.assertIsInstance(rebuilt, MappingProxyType)

    def test_workflow_action_derived_map_rebuilds_when_cached_mapping_raises_during_validation(self):
        from collections.abc import Mapping

        class BrokenMapping(Mapping):
            def __getitem__(self, key):
                raise RuntimeError("broken cache")

            def __iter__(self):
                raise RuntimeError("broken cache")

            def __len__(self):
                return 0

        window = self._window()
        self._buttons(window)
        registry = window._workflow_action_bindings()
        window._workflow_action_button_map = BrokenMapping()
        window._workflow_action_button_map_source = registry

        rebuilt = window._workflow_action_buttons()

        self.assertEqual(tuple(rebuilt), WORKFLOW_ACTIONS)
        self.assertIs(window._workflow_action_button_map_source, registry)

    def test_workflow_action_button_map_rebuilds_when_cached_map_has_invalid_type(self):
        window = self._window()
        self._buttons(window)
        registry = window._workflow_action_bindings()
        window._workflow_action_button_map = object()
        window._workflow_action_button_map_source = registry

        rebuilt = window._workflow_action_buttons()

        self.assertEqual(tuple(rebuilt), WORKFLOW_ACTIONS)
        for action, binding in registry.items():
            self.assertIs(rebuilt[action], binding.button)

    def test_workflow_action_handler_map_rebuilds_when_cached_map_has_invalid_type(self):
        window = self._window()
        registry = window._workflow_action_bindings()
        window._workflow_action_handler_map = object()
        window._workflow_action_handler_map_source = registry

        rebuilt = window._workflow_action_handlers()

        self.assertEqual(tuple(rebuilt), WORKFLOW_ACTIONS)
        for action, binding in registry.items():
            self.assertEqual(rebuilt[action], binding.handler)

    def test_workflow_action_button_map_rebuilds_when_registry_identity_changes(self):
        from types import MappingProxyType

        window = self._window()
        self._buttons(window)
        first_registry = window._workflow_action_bindings()
        first_map = window._workflow_action_buttons()
        window._workflow_action_binding_registry = MappingProxyType(dict(first_registry))

        second_map = window._workflow_action_buttons()

        self.assertIsNot(second_map, first_map)
        self.assertIs(window._workflow_action_button_map_source, window._workflow_action_binding_registry)
        self.assertEqual(tuple(second_map), WORKFLOW_ACTIONS)

    def test_workflow_action_button_map_rebuilds_when_equal_but_distinct_entry_is_cached(self):
        from types import MappingProxyType

        class EqualButton:
            def __eq__(self, other):
                return True

        window = self._window()
        self._buttons(window)
        registry = window._workflow_action_bindings()
        cached = dict(window._workflow_action_buttons())
        cached["run"] = EqualButton()
        window._workflow_action_button_map = MappingProxyType(cached)
        window._workflow_action_button_map_source = registry

        rebuilt = window._workflow_action_buttons()

        self.assertIs(rebuilt["run"], registry["run"].button)

    def test_workflow_action_button_map_rebuilds_when_cached_entries_drift(self):
        from types import MappingProxyType

        window = self._window()
        self._buttons(window)
        registry = window._workflow_action_bindings()
        window._workflow_action_button_map = MappingProxyType(
            {action: None for action in WORKFLOW_ACTIONS}
        )
        window._workflow_action_button_map_source = registry

        rebuilt = window._workflow_action_buttons()

        self.assertEqual(tuple(rebuilt), WORKFLOW_ACTIONS)
        for action, binding in registry.items():
            self.assertIs(rebuilt[action], binding.button)
        self.assertIs(window._workflow_action_button_map_source, registry)

    def test_workflow_action_handler_map_rebuilds_when_equal_but_distinct_entry_is_cached(self):
        from types import MappingProxyType

        class EqualHandler:
            def __call__(self):
                pass

            def __eq__(self, other):
                return True

        window = self._window()
        registry = window._workflow_action_bindings()
        cached = dict(window._workflow_action_handlers())
        cached["run"] = EqualHandler()
        window._workflow_action_handler_map = MappingProxyType(cached)
        window._workflow_action_handler_map_source = registry

        rebuilt = window._workflow_action_handlers()

        self.assertIs(rebuilt["run"], registry["run"].handler)

    def test_workflow_action_handler_map_rebuilds_when_cached_entries_drift(self):
        from types import MappingProxyType

        window = self._window()
        registry = window._workflow_action_bindings()
        window._workflow_action_handler_map = MappingProxyType(
            {action: None for action in WORKFLOW_ACTIONS}
        )
        window._workflow_action_handler_map_source = registry

        rebuilt = window._workflow_action_handlers()

        self.assertEqual(tuple(rebuilt), WORKFLOW_ACTIONS)
        for action, binding in registry.items():
            self.assertEqual(rebuilt[action], binding.handler)
        self.assertIs(window._workflow_action_handler_map_source, registry)

    def test_workflow_action_handler_map_rebuilds_when_registry_identity_changes(self):
        from types import MappingProxyType

        window = self._window()
        first_registry = window._workflow_action_bindings()
        first_map = window._workflow_action_handlers()
        window._workflow_action_binding_registry = MappingProxyType(dict(first_registry))

        second_map = window._workflow_action_handlers()

        self.assertIsNot(second_map, first_map)
        self.assertIs(window._workflow_action_handler_map_source, window._workflow_action_binding_registry)
        self.assertEqual(tuple(second_map), WORKFLOW_ACTIONS)

    def test_workflow_action_button_map_rebuilds_when_cached_key_order_drifts(self):
        from types import MappingProxyType

        window = self._window()
        self._buttons(window)
        registry = window._workflow_action_bindings()
        first = window._workflow_action_buttons()
        reordered = {action: first[action] for action in reversed(WORKFLOW_ACTIONS)}
        window._workflow_action_button_map = MappingProxyType(reordered)
        window._workflow_action_button_map_source = registry

        rebuilt = window._workflow_action_buttons()

        self.assertIsNot(rebuilt, first)
        self.assertEqual(tuple(rebuilt), WORKFLOW_ACTIONS)

    def test_workflow_action_handler_map_rebuilds_when_cached_key_order_drifts(self):
        from types import MappingProxyType

        window = self._window()
        registry = window._workflow_action_bindings()
        first = window._workflow_action_handlers()
        reordered = {action: first[action] for action in reversed(WORKFLOW_ACTIONS)}
        window._workflow_action_handler_map = MappingProxyType(reordered)
        window._workflow_action_handler_map_source = registry

        rebuilt = window._workflow_action_handlers()

        self.assertIsNot(rebuilt, first)
        self.assertEqual(tuple(rebuilt), WORKFLOW_ACTIONS)

    def test_workflow_action_button_map_rebuilds_when_source_reference_is_tampered(self):
        window = self._window()
        self._buttons(window)
        registry = window._workflow_action_bindings()
        first = window._workflow_action_buttons()
        window._workflow_action_button_map_source = object()

        rebuilt = window._workflow_action_buttons()

        self.assertIsNot(rebuilt, first)
        self.assertIs(window._workflow_action_button_map_source, registry)
        self.assertEqual(tuple(rebuilt), WORKFLOW_ACTIONS)

    def test_workflow_action_handler_map_rebuilds_when_source_reference_is_tampered(self):
        window = self._window()
        registry = window._workflow_action_bindings()
        first = window._workflow_action_handlers()
        window._workflow_action_handler_map_source = object()

        rebuilt = window._workflow_action_handlers()

        self.assertIsNot(rebuilt, first)
        self.assertIs(window._workflow_action_handler_map_source, registry)
        self.assertEqual(tuple(rebuilt), WORKFLOW_ACTIONS)

    def test_workflow_action_button_map_is_resolved_once_and_reused(self):
        window = self._window()
        self._buttons(window)
        first = window._workflow_action_buttons()
        second = window._workflow_action_buttons()
        self.assertIs(first, second)

    def test_workflow_action_handler_map_is_resolved_once_and_reused(self):
        window = self._window()
        first = window._workflow_action_handlers()
        second = window._workflow_action_handlers()
        self.assertIs(first, second)

    def test_refresh_action_states_uses_resolved_binding_registry(self):
        window = self._window()
        self._buttons(window)
        original = window._workflow_action_bindings
        calls = []
        def wrapped():
            calls.append(True)
            return original()
        window._workflow_action_bindings = wrapped
        window._refresh_action_states()
        self.assertEqual(len(calls), 1)

    def test_workflow_action_buttons_follow_canonical_action_order(self):
        window = self._window()
        self._buttons(window)
        buttons = window._workflow_action_buttons()
        self.assertEqual(tuple(buttons), WORKFLOW_ACTIONS)
        self.assertIs(buttons["run"], window._run_button)
        self.assertIs(buttons["save"], window._save_button)
        self.assertIs(buttons["reset"], window._reset_button)
        self.assertIs(buttons["reload"], window._reload_button)

    def test_workflow_action_button_map_is_immutable(self):
        window = self._window()
        self._buttons(window)
        buttons = window._workflow_action_buttons()
        with self.assertRaises(TypeError):
            buttons["run"] = window._save_button

    def test_workflow_action_handler_map_is_immutable(self):
        window = self._window()
        handlers = window._workflow_action_handlers()
        with self.assertRaises(TypeError):
            handlers["run"] = window._save_assumptions

    def test_workflow_action_buttons_and_handlers_share_one_contract(self):
        window = self._window()
        self._buttons(window)
        contract = window._workflow_action_contract()
        buttons = window._workflow_action_buttons()
        handlers = window._workflow_action_handlers()
        self.assertEqual(tuple(binding.action for binding in contract), WORKFLOW_ACTIONS)
        self.assertEqual({binding.action: binding.button for binding in contract}, buttons)
        self.assertEqual({binding.action: binding.handler for binding in contract}, handlers)

    def test_refresh_action_states_renders_every_canonical_action_from_state_snapshot(self):
        window = self._window()
        self._buttons(window)
        window._refresh_action_states(False)
        self.assertEqual(
            [button.states[-1] for button in (window._run_button, window._save_button, window._reset_button, window._reload_button)],
            ["disabled", "disabled", "disabled", "normal"],
        )

    def test_clean_state_disables_run_save_reset_but_allows_reload(self):
        window = self._window()
        self._buttons(window)
        window._refresh_action_states(False)
        self.assertEqual(window._run_button.states[-1], "disabled")
        self.assertEqual(window._save_button.states[-1], "disabled")
        self.assertEqual(window._reset_button.states[-1], "disabled")
        self.assertEqual(window._reload_button.states[-1], "normal")

    def test_valid_pending_state_enables_run_and_reset_only(self):
        window = self._window()
        self._buttons(window)
        window._pension_var = _FakeVar("700000")
        window._retirement_age_var = _FakeVar("63")
        window._end_age_var = _FakeVar("90")
        window._scenario_vars = {name: _FakeVar(True) for name in ("conservative", "central", "optimistic")}
        window._refresh_action_states(True)
        self.assertEqual(window._run_button.states[-1], "normal")
        self.assertEqual(window._save_button.states[-1], "disabled")
        self.assertEqual(window._reset_button.states[-1], "normal")
        self.assertEqual(window._reload_button.states[-1], "normal")

    def test_invalid_pending_state_disables_run_but_keeps_reset_available(self):
        window = self._window()
        self._buttons(window)
        window._pension_var = _FakeVar("not-money")
        window._retirement_age_var = _FakeVar("63")
        window._end_age_var = _FakeVar("90")
        window._scenario_vars = {name: _FakeVar(True) for name in ("conservative", "central", "optimistic")}
        window._refresh_action_states(True)
        self.assertEqual(window._run_button.states[-1], "disabled")
        self.assertEqual(window._save_button.states[-1], "disabled")
        self.assertEqual(window._reset_button.states[-1], "normal")
        self.assertEqual(window._reload_button.states[-1], "normal")

    def test_closed_state_disables_every_action(self):
        window = self._window()
        self._buttons(window)
        window._closed = True
        window._refresh_action_states(False)
        self.assertEqual(window._run_button.states[-1], "disabled")
        self.assertEqual(window._save_button.states[-1], "disabled")
        self.assertEqual(window._reset_button.states[-1], "disabled")
        self.assertEqual(window._reload_button.states[-1], "disabled")

    def test_reset_refreshes_action_state_after_pending_edit(self):
        window = self._window()
        self._buttons(window)
        window._pension_var = _FakeVar("700000")
        window._retirement_age_var = _FakeVar("63")
        window._end_age_var = _FakeVar("90")
        window._scenario_vars = {name: _FakeVar(name in ("central",)) for name in ("conservative", "central", "optimistic")}
        window._refresh_status()
        self.assertTrue(window.workflow_state.run_enabled)
        window._reset_inputs()
        self.assertFalse(window.workflow_state.pending_changes)
        self.assertEqual(window.workflow_state.status, "Saved assumptions")
        self.assertEqual(window._run_button.states[-1], "disabled")
        self.assertEqual(window._save_button.states[-1], "disabled")
        self.assertEqual(window._reset_button.states[-1], "disabled")
        self.assertEqual(window._reload_button.states[-1], "normal")

    def test_reset_refreshes_action_state_after_pending_invalid_edit(self):
        window = self._window()
        self._buttons(window)
        window._pension_var = _FakeVar("not-money")
        window._retirement_age_var = _FakeVar("63")
        window._end_age_var = _FakeVar("90")
        window._scenario_vars = {name: _FakeVar(True) for name in ("conservative", "central", "optimistic")}
        window._refresh_status()
        self.assertEqual(window.workflow_state.status, "Input needs attention")
        window._reset_inputs()
        self.assertEqual(window.workflow_state.status, "Saved assumptions")
        self.assertEqual(window._reset_button.states[-1], "disabled")


class ScenarioProjectionGuiUsabilityTests(unittest.TestCase):
    def _window(self):
        from planner.gui.scenario_projection_application import ScenarioProjectionApplication
        app = ScenarioProjectionApplication(Assumptions())
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

    def test_is_dirty_starts_false(self):
        window = self._window()
        self.assertFalse(window.is_dirty)

    def test_is_dirty_reflects_in_memory_edits(self):
        window = self._window()
        window.application.assumptions.set("starting_pension", 700000.0)
        self.assertTrue(window.is_dirty)

    def test_selected_scenarios_follow_controller_state(self):
        window = self._window()
        window._pension_var = _FakeVar("660000")
        window._retirement_age_var = _FakeVar("63")
        window._end_age_var = _FakeVar("90")
        window._scenario_vars = {
            "conservative": _FakeVar(False),
            "central": _FakeVar(True),
            "optimistic": _FakeVar(False),
        }
        window._refresh_results = lambda: None
        window._run_projection()
        self.assertEqual(window.selected_scenarios, ("central",))

    def test_reset_inputs_restores_current_assumptions(self):
        window = self._window()
        window._pension_var = _FakeVar("700000")
        window._retirement_age_var = _FakeVar("64")
        window._end_age_var = _FakeVar("92")
        window._scenario_vars = {name: _FakeVar(name == "central") for name in ("conservative", "central", "optimistic")}
        window.application.assumptions.set("starting_pension", 710000.0)
        window._reset_inputs()
        self.assertEqual(window._pension_var.get(), "710000.0")
        self.assertEqual(window._retirement_age_var.get(), "63")
        self.assertEqual(window._end_age_var.get(), "90")

    def test_refresh_status_reports_dirty_state_and_selection(self):
        window = self._window()
        window._status_var = _FakeVar("")
        window._selection_var = _FakeVar("")
        window.application.assumptions.set("starting_pension", 700000.0)
        window._refresh_status()
        self.assertEqual(window._status_var.get(), "Unsaved changes")
        self.assertEqual(window._selection_var.get(), "Selected scenarios: Conservative, Central, Optimistic")

    def test_run_projection_refreshes_status_after_edit(self):
        window = self._window()
        window._status_var = _FakeVar("")
        window._selection_var = _FakeVar("")
        window._pension_var = _FakeVar("700000")
        window._retirement_age_var = _FakeVar("64")
        window._end_age_var = _FakeVar("92")
        window._scenario_vars = {name: _FakeVar(name == "central") for name in ("conservative", "central", "optimistic")}
        window._refresh_results = lambda: None
        window._run_projection()
        self.assertEqual(window._status_var.get(), "Unsaved changes")
        self.assertEqual(window._selection_var.get(), "Selected scenarios: Central")

class ScenarioProjectionGuiResultFreshnessTests(unittest.TestCase):
    def _window(self):
        from planner.gui.scenario_projection_application import ScenarioProjectionApplication
        app = ScenarioProjectionApplication(Assumptions())
        view = app.build_view_model(
            allocations={"Aviva": 0.75, "Sky": 0.25},
            fund_returns={"Aviva": [0.10, 0.02, 0.08], "Sky": [0.20, 0.04, 0.16]},
        )
        return ScenarioProjectionWindow(
            view, application=app,
            allocations={"Aviva": 0.75, "Sky": 0.25},
            fund_returns={"Aviva": [0.10, 0.02, 0.08], "Sky": [0.20, 0.04, 0.16]},
        )

    def test_results_are_current_at_initial_checkpoint(self):
        window = self._window()
        self.assertTrue(window.results_are_current)

    def test_editing_projection_control_marks_results_stale(self):
        window = self._window()
        window._pension_var = _FakeVar("710000")
        window._retirement_age_var = _FakeVar("63")
        window._end_age_var = _FakeVar("90")
        window._scenario_vars = {name: _FakeVar(name == "central") for name in ("conservative", "central", "optimistic")}
        self.assertFalse(window.results_are_current)

    def test_running_projection_marks_results_current_again(self):
        window = self._window()
        window._pension_var = _FakeVar("710000")
        window._retirement_age_var = _FakeVar("63")
        window._end_age_var = _FakeVar("90")
        window._scenario_vars = {name: _FakeVar(name == "central") for name in ("conservative", "central", "optimistic")}
        window._refresh_results = lambda: None
        window._run_projection()
        self.assertTrue(window.results_are_current)

    def test_assumption_edit_marks_existing_results_stale(self):
        window = self._window()
        window.application.assumptions.set("starting_pension", 700000.0)
        self.assertFalse(window.results_are_current)

class ScenarioProjectionGuiResultExportContractTests(unittest.TestCase):
    def _window(self):
        from planner.gui.scenario_projection_application import ScenarioProjectionApplication
        app = ScenarioProjectionApplication(Assumptions())
        view = app.build_view_model(
            allocations={"Aviva": 0.75, "Sky": 0.25},
            fund_returns={"Aviva": [0.10, 0.02, 0.08], "Sky": [0.20, 0.04, 0.16]},
        )
        return ScenarioProjectionWindow(
            view, application=app,
            allocations={"Aviva": 0.75, "Sky": 0.25},
            fund_returns={"Aviva": [0.10, 0.02, 0.08], "Sky": [0.20, 0.04, 0.16]},
        )

    def test_current_result_snapshot_is_the_shared_consumer_contract(self):
        window = self._window()
        snapshot = window.current_result_snapshot()
        self.assertIs(snapshot, window._current_result_snapshot())
        self.assertEqual(snapshot["text"], window.current_result_report_text())
        self.assertEqual(
            window._mutable_result_value(snapshot["payload"]),
            window.current_result_report_payload(),
        )

    def test_current_result_snapshot_rejects_stale_results_before_consumer_access(self):
        window = self._window()
        window.application.assumptions.set("starting_pension", 710000.0)
        with self.assertRaisesRegex(RuntimeError, "results are stale"):
            window.current_result_snapshot()

    def test_current_report_payload_matches_displayed_view_model(self):
        window = self._window()
        payload = window.current_result_report_payload()
        self.assertEqual(tuple(item["name"] for item in payload["scenarios"]), window.view_model.scenario_names)
        self.assertEqual(payload["lowest_ending_balance"], window.view_model.lowest_ending_balance)
        self.assertEqual(len(payload["year_rows"]), len(window.view_model.year_rows))

    def test_stale_results_block_report_export(self):
        window = self._window()
        window.application.assumptions.set("starting_pension", 700000.0)
        with self.assertRaisesRegex(RuntimeError, "results are stale"):
            window.current_result_report_payload()

    def test_closed_window_clears_published_snapshot(self):
        window = self._window()
        snapshot = window._current_result_snapshot()
        self.assertIsNotNone(snapshot)
        window.close()
        self.assertIsNone(window._last_result_snapshot)

    def test_closed_window_blocks_report_export(self):
        window = self._window()
        window.close()
        with self.assertRaisesRegex(RuntimeError, "projection window is closed"):
            window.current_result_report_payload()

    def test_current_report_text_matches_displayed_result_after_rerun(self):
        window = self._window()
        window.application.assumptions.set("starting_pension", 700000.0)
        window._pension_var = _FakeVar("700000")
        window._retirement_age_var = _FakeVar("63")
        window._end_age_var = _FakeVar("90")
        window._scenario_vars = {name: _FakeVar(name == "central") for name in ("conservative", "central", "optimistic")}
        window._refresh_results = lambda: None
        window._run_projection()
        text = window.current_result_report_text()
        self.assertIn("RETIREMENT SCENARIO COMPARISON", text)
        self.assertIn("central", text)
        self.assertIn(f"£{window.view_model.scenario_cards[0].ending_balance:,.0f}", text)

    def test_export_current_result_json_matches_shared_snapshot_payload(self):
        import json
        import tempfile

        window = self._window()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "result.json"
            window.export_current_result_json(path)
            exported = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(exported, window.current_result_report_payload())

    def test_export_current_result_text_matches_shared_snapshot_text(self):
        import tempfile

        window = self._window()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "result.txt"
            window.export_current_result_text(path)
            exported = path.read_text(encoding="utf-8").rstrip("\n")
        self.assertEqual(exported, window.current_result_report_text())

    def test_export_current_result_rejects_stale_results(self):
        import tempfile

        window = self._window()
        window._pension_var = _FakeVar("710000")
        window._retirement_age_var = _FakeVar("64")
        window._end_age_var = _FakeVar("92")
        window._scenario_vars = {name: _FakeVar(name == "central") for name in ("conservative", "central", "optimistic")}
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(RuntimeError):
                window.export_current_result_json(Path(directory) / "stale.json")

    def test_export_overwrites_existing_file_only_after_complete_write(self):
        import tempfile

        window = self._window()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "result.json"
            path.write_text("old-content", encoding="utf-8")
            window.export_current_result_json(path)
            self.assertNotEqual(path.read_text(encoding="utf-8"), "old-content")
            self.assertFalse(path.with_name(f".{path.name}.result.tmp").exists())

    def test_export_current_result_bundle_uses_one_shared_snapshot_for_both_files(self):
        import tempfile
        from unittest.mock import patch

        window = self._window()
        with tempfile.TemporaryDirectory() as directory:
            first = window._current_result_snapshot()
            with patch.object(window, "_current_result_snapshot", return_value=first) as resolver:
                paths = window.export_current_result_bundle(directory)
            self.assertEqual(paths["json"].name, "retirement_projection.json")
            self.assertEqual(paths["text"].name, "retirement_projection.txt")
            self.assertEqual(resolver.call_count, 1)
            import json
            payload = json.loads(paths["json"].read_text(encoding="utf-8"))
            self.assertEqual(payload, window.current_result_report_payload())
            self.assertEqual(paths["text"].read_text(encoding="utf-8"), window.current_result_report_text() + "\n")

    def test_export_current_result_bundle_rejects_invalid_stem_before_writing(self):
        import tempfile

        window = self._window()
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                window.export_current_result_bundle(directory, "nested/result")
            self.assertEqual(list(Path(directory).iterdir()), [])

    def test_export_current_result_bundle_blocks_existing_destination_by_default(self):
        import tempfile

        window = self._window()
        with tempfile.TemporaryDirectory() as directory:
            json_path = Path(directory) / "retirement_projection.json"
            json_path.write_text("existing", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                window.export_current_result_bundle(directory)
            self.assertEqual(json_path.read_text(encoding="utf-8"), "existing")
            self.assertFalse((Path(directory) / "retirement_projection.txt").exists())
            self.assertEqual(list(Path(directory).glob(".*.tmp")), [])

    def test_export_current_result_bundle_overwrite_replaces_both_outputs(self):
        import json
        import tempfile

        window = self._window()
        with tempfile.TemporaryDirectory() as directory:
            json_path = Path(directory) / "retirement_projection.json"
            text_path = Path(directory) / "retirement_projection.txt"
            json_path.write_text("old-json", encoding="utf-8")
            text_path.write_text("old-text", encoding="utf-8")
            paths = window.export_current_result_bundle(directory, overwrite=True)
            self.assertEqual(json.loads(paths["json"].read_text(encoding="utf-8")), window.current_result_report_payload())
            self.assertEqual(paths["text"].read_text(encoding="utf-8"), window.current_result_report_text() + "\n")
            self.assertEqual(list(Path(directory).glob(".*.tmp")), [])
            self.assertEqual(list(Path(directory).glob(".*.bak")), [])

    def test_export_current_result_bundle_rolls_back_both_outputs_on_second_publish_failure(self):
        import tempfile
        from unittest.mock import patch

        window = self._window()
        with tempfile.TemporaryDirectory() as directory:
            json_path = Path(directory) / "retirement_projection.json"
            text_path = Path(directory) / "retirement_projection.txt"
            json_path.write_text("old-json", encoding="utf-8")
            text_path.write_text("old-text", encoding="utf-8")
            original_replace = Path.replace
            calls = {"count": 0}

            def replace_with_failure(self, target):
                calls["count"] += 1
                if calls["count"] == 4:
                    raise OSError("simulated second publish failure")
                return original_replace(self, target)

            with patch.object(Path, "replace", new=replace_with_failure):
                with self.assertRaisesRegex(OSError, "simulated second publish failure"):
                    window.export_current_result_bundle(directory, overwrite=True)

            self.assertEqual(json_path.read_text(encoding="utf-8"), "old-json")
            self.assertEqual(text_path.read_text(encoding="utf-8"), "old-text")
            self.assertEqual(list(Path(directory).glob(".*.tmp")), [])
            self.assertEqual(list(Path(directory).glob(".*.bak")), [])

    def test_failed_atomic_export_cleans_temporary_file_and_preserves_destination(self):
        import tempfile
        from unittest.mock import patch

        window = self._window()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "result.txt"
            path.write_text("existing", encoding="utf-8")
            with patch.object(Path, "replace", side_effect=OSError("simulated publish failure")):
                with self.assertRaisesRegex(OSError, "simulated publish failure"):
                    window.export_current_result_text(path)

            self.assertEqual(path.read_text(encoding="utf-8"), "existing")
            self.assertEqual(list(Path(directory).glob(".*.tmp")), [])

    def test_report_snapshot_is_reused_for_repeated_current_exports(self):
        window = self._window()
        first_snapshot = window._current_result_snapshot()
        second_snapshot = window._current_result_snapshot()
        self.assertIs(first_snapshot, second_snapshot)
        self.assertEqual(first_snapshot["text"], second_snapshot["text"])

    def test_report_snapshot_payload_is_immutable_at_all_nested_levels(self):
        window = self._window()
        snapshot = window._current_result_snapshot()
        with self.assertRaises(TypeError):
            snapshot["payload"]["scenarios"] = ()
        with self.assertRaises(TypeError):
            snapshot["payload"]["summary"][0]["name"] = "tampered"
        with self.assertRaises(TypeError):
            snapshot["payload"]["year_rows"][0]["ending_balance"] = 0

    def test_new_projection_publishes_a_distinct_report_snapshot(self):
        window = self._window()
        first_snapshot = window._current_result_snapshot()
        window.application.assumptions.set("starting_pension", 700000.0)
        window._pension_var = _FakeVar("700000")
        window._retirement_age_var = _FakeVar("63")
        window._end_age_var = _FakeVar("90")
        window._scenario_vars = {name: _FakeVar(name == "central") for name in ("conservative", "central", "optimistic")}
        window._refresh_results = lambda: None
        window._run_projection()
        second_snapshot = window._current_result_snapshot()
        self.assertIsNot(first_snapshot, second_snapshot)
        self.assertNotEqual(first_snapshot["text"], second_snapshot["text"])

class ScenarioProjectionGuiPendingStateTests(unittest.TestCase):
    def _window(self):
        from planner.gui.scenario_projection_application import ScenarioProjectionApplication
        app = ScenarioProjectionApplication(Assumptions())
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

    def test_pending_scenarios_follow_checkbuttons_before_run(self):
        window = self._window()
        window._pension_var = _FakeVar("660000")
        window._retirement_age_var = _FakeVar("63")
        window._end_age_var = _FakeVar("90")
        window._scenario_vars = {
            "conservative": _FakeVar(False),
            "central": _FakeVar(True),
            "optimistic": _FakeVar(False),
        }
        self.assertEqual(window.selected_scenarios, ("conservative", "central", "optimistic"))
        self.assertEqual(window.pending_selected_scenarios, ("central",))
        self.assertTrue(window.has_pending_changes)

    def test_pending_change_status_is_distinct_from_unsaved_assumptions(self):
        window = self._window()
        window._pension_var = _FakeVar("660000")
        window._retirement_age_var = _FakeVar("63")
        window._end_age_var = _FakeVar("90")
        window._scenario_vars = {name: _FakeVar(name == "central") for name in ("conservative", "central", "optimistic")}
        window._status_var = _FakeVar("")
        window._selection_var = _FakeVar("")
        window._refresh_status()
        self.assertEqual(window._status_var.get(), "Changes ready to run")
        self.assertEqual(window._selection_var.get(), "Selected scenarios: Central")

    def test_reset_inputs_clears_pending_control_changes(self):
        window = self._window()
        window._pension_var = _FakeVar("700000")
        window._retirement_age_var = _FakeVar("64")
        window._end_age_var = _FakeVar("92")
        window._scenario_vars = {name: _FakeVar(name == "central") for name in ("conservative", "central", "optimistic")}
        self.assertTrue(window.has_pending_changes)
        window._reset_inputs()
        self.assertFalse(window.has_pending_changes)
        self.assertEqual(window.pending_selected_scenarios, window.selected_scenarios)

    def test_invalid_pending_control_state_is_reported_as_pending_change(self):
        window = self._window()
        window._pension_var = _FakeVar("not-a-number")
        window._retirement_age_var = _FakeVar("63")
        window._end_age_var = _FakeVar("90")
        window._scenario_vars = {name: _FakeVar(True) for name in ("conservative", "central", "optimistic")}
        self.assertTrue(window.has_pending_changes)

class _FakeButton:
    def __init__(self):
        self.states = []

    def configure(self, **kwargs):
        self.states.append(kwargs.get("state"))


class _FakeRoot:
    def __init__(self):
        self.bindings = {}
        self.destroyed = False

    def bind(self, event, callback):
        self.bindings[event] = callback

    def destroy(self):
        self.destroyed = True


class ScenarioProjectionGuiInteractionPolishTests(unittest.TestCase):
    def _window(self):
        from planner.gui.scenario_projection_application import ScenarioProjectionApplication
        app = ScenarioProjectionApplication(Assumptions())
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

    def _controls(self, window, pension="660000", retirement="63", end_age="90", central=True):
        window._pension_var = _FakeVar(pension)
        window._retirement_age_var = _FakeVar(retirement)
        window._end_age_var = _FakeVar(end_age)
        window._scenario_vars = {
            name: _FakeVar(name == "central" if central else True)
            for name in ("conservative", "central", "optimistic")
        }

    def test_run_button_disabled_when_no_pending_changes(self):
        window = self._window()
        self._controls(window, central=False)
        window._scenario_vars = {name: _FakeVar(True) for name in ("conservative", "central", "optimistic")}
        window._run_button = _FakeButton()
        window._save_button = _FakeButton()
        window._refresh_status()
        self.assertEqual(window._run_button.states[-1], "disabled")

    def test_run_button_enabled_for_pending_changes(self):
        window = self._window()
        self._controls(window, pension="700000")
        window._run_button = _FakeButton()
        window._save_button = _FakeButton()
        window._refresh_status()
        self.assertEqual(window._run_button.states[-1], "normal")

    def test_save_button_waits_until_pending_changes_are_run(self):
        window = self._window()
        self._controls(window, pension="700000")
        window.application.assumptions.set("starting_pension", 710000.0)
        window._run_button = _FakeButton()
        window._save_button = _FakeButton()
        window._refresh_status()
        self.assertEqual(window._save_button.states[-1], "disabled")

    def test_save_button_enabled_for_dirty_applied_state(self):
        window = self._window()
        self._controls(window, pension="710000", central=False)
        window.application.assumptions.set("starting_pension", 710000.0)
        window._scenario_vars = {name: _FakeVar(True) for name in ("conservative", "central", "optimistic")}
        window._run_button = _FakeButton()
        window._save_button = _FakeButton()
        window._refresh_status()
        self.assertEqual(window._save_button.states[-1], "normal")

    def test_keyboard_shortcut_contract_covers_canonical_actions_without_unknowns(self):
        from planner.gui.scenario_projection_window import WORKFLOW_KEYBOARD_BINDINGS
        from planner.gui.workflow_state import WORKFLOW_ACTIONS

        actions = tuple(action for _event, action, _handler in WORKFLOW_KEYBOARD_BINDINGS)
        self.assertTrue(actions)
        self.assertTrue(set(actions).issubset(set(WORKFLOW_ACTIONS)))
        self.assertEqual(set(actions), set(WORKFLOW_ACTIONS))

    def test_keyboard_shortcuts_bind_canonical_event_handlers_directly(self):
        window = self._window()
        root = _FakeRoot()
        window._root = root
        window._bind_keyboard_shortcuts()

        expected = {
            "<Return>": window._run_from_event,
            "<Escape>": window._reset_from_event,
            "<Alt-r>": window._run_from_event,
            "<Alt-s>": window._save_from_event,
            "<Alt-t>": window._reset_from_event,
            "<Alt-l>": window._reload_from_event,
        }
        self.assertEqual(set(root.bindings), set(expected))
        for event, handler in expected.items():
            self.assertEqual(root.bindings[event], handler)

    def test_keyboard_shortcuts_bind_run_and_reset(self):
        window = self._window()
        root = _FakeRoot()
        window._root = root
        window._bind_keyboard_shortcuts()
        self.assertIn("<Return>", root.bindings)
        self.assertIn("<Escape>", root.bindings)

    def test_invalid_pending_input_status_reports_attention(self):
        window = self._window()
        window._status_var = _FakeVar("")
        window._selection_var = _FakeVar("")
        self._controls(window, pension="not-money")
        window._refresh_status()
        self.assertEqual(window._status_var.get(), "Input needs attention")

    def test_pending_input_change_callback_refreshes_status(self):
        window = self._window()
        window._status_var = _FakeVar("")
        window._selection_var = _FakeVar("")
        self._controls(window, pension="700000")
        window._on_input_change()
        self.assertEqual(window._status_var.get(), "Changes ready to run")



class ScenarioProjectionGuiDensityTests(unittest.TestCase):
    def setUp(self):
        statistics = PortfolioHistoricalStatisticsCalculator().calculate(
            {"Aviva": 0.75, "Sky": 0.25},
            {"Aviva": [0.10, 0.02, 0.08], "Sky": [0.20, 0.04, 0.16]},
        )
        comparison = ScenarioProjectionComparisonRunner().run(
            assumptions=Assumptions(), statistics=statistics
        )
        self.view = ScenarioProjectionViewModel.from_comparison(comparison)

    def test_view_model_scenario_count_is_available_for_dense_summary(self):
        self.assertEqual(len(self.view.scenario_cards), 3)

    def test_year_rows_preserve_order_for_dense_table(self):
        self.assertEqual([row.year for row in self.view.year_rows[:3]], [2027, 2028, 2029])

    def test_scenario_names_are_stable_for_card_layout(self):
        self.assertEqual(self.view.scenario_names, ("conservative", "central", "optimistic"))

    def test_ending_balance_series_preserves_card_order(self):
        series = self.view.ending_balance_series()
        self.assertEqual(tuple(name for name, _ in series), self.view.scenario_names)

    def test_gui_window_keeps_scrollable_result_contract(self):
        self.assertGreater(len(self.view.year_rows), 0)

if __name__ == "__main__":
    unittest.main()

class ScenarioProjectionGuiValidationTests(unittest.TestCase):
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
        window = ScenarioProjectionWindow(
            view,
            application=app,
            allocations={"Aviva": 0.75, "Sky": 0.25},
            fund_returns={"Aviva": [0.10, 0.02, 0.08], "Sky": [0.20, 0.04, 0.16]},
        )
        window._pension_var = _FakeVar("660000")
        window._retirement_age_var = _FakeVar("63")
        window._end_age_var = _FakeVar("90")
        window._scenario_vars = {name: _FakeVar(True) for name in ("conservative", "central", "optimistic")}
        return window

    def test_pending_validation_message_is_empty_for_valid_controls(self):
        window = self._window()
        self.assertEqual(window._pending_validation_message(), "")

    def test_pending_validation_message_reports_bad_pension(self):
        window = self._window()
        window._pension_var.set("nan")
        self.assertIn("finite", window._pending_validation_message())

    def test_pending_validation_message_reports_age_order(self):
        window = self._window()
        window._end_age_var.set("62")
        self.assertIn("at least retirement_age", window._pending_validation_message())

    def test_pending_validation_message_reports_no_scenarios(self):
        window = self._window()
        for variable in window._scenario_vars.values():
            variable.set(False)
        self.assertIn("at least one scenario", window._pending_validation_message())

    def test_refresh_status_exposes_validation_feedback(self):
        window = self._window()
        window._status_var = _FakeVar("")
        window._selection_var = _FakeVar("")
        window._validation_var = _FakeVar("")
        window._run_button = _FakeButton()
        window._save_button = _FakeButton()
        window._pension_var.set("")
        window._refresh_status()
        self.assertIn("valid numeric", window._validation_var.value)

    def test_invalid_pending_controls_disable_run(self):
        window = self._window()
        window._run_button = _FakeButton()
        window._save_button = _FakeButton()
        window._pension_var.set("bad")
        window._refresh_action_states(True)
        self.assertEqual(window._run_button.states[-1], "disabled")

class _FocusFake:
    def __init__(self):
        self.focused = False
        self.selection = None

    def focus_set(self):
        self.focused = True

    def selection_range(self, start, end):
        self.selection = (start, end)


class ScenarioProjectionGuiAccessibilityTests(unittest.TestCase):
    def _window(self):
        from planner.gui.scenario_projection_application import ScenarioProjectionApplication
        app = ScenarioProjectionApplication(Assumptions())
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

    def _controls(self, window, pension="660000", retirement="63", end_age="90", scenarios=None):
        window._pension_var = _FakeVar(pension)
        window._retirement_age_var = _FakeVar(retirement)
        window._end_age_var = _FakeVar(end_age)
        selected = set(("conservative", "central", "optimistic") if scenarios is None else scenarios)
        window._scenario_vars = {name: _FakeVar(name in selected) for name in ("conservative", "central", "optimistic")}

    def test_keyboard_shortcuts_include_accessible_action_aliases(self):
        window = self._window()
        root = _FakeRoot()
        window._root = root
        window._bind_keyboard_shortcuts()
        self.assertIn("<Alt-r>", root.bindings)
        self.assertIn("<Alt-s>", root.bindings)
        self.assertIn("<Alt-t>", root.bindings)
        self.assertIn("<Alt-l>", root.bindings)

    def test_focus_validation_target_moves_to_bad_pension(self):
        window = self._window()
        self._controls(window, pension="not-a-number")
        pension_entry = _FocusFake()
        window._entry_widgets = [pension_entry, _FocusFake(), _FocusFake()]
        window._focus_validation_target()
        self.assertTrue(pension_entry.focused)

    def test_focus_validation_target_moves_to_bad_end_age(self):
        window = self._window()
        self._controls(window, retirement="63", end_age="62")
        entries = [_FocusFake(), _FocusFake(), _FocusFake()]
        window._entry_widgets = entries
        window._focus_validation_target()
        self.assertTrue(entries[2].focused)

    def test_focus_validation_target_moves_to_first_scenario_when_none_selected(self):
        window = self._window()
        self._controls(window, scenarios=())
        checkbuttons = {name: _FocusFake() for name in ("conservative", "central", "optimistic")}
        window._scenario_checkbuttons = checkbuttons
        window._entry_widgets = [_FocusFake(), _FocusFake(), _FocusFake()]
        window._focus_validation_target()
        self.assertTrue(checkbuttons["conservative"].focused)

    def test_focus_pension_entry_selects_existing_value(self):
        window = self._window()
        entry = _FocusFake()
        window._entry_widgets = [entry]
        window._focus_pension_entry()
        self.assertTrue(entry.focused)
        self.assertEqual(entry.selection, (0, "end"))

    def test_focus_validation_target_handles_missing_entry_widgets(self):
        window = self._window()
        self._controls(window, pension="bad")
        window._entry_widgets = []
        label = _FocusFake()
        window._validation_label = label
        window._focus_validation_target()
        self.assertTrue(label.focused)

    def test_reset_keeps_focusable_controls_available_after_pending_edit(self):
        window = self._window()
        self._controls(window, pension="700000")
        entries = [_FocusFake(), _FocusFake(), _FocusFake()]
        window._entry_widgets = entries
        window._reset_inputs()
        self.assertFalse(window.has_pending_changes)
        self.assertEqual(window._pension_var.get(), "660000.0")



class ScenarioProjectionGuiDensityTests(unittest.TestCase):
    def setUp(self):
        statistics = PortfolioHistoricalStatisticsCalculator().calculate(
            {"Aviva": 0.75, "Sky": 0.25},
            {"Aviva": [0.10, 0.02, 0.08], "Sky": [0.20, 0.04, 0.16]},
        )
        comparison = ScenarioProjectionComparisonRunner().run(
            assumptions=Assumptions(), statistics=statistics
        )
        self.view = ScenarioProjectionViewModel.from_comparison(comparison)

    def test_view_model_scenario_count_is_available_for_dense_summary(self):
        self.assertEqual(len(self.view.scenario_cards), 3)

    def test_year_rows_preserve_order_for_dense_table(self):
        self.assertEqual([row.year for row in self.view.year_rows[:3]], [2027, 2028, 2029])

    def test_scenario_names_are_stable_for_card_layout(self):
        self.assertEqual(self.view.scenario_names, ("conservative", "central", "optimistic"))

    def test_ending_balance_series_preserves_card_order(self):
        series = self.view.ending_balance_series()
        self.assertEqual(tuple(name for name, _ in series), self.view.scenario_names)

    def test_gui_window_keeps_scrollable_result_contract(self):
        self.assertGreater(len(self.view.year_rows), 0)

if __name__ == "__main__":
    unittest.main()

class _FakeCanvas:
    def __init__(self, width=800, height=180, series=()):
        self.width = width
        self.height = height
        self.calls = []
        self._scenario_series = series

    def delete(self, *args):
        self.calls.append(("delete", args))

    def winfo_width(self):
        return self.width

    def winfo_height(self):
        return self.height

    def create_text(self, *args, **kwargs):
        self.calls.append(("text", args, kwargs))

    def create_rectangle(self, *args, **kwargs):
        self.calls.append(("rectangle", args, kwargs))

    def create_line(self, *args, **kwargs):
        self.calls.append(("line", args, kwargs))

    def bind(self, *args, **kwargs):
        self.calls.append(("bind", args, kwargs))

    def focus_set(self):
        self.calls.append(("focus_set", (), {}))


class ScenarioProjectionGuiChartTests(unittest.TestCase):
    def _window(self):
        from planner.gui.scenario_projection_application import ScenarioProjectionApplication
        app = ScenarioProjectionApplication(Assumptions())
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

    def test_chart_uses_view_model_ending_balance_series(self):
        window = self._window()
        canvas = _FakeCanvas(series=window.view_model.ending_balance_series())
        window._chart_canvas = canvas
        window._draw_ending_balance_chart()
        rectangles = [call for call in canvas.calls if call[0] == "rectangle"]
        self.assertEqual(len(rectangles), 3)

    def test_chart_labels_each_selected_scenario(self):
        window = self._window()
        series = (("central", 100.0), ("optimistic", 150.0))
        canvas = _FakeCanvas(series=series)
        window._chart_canvas = canvas
        window._draw_ending_balance_chart()
        labels = [call[2]["text"] for call in canvas.calls if call[0] == "text" and "text" in call[2]]
        self.assertIn("Central", labels)
        self.assertIn("Optimistic", labels)

    def test_chart_scales_largest_value_to_plot_width(self):
        window = self._window()
        canvas = _FakeCanvas(width=800, series=(("central", 100.0), ("optimistic", 200.0)))
        window._chart_canvas = canvas
        window._draw_ending_balance_chart()
        rectangles = [call for call in canvas.calls if call[0] == "rectangle"]
        first_width = rectangles[0][1][2] - rectangles[0][1][0]
        second_width = rectangles[1][1][2] - rectangles[1][1][0]
        self.assertAlmostEqual(second_width, 2 * first_width)

    def test_chart_handles_empty_scenario_series(self):
        window = self._window()
        canvas = _FakeCanvas(series=())
        window._chart_canvas = canvas
        window._draw_ending_balance_chart()
        labels = [call[2]["text"] for call in canvas.calls if call[0] == "text" and "text" in call[2]]
        self.assertIn("No scenarios selected.", labels)
        self.assertFalse([call for call in canvas.calls if call[0] == "rectangle"])

    def test_chart_includes_axis_endpoints(self):
        window = self._window()
        canvas = _FakeCanvas(series=(("central", 100.0),))
        window._chart_canvas = canvas
        window._draw_ending_balance_chart()
        labels = [call[2]["text"] for call in canvas.calls if call[0] == "text" and "text" in call[2]]
        self.assertIn("£0", labels)
        self.assertIn("£100", labels)

    def test_chart_is_rebuilt_after_result_refresh(self):
        window = self._window()
        class _Content:
            def winfo_children(self):
                return []
        window._content = _Content()
        window._render_results = lambda ttk: setattr(window, "_chart_canvas", "rebuilt")
        window._refresh_results()
        self.assertEqual(window._chart_canvas, "rebuilt")


class ScenarioProjectionGuiChartAccessibilityTests(unittest.TestCase):
    def _window(self):
        from planner.gui.scenario_projection_application import ScenarioProjectionApplication
        app = ScenarioProjectionApplication(Assumptions())
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

    def test_chart_accessibility_summary_describes_focused_scenario(self):
        window = self._window()
        canvas = _FakeCanvas(series=(("central", 100.0), ("optimistic", 200.0)))
        window._chart_canvas = canvas
        window._chart_accessibility_var = _FakeVar("")
        window._refresh_chart_accessibility(1)
        self.assertIn("Optimistic", window._chart_accessibility_var.get())
        self.assertIn("£200", window._chart_accessibility_var.get())
        self.assertIn("Central £100", window._chart_accessibility_var.get())

    def test_chart_keyboard_navigation_changes_focused_scenario(self):
        window = self._window()
        canvas = _FakeCanvas(series=(("central", 100.0), ("optimistic", 200.0)))
        window._chart_canvas = canvas
        window._chart_accessibility_var = _FakeVar("")
        event = type("Event", (), {"keysym": "Right"})()
        result = window._on_chart_key(event)
        self.assertEqual(result, "break")
        self.assertEqual(window._chart_focus_index, 1)
        self.assertIn("Optimistic", window._chart_accessibility_var.get())

    def test_chart_keyboard_home_and_end_select_boundaries(self):
        window = self._window()
        canvas = _FakeCanvas(series=(("conservative", 50.0), ("central", 100.0), ("optimistic", 200.0)))
        window._chart_canvas = canvas
        window._chart_accessibility_var = _FakeVar("")
        for key, expected in (("End", 2), ("Home", 0)):
            event = type("Event", (), {"keysym": key})()
            self.assertEqual(window._on_chart_key(event), "break")
            self.assertEqual(window._chart_focus_index, expected)

    def test_empty_chart_has_accessible_empty_state(self):
        window = self._window()
        canvas = _FakeCanvas(series=())
        window._chart_canvas = canvas
        window._chart_accessibility_var = _FakeVar("")
        window._refresh_chart_accessibility()
        self.assertEqual(window._chart_accessibility_var.get(), "Chart: no scenarios selected.")

class _FakeRootLifecycle:
    def __init__(self):
        self.destroy_calls = 0

    def destroy(self):
        self.destroy_calls += 1


class ScenarioProjectionGuiLifecycleTests(unittest.TestCase):
    def _window(self, root=None):
        statistics = PortfolioHistoricalStatisticsCalculator().calculate(
            {"Aviva": 0.75, "Sky": 0.25},
            {"Aviva": [0.10, 0.02, 0.08], "Sky": [0.20, 0.04, 0.16]},
        )
        comparison = ScenarioProjectionComparisonRunner().run(
            assumptions=Assumptions(), statistics=statistics
        )
        return ScenarioProjectionWindow(
            ScenarioProjectionViewModel.from_comparison(comparison), root=root
        )

    def test_close_marks_window_closed(self):
        root = _FakeRootLifecycle()
        window = self._window(root)
        window.close()
        self.assertTrue(window.is_closed)
        self.assertEqual(root.destroy_calls, 1)

    def test_close_is_idempotent(self):
        root = _FakeRootLifecycle()
        window = self._window(root)
        window.close()
        window.close()
        self.assertEqual(root.destroy_calls, 1)

    def test_close_resynchronises_terminal_workflow_presentation(self):
        root = _FakeRootLifecycle()
        window = self._window(root)
        window._status_var = _FakeVar("")
        window._validation_var = _FakeVar("")
        window._selection_var = _FakeVar("")
        window._run_button = _FakeButton()
        window._save_button = _FakeButton()
        window._reset_button = _FakeButton()
        window._reload_button = _FakeButton()
        window.close()
        self.assertEqual(window._status_var.get(), "Closed")
        self.assertEqual(window.workflow_state.status, "Closed")
        self.assertEqual(window._run_button.states[-1], "disabled")
        self.assertEqual(window._save_button.states[-1], "disabled")
        self.assertEqual(window._reset_button.states[-1], "disabled")
        self.assertEqual(window._reload_button.states[-1], "disabled")

    def test_closed_window_cannot_be_built_again(self):
        root = _FakeRootLifecycle()
        window = self._window(root)
        window.close()
        with self.assertRaises(RuntimeError):
            window.build()

    def test_refresh_results_is_noop_after_close(self):
        root = _FakeRootLifecycle()
        window = self._window(root)
        window.close()
        window._content = object()
        window._refresh_results()
        self.assertIsInstance(window._content, object)

    def test_run_projection_is_noop_after_close(self):
        window = self._window(_FakeRootLifecycle())
        window.close()
        window._run_projection()
        self.assertTrue(window.is_closed)

    def test_save_and_reload_are_noop_after_close(self):
        window = self._window(_FakeRootLifecycle())
        window.close()
        window._save_assumptions()
        window._reload_saved_assumptions()
        self.assertTrue(window.is_closed)

class ScenarioProjectionGuiTestabilityTests(unittest.TestCase):
    def setUp(self):
        import shutil, tempfile
        from pathlib import Path
        self._tempdir = tempfile.TemporaryDirectory()
        source = Path(__file__).resolve().parents[1] / "data" / "assumptions.json"
        target = Path(self._tempdir.name) / "assumptions.json"
        shutil.copy2(source, target)
        self._assumptions_path = target

    def tearDown(self):
        self._tempdir.cleanup()

    def _window(self):
        from planner.gui.scenario_projection_application import ScenarioProjectionApplication
        from planner.gui.testability import RecordingDialog
        app = ScenarioProjectionApplication(Assumptions(str(self._assumptions_path)))
        view = app.build_view_model(
            allocations={"Aviva": 0.75, "Sky": 0.25},
            fund_returns={"Aviva": [0.10, 0.02, 0.08], "Sky": [0.20, 0.04, 0.16]},
        )
        dialog = RecordingDialog()
        window = ScenarioProjectionWindow(
            view,
            application=app,
            allocations={"Aviva": 0.75, "Sky": 0.25},
            fund_returns={"Aviva": [0.10, 0.02, 0.08], "Sky": [0.20, 0.04, 0.16]},
            dialog=dialog,
        )
        return window, dialog

    def test_recording_dialog_captures_errors_without_tk(self):
        from planner.gui.testability import RecordingDialog
        dialog = RecordingDialog()
        dialog.showerror("Title", "Problem")
        self.assertEqual(dialog.errors, [("Title", "Problem")])

    def test_recording_dialog_captures_info_without_tk(self):
        from planner.gui.testability import RecordingDialog
        dialog = RecordingDialog()
        dialog.showinfo("Title", "Saved")
        self.assertEqual(dialog.infos, [("Title", "Saved")])

    def test_invalid_projection_uses_injected_dialog(self):
        window, dialog = self._window()
        window._pension_var = _FakeVar("not-money")
        window._retirement_age_var = _FakeVar("63")
        window._end_age_var = _FakeVar("90")
        window._scenario_vars = {"central": _FakeVar(True)}
        window._focus_validation_target = lambda: None
        window._refresh_status = lambda: None
        window._run_projection()
        self.assertEqual(len(dialog.errors), 1)
        self.assertEqual(dialog.errors[0][0], "Invalid projection inputs")

    def test_failed_save_uses_injected_dialog(self):
        window, dialog = self._window()
        window.controller.save = lambda: (_ for _ in ()).throw(OSError("disk full"))
        window._save_assumptions()
        self.assertEqual(dialog.errors, [("Could not save assumptions", "disk full")])

    def test_successful_save_uses_injected_dialog(self):
        window, dialog = self._window()
        window.application.assumptions.set("starting_pension", 700000.0)
        window._refresh_status = lambda: None
        window._save_assumptions()
        self.assertEqual(dialog.infos, [("Assumptions saved", "Validated assumptions were saved.")])

    def test_window_can_be_constructed_with_dialog_double_without_tk(self):
        window, dialog = self._window()
        self.assertIs(window._dialog, dialog)

if __name__ == "__main__":
    unittest.main()

class ScenarioProjectionGuiEventIntegrationTests(unittest.TestCase):
    def setUp(self):
        import shutil
        import tempfile
        self._tempdir = tempfile.TemporaryDirectory()
        source = Path(__file__).resolve().parents[1] / "data" / "assumptions.json"
        target = Path(self._tempdir.name) / "assumptions.json"
        shutil.copy2(source, target)
        self._assumptions_path = target

    def tearDown(self):
        self._tempdir.cleanup()

    def _application(self):
        from planner.gui.scenario_projection_application import ScenarioProjectionApplication
        return ScenarioProjectionApplication(Assumptions(str(self._assumptions_path)))

    def _window(self):
        from planner.gui.scenario_projection_window import ScenarioProjectionWindow
        from planner.gui.event_services import RecordingEventService
        from planner.gui.testability import RecordingDialog
        app = self._application()
        view = app.build_view_model(
            allocations={"Aviva": 0.75, "Sky": 0.25},
            fund_returns={"Aviva": [0.10, 0.02, 0.08], "Sky": [0.20, 0.04, 0.16]},
        )
        window = ScenarioProjectionWindow(
            view,
            root=_FakeRoot(),
            application=app,
            allocations={"Aviva": 0.75, "Sky": 0.25},
            fund_returns={"Aviva": [0.10, 0.02, 0.08], "Sky": [0.20, 0.04, 0.16]},
            dialog=RecordingDialog(),
            event_service=RecordingEventService(),
        )
        return window

    def _controls(self, window, pension="660000", retirement="63", end_age="90", selected=("central",)):
        window._pension_var = _FakeVar(pension)
        window._retirement_age_var = _FakeVar(retirement)
        window._end_age_var = _FakeVar(end_age)
        window._scenario_vars = {
            name: _FakeVar(name in selected)
            for name in ("conservative", "central", "optimistic")
        }

    def test_button_and_event_dispatch_share_the_same_workflow_gate(self):
        window = self._window()
        self._controls(window, pension="700000", retirement="64", end_age="92", selected=("central",))
        calls = []
        window._run_projection = lambda: calls.append("run")
        window._run_from_button()
        window._run_from_event()
        self.assertEqual(calls, ["run", "run"])

    def test_workflow_action_handler_map_is_canonical(self):
        window = self._window()
        handlers = window._workflow_action_handlers()
        self.assertEqual(set(handlers), {"run", "save", "reset", "reload"})
        for action, method_name in (("run", "_run_projection"), ("save", "_save_assumptions"), ("reset", "_reset_inputs"), ("reload", "_reload_saved_assumptions")):
            resolved = handlers[action]
            expected = getattr(window, method_name)
            self.assertIs(resolved.__self__, expected.__self__)
            self.assertIs(resolved.__func__, expected.__func__)

    def test_dispatch_resolves_canonical_handler_when_not_injected(self):
        window = self._window()
        self._controls(window, pension="700000", retirement="64", end_age="92", selected=("central",))
        calls = []
        window._run_projection = lambda: calls.append("run")
        self.assertTrue(window._dispatch_workflow_action("run"))
        self.assertEqual(calls, ["run"])

    def test_button_and_event_entry_points_resolve_action_without_handler_pairing(self):
        window = self._window()
        self._controls(window, pension="700000", retirement="64", end_age="92", selected=("central",))
        calls = []
        window._run_projection = lambda: calls.append("run")
        window._run_from_button()
        window._run_from_event()
        self.assertEqual(calls, ["run", "run"])

    def test_button_and_event_entry_points_return_the_shared_dispatch_outcome(self):
        window = self._window()
        self._controls(window, pension="700000", retirement="64", end_age="92", selected=("central",))
        window._run_projection = lambda: None
        self.assertTrue(window._run_from_button())
        self.assertTrue(window._run_from_event())

        clean = self._window()
        self._controls(clean, selected=("conservative", "central", "optimistic"))
        self.assertFalse(clean._run_from_button())
        self.assertFalse(clean._run_from_event())

    def test_all_button_and_event_entry_points_use_canonical_action_names(self):
        window = self._window()
        calls = []
        window._dispatch_workflow_action = lambda action: calls.append(action) or True
        for entry_point, expected in (
            (window._run_from_button, "run"),
            (window._save_from_button, "save"),
            (window._reset_from_button, "reset"),
            (window._reload_from_button, "reload"),
            (window._run_from_event, "run"),
            (window._save_from_event, "save"),
            (window._reset_from_event, "reset"),
            (window._reload_from_event, "reload"),
        ):
            self.assertTrue(entry_point())
            self.assertEqual(calls[-1], expected)
        self.assertEqual(calls, ["run", "save", "reset", "reload", "run", "save", "reset", "reload"])

    def test_dispatch_blocks_unknown_workflow_action_before_handler(self):
        window = self._window()
        calls = []
        with self.assertRaises(ValueError):
            window._dispatch_workflow_action("export", lambda: calls.append("export"))
        self.assertEqual(calls, [])

    def test_dispatch_rejects_non_string_workflow_action_before_refresh(self):
        window = self._window()
        calls = []
        original = window._refresh_status
        window._refresh_status = lambda: calls.append("refresh")
        with self.assertRaises(ValueError):
            window._dispatch_workflow_action(["run"], lambda: calls.append("handler"))
        self.assertEqual(calls, [])
        window._refresh_status = original

    def test_dispatch_rejects_non_callable_injected_handler_before_refresh(self):
        window = self._window()
        calls = []
        original = window._refresh_status
        window._refresh_status = lambda: calls.append("refresh")
        with self.assertRaises(TypeError):
            window._dispatch_workflow_action("run", object())
        self.assertEqual(calls, [])
        window._refresh_status = original

    def test_dispatch_returns_false_when_action_is_not_permitted(self):
        window = self._window()
        self._controls(window, selected=("conservative", "central", "optimistic"))
        calls = []
        self.assertFalse(window._dispatch_workflow_action("run", lambda: calls.append("run")))
        self.assertEqual(calls, [])

    def test_button_entry_point_preserves_handler_exception_and_resynchronises(self):
        window = self._window()
        self._controls(window, pension="700000", retirement="64", end_age="92", selected=("central",))
        refreshes = []
        original_refresh = window._refresh_status
        window._refresh_status = lambda: (refreshes.append("refresh"), original_refresh())[1]

        def handler():
            window._pension_var.set("not-money")
            raise RuntimeError("button entry failure")

        window._run_projection = handler
        with self.assertRaisesRegex(RuntimeError, "button entry failure"):
            window._run_from_button()
        self.assertGreaterEqual(len(refreshes), 2)
        self.assertTrue(window.workflow_state.pending_changes)
        self.assertFalse(window.workflow_state.run_enabled)
        self.assertEqual(window.workflow_state.status, "Input needs attention")

    def test_event_entry_point_preserves_handler_exception_and_resynchronises(self):
        window = self._window()
        self._controls(window, pension="700000", retirement="64", end_age="92", selected=("central",))
        refreshes = []
        original_refresh = window._refresh_status
        window._refresh_status = lambda: (refreshes.append("refresh"), original_refresh())[1]

        def handler():
            window._retirement_age_var.set("not-an-age")
            raise RuntimeError("event entry failure")

        window._run_projection = handler
        with self.assertRaisesRegex(RuntimeError, "event entry failure"):
            window._run_from_event()
        self.assertGreaterEqual(len(refreshes), 2)
        self.assertTrue(window.workflow_state.pending_changes)
        self.assertFalse(window.workflow_state.run_enabled)
        self.assertEqual(window.workflow_state.status, "Input needs attention")

    def test_dispatch_resynchronises_after_handler_raises(self):
        window = self._window()
        self._controls(window, pension="700000", retirement="64", end_age="92", selected=("central",))
        window._refresh_status()

        def handler():
            window._pension_var.set("not-money")
            raise RuntimeError("simulated presentation failure")

        with self.assertRaisesRegex(RuntimeError, "simulated presentation failure"):
            window._dispatch_workflow_action("run", handler)
        self.assertTrue(window.workflow_state.pending_changes)
        self.assertFalse(window.workflow_state.run_enabled)
        self.assertEqual(window.workflow_state.status, "Input needs attention")

    def test_dispatch_returns_true_and_resynchronises_after_handler(self):
        window = self._window()
        self._controls(window, pension="700000", retirement="64", end_age="92", selected=("central",))
        def handler():
            window._pension_var.set("660000")
            window._retirement_age_var.set("63")
            window._end_age_var.set("90")
            for name, variable in window._scenario_vars.items():
                variable.set(name in ("conservative", "central", "optimistic"))
        self.assertTrue(window._dispatch_workflow_action("run", handler))
        self.assertFalse(window.workflow_state.pending_changes)
        self.assertFalse(window.workflow_state.run_enabled)
        self.assertFalse(window.workflow_state.reset_enabled)

    def test_dispatch_resynchronises_after_save_handler_completes_persistence(self):
        window = self._window()
        window.application.assumptions.set("starting_pension", 700000.0)
        self._controls(window, pension="700000", retirement="63", end_age="90", selected=("conservative", "central", "optimistic"))
        window._refresh_status()
        self.assertTrue(window.workflow_state.save_enabled)
        def handler():
            window.application.assumptions.reset_change_tracking()
        self.assertTrue(window._dispatch_workflow_action("save", handler))
        self.assertFalse(window.workflow_state.pending_changes)
        self.assertFalse(window.workflow_state.save_enabled)
        self.assertEqual(window.workflow_state.status, "Saved assumptions")

    def test_button_run_does_not_bypass_disabled_workflow_action(self):
        window = self._window()
        self._controls(window, pension="660000", retirement="63", end_age="90", selected=("conservative", "central", "optimistic"))
        original = window.view_model
        window._run_from_button()
        self.assertIs(window.view_model, original)

    def test_button_run_allows_valid_pending_workflow_action(self):
        window = self._window()
        self._controls(window, pension="700000", retirement="64", end_age="92", selected=("central",))
        calls = []
        window._run_projection = lambda: calls.append("run")
        window._run_from_button()
        self.assertEqual(calls, ["run"])

    def test_button_save_does_not_bypass_pending_edit(self):
        window = self._window()
        self._controls(window, pension="700000", retirement="64", end_age="92", selected=("central",))
        calls = []
        window._save_assumptions = lambda: calls.append("save")
        window._save_from_button()
        self.assertEqual(calls, [])

    def test_button_reset_does_not_bypass_clean_state(self):
        window = self._window()
        self._controls(window, selected=("conservative", "central", "optimistic"))
        calls = []
        window._reset_inputs = lambda: calls.append("reset")
        window._reset_from_button()
        self.assertEqual(calls, [])

    def test_button_reload_remains_available_in_clean_state(self):
        window = self._window()
        self._controls(window)
        calls = []
        window._reload_saved_assumptions = lambda: calls.append("reload")
        window._reload_from_button()
        self.assertEqual(calls, ["reload"])

    def test_all_button_and_event_entry_points_are_terminal_after_close(self):
        window = self._window()
        self._controls(window, pension="700000", retirement="64", end_age="92", selected=("central",))
        calls = []
        window._run_projection = lambda: calls.append("run")
        window._save_assumptions = lambda: calls.append("save")
        window._reset_inputs = lambda: calls.append("reset")
        window._reload_saved_assumptions = lambda: calls.append("reload")
        window.close()

        for entry_point in (
            window._run_from_button,
            window._save_from_button,
            window._reset_from_button,
            window._reload_from_button,
            window._run_from_event,
            window._save_from_event,
            window._reset_from_event,
            window._reload_from_event,
        ):
            self.assertFalse(entry_point())

        self.assertEqual(calls, [])
        self.assertTrue(window.is_closed)

    def test_keyboard_binding_is_terminal_after_close(self):
        window = self._window()
        from planner.gui.event_services import RecordingEventService
        service = RecordingEventService()
        window._event_service = service
        window.close()
        window._bind_keyboard_shortcuts()
        self.assertEqual(service.bindings, {})

    def test_keyboard_binding_contract_covers_each_workflow_action(self):
        window = self._window()
        contract = window._keyboard_binding_contract()
        self.assertEqual(
            {action for _event, action, _handler in contract},
            set(WORKFLOW_ACTIONS),
        )
        self.assertTrue(all(callable(handler) for _event, _action, handler in contract))

    def test_keyboard_binding_contract_rejects_duplicate_event_action_pairs(self):
        window = self._window()
        original = window.__class__.__dict__["_bind_keyboard_shortcuts"]
        from planner.gui.scenario_projection_window import WORKFLOW_KEYBOARD_BINDINGS
        try:
            import planner.gui.scenario_projection_window as module
            module.WORKFLOW_KEYBOARD_BINDINGS = WORKFLOW_KEYBOARD_BINDINGS + (
                WORKFLOW_KEYBOARD_BINDINGS[0],
            )
            with self.assertRaisesRegex(RuntimeError, "duplicate event/action pair"):
                window._keyboard_binding_contract()
        finally:
            module.WORKFLOW_KEYBOARD_BINDINGS = WORKFLOW_KEYBOARD_BINDINGS
        self.assertIsNotNone(original)

    def test_keyboard_binding_publication_is_atomic_on_invalid_action_contract(self):
        window = self._window()
        from planner.gui.event_services import RecordingEventService
        import planner.gui.scenario_projection_window as module
        original = module.WORKFLOW_KEYBOARD_BINDINGS
        service = RecordingEventService()
        window._event_service = service
        module.WORKFLOW_KEYBOARD_BINDINGS = original + (("<Alt-x>", "export", "_run_from_event"),)
        try:
            with self.assertRaisesRegex(RuntimeError, "outside canonical workflow actions"):
                window._bind_keyboard_shortcuts()
        finally:
            module.WORKFLOW_KEYBOARD_BINDINGS = original
        self.assertEqual(service.bindings, {})

    def test_keyboard_binding_publication_is_atomic_on_invalid_handler_contract(self):
        window = self._window()
        from planner.gui.event_services import RecordingEventService
        import planner.gui.scenario_projection_window as module
        original = module.WORKFLOW_KEYBOARD_BINDINGS
        service = RecordingEventService()
        window._event_service = service
        module.WORKFLOW_KEYBOARD_BINDINGS = original + (("<Alt-x>", "run", "_missing_handler"),)
        try:
            with self.assertRaisesRegex(RuntimeError, "handler is not callable"):
                window._bind_keyboard_shortcuts()
        finally:
            module.WORKFLOW_KEYBOARD_BINDINGS = original
        self.assertEqual(service.bindings, {})

    def test_keyboard_binding_is_idempotent_for_same_event_service(self):
        window = self._window()
        from planner.gui.event_services import RecordingEventService
        service = RecordingEventService()
        window._event_service = service
        window._bind_keyboard_shortcuts()
        callbacks = dict(service.bindings)
        window._bind_keyboard_shortcuts()
        self.assertEqual(set(service.bindings), {"<Return>", "<Escape>", "<Alt-r>", "<Alt-s>", "<Alt-t>", "<Alt-l>"})
        for event, callback in callbacks.items():
            self.assertIs(service.bindings[event], callback)

    def test_keyboard_binding_rewires_when_event_service_changes(self):
        window = self._window()
        from planner.gui.event_services import RecordingEventService
        first = RecordingEventService()
        second = RecordingEventService()
        window._event_service = first
        window._bind_keyboard_shortcuts()
        window._event_service = second
        window._bind_keyboard_shortcuts()
        self.assertEqual(set(first.bindings), {"<Return>", "<Escape>", "<Alt-r>", "<Alt-s>", "<Alt-t>", "<Alt-l>"})
        self.assertEqual(set(second.bindings), {"<Return>", "<Escape>", "<Alt-r>", "<Alt-s>", "<Alt-t>", "<Alt-l>"})
        self.assertIsNot(first.bindings["<Return>"], second.bindings["<Return>"])

    def test_input_change_callback_is_terminal_after_close(self):
        window = self._window()
        window.close()
        refreshes = []
        window._refresh_status = lambda: refreshes.append(True)
        window._on_input_change()
        self.assertEqual(refreshes, [])

    def test_all_event_entry_points_share_blocked_workflow_state(self):
        window = self._window()
        self._controls(window, selected=("conservative", "central", "optimistic"))
        calls = []
        window._run_projection = lambda: calls.append("run")
        window._save_assumptions = lambda: calls.append("save")
        window._reset_inputs = lambda: calls.append("reset")
        window._reload_saved_assumptions = lambda: calls.append("reload")
        window._refresh_status()

        self.assertFalse(window._run_from_event())
        self.assertFalse(window._save_from_event())
        self.assertFalse(window._reset_from_event())
        self.assertTrue(window._reload_from_event())
        self.assertEqual(calls, ["reload"])

    def test_button_actions_are_blocked_after_close(self):
        window = self._window()
        self._controls(window, pension="700000", retirement="64", end_age="92", selected=("central",))
        calls = []
        window._run_projection = lambda: calls.append("run")
        window._save_assumptions = lambda: calls.append("save")
        window._reset_inputs = lambda: calls.append("reset")
        window._reload_saved_assumptions = lambda: calls.append("reload")
        window.close()
        window._run_from_button()
        window._save_from_button()
        window._reset_from_button()
        window._reload_from_button()
        self.assertEqual(calls, [])

    def test_recording_event_service_triggers_keyboard_binding(self):
        window = self._window()
        self._controls(window, selected=("central",))
        calls = []
        window._run_projection = lambda: calls.append("run")
        window._bind_keyboard_shortcuts()
        window._event_service.trigger("<Return>")
        self.assertEqual(calls, ["run"])

    def test_return_event_runs_projection_and_refreshes_view_model(self):
        window = self._window()
        self._controls(window, pension="700000", retirement="64", end_age="92", selected=("central",))
        refreshed = []
        window._refresh_results = lambda: refreshed.append(window.view_model.scenario_names)
        window._bind_keyboard_shortcuts()
        window._event_service.trigger("<Return>")
        self.assertEqual(window.view_model.scenario_names, ("central",))
        self.assertEqual(refreshed, [("central",)])

    def test_return_event_does_not_bypass_disabled_run_for_invalid_input(self):
        window = self._window()
        self._controls(window, pension="not-money")
        window._bind_keyboard_shortcuts()
        window._event_service.trigger("<Return>")
        self.assertEqual(window.workflow_state.status, "Input needs attention")
        self.assertEqual(window._dialog.errors, [])

    def test_return_event_does_not_bypass_disabled_run_when_clean(self):
        window = self._window()
        self._controls(window, pension="660000", retirement="63", end_age="90", selected=("conservative", "central", "optimistic"))
        window._bind_keyboard_shortcuts()
        original = window.view_model
        window._event_service.trigger("<Return>")
        self.assertIs(window.view_model, original)

    def test_alt_s_event_does_not_bypass_disabled_save_with_pending_edit(self):
        window = self._window()
        self._controls(window, pension="700000", retirement="64", end_age="92", selected=("central",))
        window._bind_keyboard_shortcuts()
        window._event_service.trigger("<Alt-s>")
        self.assertTrue(window.has_pending_changes)
        self.assertTrue(window.is_dirty is False)
        self.assertEqual(window._dialog.infos, [])

    def test_alt_s_event_saves_and_records_info(self):
        window = self._window()
        self._controls(window, pension="700000", retirement="64", end_age="92", selected=("central",))
        window._run_projection()
        window._bind_keyboard_shortcuts()
        window._event_service.trigger("<Alt-s>")
        self.assertFalse(window.is_dirty)
        self.assertEqual(window._dialog.infos[-1][0], "Assumptions saved")

    def test_alt_t_event_resets_controls_to_applied_state(self):
        window = self._window()
        self._controls(window, pension="700000", retirement="64", end_age="92", selected=("central",))
        window._run_projection()
        self._controls(window, pension="710000", retirement="65", end_age="93", selected=("optimistic",))
        window._bind_keyboard_shortcuts()
        window._event_service.trigger("<Alt-t>")
        self.assertEqual(window._current_input_strings(), ("700000.0", "64", "92", ("central",)))

    def test_reset_shortcut_resynchronises_workflow_state(self):
        window = self._window()
        self._controls(window, pension="700000", retirement="64", end_age="92", selected=("central",))
        window._run_projection()
        self._controls(window, pension="710000", retirement="65", end_age="93", selected=("optimistic",))
        window._bind_keyboard_shortcuts()
        self.assertTrue(window.has_pending_changes)
        window._event_service.trigger("<Alt-t>")
        self.assertFalse(window.workflow_state.pending_changes)
        self.assertFalse(window.workflow_state.run_enabled)
        self.assertFalse(window.workflow_state.reset_enabled)
        self.assertEqual(window.workflow_state.status, "Unsaved changes")

    def test_alt_l_event_reloads_saved_assumptions_headlessly(self):
        window = self._window()
        self._controls(window, pension="700000", retirement="64", end_age="92", selected=("central",))
        window._run_projection()
        window._run_projection = window._run_projection
        window._bind_keyboard_shortcuts()
        window._event_service.trigger("<Alt-s>")
        self._controls(window, pension="710000", retirement="65", end_age="93", selected=("optimistic",))
        window._event_service.trigger("<Alt-l>")
        self.assertEqual(window.application.inputs().starting_pension, 700000.0)
        self.assertEqual(window.application.inputs().retirement_age, 64)
        self.assertEqual(window.application.inputs().projection_end_age, 92)
        self.assertEqual(window.selected_scenarios, ("conservative", "central", "optimistic"))
        self.assertFalse(window.is_dirty)

    def test_escape_event_after_close_is_safe(self):
        window = self._window()
        self._controls(window)
        window._bind_keyboard_shortcuts()
        window.close()
        window._event_service.trigger("<Escape>")
        self.assertTrue(window.is_closed)
        self.assertTrue(window._root.destroyed)

    def test_reload_event_error_is_recorded_without_tk_dialog(self):
        window = self._window()
        window.application.assumptions.set("starting_pension", 700000.0)
        original = window.controller.reload_saved
        window.controller.reload_saved = lambda: (_ for _ in ()).throw(OSError("reload failed"))
        window._bind_keyboard_shortcuts()
        window._event_service.trigger("<Alt-l>")
        self.assertEqual(window._dialog.errors[-1], ("Could not reload assumptions", "reload failed"))
        window.controller.reload_saved = original

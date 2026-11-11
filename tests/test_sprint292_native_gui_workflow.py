"""Sprint 292: native Tk integration coverage for scenario projection workflows.

The tests exercise the actual projection window and its ttk controls while
isolating persistence in a temporary assumptions document.
"""
from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

try:
    import tkinter as tk
    from tkinter import ttk
except ImportError:
    tk = None
    ttk = None

from planner.assumptions import Assumptions
from planner.gui.scenario_projection_application import ScenarioProjectionApplication
from planner.gui.scenario_projection_window import ScenarioProjectionWindow
from planner.gui.testability import RecordingDialog


ROOT = Path(__file__).resolve().parents[1]
ALLOCATIONS = {"Aviva": 0.75, "Sky": 0.25}
FUND_RETURNS = {
    "Aviva": [0.10, 0.02, 0.08],
    "Sky": [0.20, 0.04, 0.16],
}


class Sprint292NativeProjectionWorkflowTests(unittest.TestCase):
    """Drive real Tk variables, buttons, checkbuttons and result widgets."""

    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.path = Path(self.tempdir.name) / "assumptions.json"
        shutil.copy2(ROOT / "data" / "assumptions.json", self.path)
        self.disk_baseline = self.path.read_bytes()

        if tk is None or ttk is None:
            self.tempdir.cleanup()
            self.skipTest("Tkinter is not installed in this Python environment")
        try:
            self.root = tk.Tk()
        except (tk.TclError, RuntimeError) as exc:
            self.tempdir.cleanup()
            self.skipTest(f"Tk display is unavailable: {exc}")
        self.root.withdraw()

        self.dialog = RecordingDialog()
        self.application = ScenarioProjectionApplication(Assumptions(str(self.path)))
        self.initial_inputs = self.application.inputs()
        self.initial_view = self.application.build_view_model(
            allocations=ALLOCATIONS,
            fund_returns=FUND_RETURNS,
        )
        self.window = ScenarioProjectionWindow(
            self.initial_view,
            root=self.root,
            application=self.application,
            allocations=ALLOCATIONS,
            fund_returns=FUND_RETURNS,
            dialog=self.dialog,
        )
        self.window.build()
        self.root.update_idletasks()

    def tearDown(self) -> None:
        try:
            if tk is not None and getattr(self, "root", None) is not None:
                self.root.destroy()
        except tk.TclError:
            pass
        self.tempdir.cleanup()

    def _run_button(self) -> ttk.Button:
        self.assertIsInstance(self.window._run_button, ttk.Button)
        return self.window._run_button

    def _save_button(self) -> ttk.Button:
        self.assertIsInstance(self.window._save_button, ttk.Button)
        return self.window._save_button

    def _reset_button(self) -> ttk.Button:
        self.assertIsInstance(self.window._reset_button, ttk.Button)
        return self.window._reset_button

    def _reload_button(self) -> ttk.Button:
        self.assertIsInstance(self.window._reload_button, ttk.Button)
        return self.window._reload_button

    def test_build_exposes_native_inputs_scenario_controls_and_workflow_actions(self) -> None:
        self.assertEqual(self.root.title(), "Retirement Scenario Comparison")
        self.assertIsInstance(self.window._entry_widgets[0], ttk.Entry)
        self.assertIsInstance(self.window._entry_widgets[1], ttk.Entry)
        self.assertIsInstance(self.window._entry_widgets[2], ttk.Entry)
        self.assertEqual(
            set(self.window._scenario_checkbuttons),
            {"conservative", "central", "optimistic"},
        )
        self.assertTrue(all(isinstance(item, ttk.Checkbutton) for item in self.window._scenario_checkbuttons.values()))
        self.assertIsInstance(self._run_button(), ttk.Button)
        self.assertIsInstance(self._save_button(), ttk.Button)
        self.assertIsInstance(self._reset_button(), ttk.Button)
        self.assertIsInstance(self._reload_button(), ttk.Button)
        self.assertEqual(self.window.pending_selected_scenarios, self.initial_inputs.scenarios)
        self.assertTrue(self.window.results_are_current)

    def test_editing_pension_and_retirement_age_marks_results_stale_until_run(self) -> None:
        self.window._pension_var.set("700000")
        self.window._retirement_age_var.set(str(self.initial_inputs.retirement_age + 1))
        self.root.update_idletasks()

        self.assertTrue(self.window.has_pending_changes)
        self.assertFalse(self.window.results_are_current)
        self.assertTrue(self.window.workflow_state.run_enabled)
        self.assertFalse(self.window.workflow_state.save_enabled)
        self.assertIn("stale", self.window._results_status_var.get().lower())

        self._run_button().invoke()
        self.root.update_idletasks()

        self.assertFalse(self.window.has_pending_changes)
        self.assertTrue(self.window.results_are_current)
        self.assertEqual(self.application.inputs().starting_pension, 700000.0)
        self.assertEqual(
            self.application.inputs().retirement_age,
            self.initial_inputs.retirement_age + 1,
        )
        self.assertTrue(self.window.workflow_state.save_enabled)
        self.assertEqual(self.window.view_model.scenario_names, self.initial_inputs.scenarios)

    def test_scenario_checkbuttons_change_selection_and_projection_results(self) -> None:
        self.window._scenario_checkbuttons["optimistic"].invoke()
        self.window._scenario_checkbuttons["conservative"].invoke()
        self.root.update_idletasks()

        self.assertEqual(self.window.pending_selected_scenarios, ("central",))
        self.assertFalse(self.window.results_are_current)
        self.assertTrue(self.window.workflow_state.run_enabled)

        self._run_button().invoke()
        self.root.update_idletasks()

        self.assertEqual(self.window.selected_scenarios, ("central",))
        self.assertEqual(self.window.view_model.scenario_names, ("central",))
        self.assertTrue(self.window.results_are_current)

    def test_invalid_input_is_rejected_and_does_not_replace_previous_projection(self) -> None:
        previous_view = self.window.view_model
        previous_inputs = self.application.inputs()
        self.window._pension_var.set("-1")
        self.root.update_idletasks()

        self.assertTrue(self.window.has_pending_changes)
        self.assertFalse(self.window.workflow_state.run_enabled)
        self.assertIn("attention", self.window.workflow_state.status.lower())
        self.assertIs(self.window.view_model, previous_view)
        self.assertEqual(self.application.inputs(), previous_inputs)
        self.assertEqual(self.path.read_bytes(), self.disk_baseline)

    def test_reset_restores_applied_values_without_persisting_pending_edits(self) -> None:
        self.window._pension_var.set("710000")
        self.window._retirement_age_var.set(str(self.initial_inputs.retirement_age + 2))
        self.root.update_idletasks()
        self.assertTrue(self.window.workflow_state.reset_enabled)

        self._reset_button().invoke()
        self.root.update_idletasks()

        self.assertEqual(self.window._pension_var.get(), str(self.initial_inputs.starting_pension))
        self.assertEqual(self.window._retirement_age_var.get(), str(self.initial_inputs.retirement_age))
        self.assertFalse(self.window.has_pending_changes)
        self.assertTrue(self.window.results_are_current)
        self.assertEqual(self.path.read_bytes(), self.disk_baseline)

    def test_save_persists_successfully_run_inputs_only_after_explicit_action(self) -> None:
        self.window._pension_var.set("720000")
        self.root.update_idletasks()
        self._run_button().invoke()
        self.root.update_idletasks()

        # Run applies the new value in memory; persistence remains explicit.
        self.assertEqual(self.path.read_bytes(), self.disk_baseline)
        self.assertEqual(self.application.inputs().starting_pension, 720000.0)
        self.assertTrue(self.application.assumptions.has_changes())
        self.assertTrue(self.window.workflow_state.save_enabled)

        self._save_button().invoke()
        self.root.update_idletasks()

        self.assertEqual(
            float(Assumptions(str(self.path)).get("starting_pension")),
            720000.0,
        )
        self.assertFalse(self.application.assumptions.has_changes())
        self.assertFalse(self.window.workflow_state.save_enabled)
        self.assertTrue(self.dialog.infos)

    def test_reload_restores_last_saved_inputs_and_rebuilds_current_results(self) -> None:
        self.window._pension_var.set("730000")
        self.root.update_idletasks()
        self._run_button().invoke()
        self.root.update_idletasks()
        self._save_button().invoke()
        self.root.update_idletasks()
        saved_bytes = self.path.read_bytes()

        self.window._pension_var.set("810000")
        self.root.update_idletasks()
        self._run_button().invoke()
        self.root.update_idletasks()
        self.assertEqual(self.application.inputs().starting_pension, 810000.0)

        self._reload_button().invoke()
        self.root.update_idletasks()

        self.assertEqual(self.application.inputs().starting_pension, 730000.0)
        self.assertEqual(self.window._pension_var.get(), "730000.0")
        self.assertEqual(self.path.read_bytes(), saved_bytes)
        self.assertTrue(self.window.results_are_current)
        self.assertFalse(self.application.assumptions.has_changes())


if __name__ == "__main__":
    unittest.main()

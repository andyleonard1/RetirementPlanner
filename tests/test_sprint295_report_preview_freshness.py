"""Sprint 295: report preview freshness and window lifecycle tests.

The tests exercise native Tk controls and ensure a preview never outlives the
published projection result from which its report text was produced.
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
from planner.gui.testability import RecordingDialog, RecordingFileDialog


ROOT = Path(__file__).resolve().parents[1]
ALLOCATIONS = {"Aviva": 0.75, "Sky": 0.25}
FUND_RETURNS = {
    "Aviva": (0.10, 0.02, 0.08),
    "Sky": (0.20, 0.04, 0.16),
}


class Sprint295ReportPreviewFreshnessTests(unittest.TestCase):
    """Verify preview lifecycle follows the current published projection."""

    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.directory = Path(self.tempdir.name)
        assumptions_path = self.directory / "assumptions.json"
        shutil.copy2(ROOT / "data" / "assumptions.json", assumptions_path)

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
        self.file_dialog = RecordingFileDialog(str(self.directory))
        self.application = ScenarioProjectionApplication(Assumptions(str(assumptions_path)))
        self.initial_inputs = self.application.inputs()
        view_model = self.application.build_view_model(
            allocations=ALLOCATIONS,
            fund_returns=FUND_RETURNS,
        )
        self.window = ScenarioProjectionWindow(
            view_model,
            root=self.root,
            application=self.application,
            allocations=ALLOCATIONS,
            fund_returns=FUND_RETURNS,
            dialog=self.dialog,
            file_dialog=self.file_dialog,
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

    def _run_projection(self) -> None:
        self.window._pension_var.set(
            str(self.initial_inputs.starting_pension + 1000)
        )
        self.root.update_idletasks()
        self.assertTrue(self.window.workflow_state.run_enabled)
        self.window._run_button.invoke()
        self.root.update_idletasks()
        self.assertTrue(self.window.results_are_current)
        self.assertIsNotNone(self.window._last_workflow_result)

    def _open_preview(self):
        button = self.window._report_preview_button
        self.assertIsInstance(button, ttk.Button)
        self.assertEqual(str(button.cget("state")), "normal")
        button.invoke()
        self.root.update_idletasks()
        preview = self.window._report_preview_window
        self.assertIsNotNone(preview)
        self.assertTrue(preview.winfo_exists())
        return preview

    def _find_close_button(self, widget):
        for child in widget.winfo_children():
            if isinstance(child, ttk.Button) and child.cget("text") == "Close":
                return child
            found = self._find_close_button(child)
            if found is not None:
                return found
        return None

    def test_stale_inputs_close_open_preview_and_clear_references(self) -> None:
        self._run_projection()
        preview = self._open_preview()
        self.assertIs(self.window._report_preview_window, preview)

        self.window._pension_var.set(str(self.initial_inputs.starting_pension + 2000))
        self.root.update_idletasks()

        self.assertFalse(self.window.results_are_current)
        self.assertFalse(preview.winfo_exists())
        self.assertIsNone(self.window._report_preview_window)
        self.assertIsNone(self.window._report_preview_text)
        self.assertIn("stale", self.window._report_status_var.get().lower())

    def test_new_projection_allows_a_fresh_preview_without_extra_calculation(self) -> None:
        self._run_projection()
        old_preview = self._open_preview()

        self.window._pension_var.set(str(self.initial_inputs.starting_pension + 2000))
        self.root.update_idletasks()
        self.assertFalse(old_preview.winfo_exists())

        self.window._run_button.invoke()
        self.root.update_idletasks()
        self.assertTrue(self.window.results_are_current)
        expected_text = self.window.current_result_report_text()

        run_calls = []
        original_run = self.window.controller.run

        def counted_run(*args, **kwargs):
            run_calls.append((args, kwargs))
            return original_run(*args, **kwargs)

        self.window.controller.run = counted_run
        new_preview = self._open_preview()

        self.assertIsNot(new_preview, old_preview)
        self.assertEqual(
            self.window._report_preview_text.get("1.0", "end-1c"),
            expected_text,
        )
        self.assertEqual(run_calls, [])

    def test_closing_preview_button_clears_references_and_allows_reopening(self) -> None:
        self._run_projection()
        first_preview = self._open_preview()
        close_button = self._find_close_button(first_preview)
        self.assertIsNotNone(close_button)

        close_button.invoke()
        self.root.update_idletasks()

        self.assertFalse(first_preview.winfo_exists())
        self.assertIsNone(self.window._report_preview_window)
        self.assertIsNone(self.window._report_preview_text)

        second_preview = self._open_preview()
        self.assertIsNot(second_preview, first_preview)
        self.assertTrue(second_preview.winfo_exists())


if __name__ == "__main__":
    unittest.main()

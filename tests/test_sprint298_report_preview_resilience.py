"""Sprint 298: report preview state and error resilience tests.

Verify failures and unavailable projection results are reported safely, and a
later successful retry presents only the current report.
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


class Sprint298ReportPreviewResilienceTests(unittest.TestCase):
    """Exercise preview failures and recovery through the native Tk window."""

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
        self.allocations = dict(ALLOCATIONS)
        self.fund_returns = dict(FUND_RETURNS)
        view_model = self.application.build_view_model(
            allocations=self.allocations,
            fund_returns=self.fund_returns,
        )
        self.window = ScenarioProjectionWindow(
            view_model,
            root=self.root,
            application=self.application,
            allocations=self.allocations,
            fund_returns=self.fund_returns,
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

    def _run_projection(self, pension_delta: float = 1000) -> object:
        self.window._pension_var.set(
            str(self.initial_inputs.starting_pension + pension_delta)
        )
        self.root.update_idletasks()
        self.assertTrue(self.window.workflow_state.run_enabled)
        self.window._run_button.invoke()
        self.root.update_idletasks()
        self.assertTrue(self.window.results_are_current)
        result = self.window._last_workflow_result
        self.assertIsNotNone(result)
        return result

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

    def test_report_generation_exceptions_are_reported_without_opening_preview(self) -> None:
        self._run_projection()

        for error in (RuntimeError("report service unavailable"), ValueError("invalid report data"),
                      TypeError("unexpected report value")):
            with self.subTest(error=type(error).__name__):
                self.window.current_result_report_text = lambda error=error: (_ for _ in ()).throw(error)

                opened = self.window._preview_report()
                self.root.update_idletasks()

                self.assertFalse(opened)
                self.assertIsNone(self.window._report_preview_window)
                self.assertIsNone(self.window._report_preview_text)
                self.assertIn(str(error), self.window._report_status_var.get())

    def test_preview_can_be_retried_successfully_after_transient_report_error(self) -> None:
        result = self._run_projection()
        expected_text = result.report_text
        attempts = {"count": 0}

        def report_text_with_transient_failure() -> str:
            attempts["count"] += 1
            if attempts["count"] == 1:
                raise RuntimeError("temporary report-generation failure")
            return expected_text

        self.window.current_result_report_text = report_text_with_transient_failure

        self.assertFalse(self.window._preview_report())
        self.assertIn("temporary report-generation failure", self.window._report_status_var.get())
        self.assertIsNone(self.window._report_preview_window)
        self.assertIsNone(self.window._report_preview_text)

        self.assertTrue(self.window._preview_report())
        self.root.update_idletasks()
        self.assertEqual(attempts["count"], 2)
        self.assertIsNotNone(self.window._report_preview_window)
        self.assertEqual(
            self.window._report_preview_text.get("1.0", "end-1c"),
            expected_text,
        )
        self.assertIn("opened", self.window._report_status_var.get().lower())

    def test_stale_projection_closes_existing_preview_and_blocks_reopening(self) -> None:
        self._run_projection()
        preview = self._open_preview()

        self.window._pension_var.set(str(self.initial_inputs.starting_pension + 2500))
        self.root.update_idletasks()

        self.assertFalse(preview.winfo_exists())
        self.assertIsNone(self.window._report_preview_window)
        self.assertIsNone(self.window._report_preview_text)
        self.assertFalse(self.window._preview_report())
        self.assertIsNone(self.window._report_preview_window)
        self.assertIsNone(self.window._report_preview_text)
        self.assertIn("stale", self.window._report_status_var.get().lower())

    def test_closed_projection_window_cannot_open_a_report_preview(self) -> None:
        self._run_projection()
        self.window.close()

        self.assertFalse(self.window._preview_report())
        self.assertIsNone(self.window._report_preview_window)
        self.assertIsNone(self.window._report_preview_text)


if __name__ == "__main__":
    unittest.main()

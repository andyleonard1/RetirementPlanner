"""Sprint 294: native Tk report preview and export feedback integration tests.

The tests drive real GUI controls while isolating filesystem and export
boundaries with temporary directories and injected exporters.
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


class Sprint294NativeGuiReportPreviewTests(unittest.TestCase):
    """Exercise report preview and export feedback through native Tk controls."""

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

    def _preview_button(self) -> ttk.Button:
        self.assertIsInstance(self.window._report_preview_button, ttk.Button)
        return self.window._report_preview_button

    def _reports_button(self) -> ttk.Button:
        self.assertIsInstance(self.window._reports_button, ttk.Button)
        return self.window._reports_button

    def _report_pack_button(self) -> ttk.Button:
        self.assertIsInstance(self.window._report_pack_button, ttk.Button)
        return self.window._report_pack_button

    def _feedback(self) -> str:
        return self.window._report_status_var.get()

    def test_build_exposes_native_preview_action_and_export_feedback(self) -> None:
        self.assertEqual(self._preview_button().cget("text"), "Preview report…")
        self.assertIsNotNone(self.window._report_status_var)
        self.assertEqual(self._feedback(), "Reports: ready to preview or export current results.")

    def test_preview_displays_published_report_text_without_recalculation(self) -> None:
        self._run_projection()
        expected_text = self.window.current_result_report_text()
        run_calls = []
        original_run = self.window.controller.run

        def counted_run(*args, **kwargs):
            run_calls.append((args, kwargs))
            return original_run(*args, **kwargs)

        self.window.controller.run = counted_run
        self._preview_button().invoke()
        self.root.update_idletasks()

        preview = self.window._report_preview_window
        self.assertIsNotNone(preview)
        self.assertTrue(preview.winfo_exists())
        self.assertEqual(preview.title(), "Retirement report preview")
        self.assertEqual(self.window._report_preview_text.get("1.0", "end-1c"), expected_text)
        self.assertEqual(str(self.window._report_preview_text.cget("state")), "disabled")
        self.assertEqual(run_calls, [])
        self.assertIn("preview", self._feedback().lower())

    def test_stale_results_disable_preview_and_do_not_open_a_window(self) -> None:
        self._run_projection()
        self.window._pension_var.set("765000")
        self.root.update_idletasks()

        self.assertFalse(self.window.results_are_current)
        self.assertEqual(str(self._preview_button().cget("state")), "disabled")
        self._preview_button().invoke()
        self.root.update_idletasks()

        self.assertIsNone(self.window._report_preview_window)
        self.assertFalse(self.dialog.errors)

    def test_closed_window_rejects_preview(self) -> None:
        self._run_projection()
        self.window.close()

        self.assertFalse(self.window._preview_report())
        self.assertIsNone(self.window._report_preview_window)

    def test_successful_report_suite_export_updates_inline_feedback(self) -> None:
        self._run_projection()
        report_path = self.directory / "retirement_scenario_projection.pdf"
        self.window._report_suite_exporter = lambda **kwargs: {"scenario": report_path}

        self._reports_button().invoke()
        self.root.update_idletasks()

        self.assertIn("exported", self._feedback().lower())
        self.assertIn(str(report_path), self._feedback())
        self.assertEqual(len(self.dialog.infos), 1)
        self.assertFalse(self.dialog.errors)

    def test_successful_report_pack_export_updates_inline_feedback(self) -> None:
        self._run_projection()
        suite_path = self.directory / "retirement_scenario_projection.pdf"
        pack_path = self.directory / "RetirementPlanner_Report_Pack.pdf"
        self.window._report_suite_exporter = lambda **kwargs: {"scenario": suite_path}
        self.window._report_pack_exporter = lambda suite, destination: destination

        self._report_pack_button().invoke()
        self.root.update_idletasks()

        self.assertIn("exported", self._feedback().lower())
        self.assertIn(str(pack_path), self._feedback())
        self.assertEqual(len(self.dialog.infos), 1)
        self.assertFalse(self.dialog.errors)

    def test_cancelled_export_updates_inline_feedback_without_calling_exporter(self) -> None:
        self._run_projection()
        self.file_dialog.directory = ""
        calls = []
        self.window._report_suite_exporter = lambda **kwargs: calls.append(kwargs)

        self._reports_button().invoke()
        self.root.update_idletasks()

        self.assertIn("cancel", self._feedback().lower())
        self.assertFalse(calls)
        self.assertFalse(self.dialog.errors)
        self.assertFalse(self.dialog.infos)

    def test_export_failure_updates_inline_feedback_and_keeps_error_dialog(self) -> None:
        self._run_projection()

        def failing_exporter(**kwargs):
            raise OSError("simulated PDF write failure")

        self.window._report_suite_exporter = failing_exporter
        self._reports_button().invoke()
        self.root.update_idletasks()

        self.assertIn("failed", self._feedback().lower())
        self.assertIn("simulated PDF write failure", self._feedback())
        self.assertEqual(self.dialog.errors[-1][0], "Could not export PDF reports")
        self.assertFalse(self.dialog.infos)


if __name__ == "__main__":
    unittest.main()

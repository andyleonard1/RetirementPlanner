"""Sprint 293: native Tk integration coverage for PDF report exports.

The tests exercise the real report-export buttons while injecting directory
selection and export services so no PDFs are written during GUI integration
tests.
"""
from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

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


class Sprint293NativeGuiReportExportTests(unittest.TestCase):
    """Drive native Tk report buttons and inspect their injected service calls."""

    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.directory = Path(self.tempdir.name)
        self.assumptions_path = self.directory / "assumptions.json"
        shutil.copy2(ROOT / "data" / "assumptions.json", self.assumptions_path)

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
        self.application = ScenarioProjectionApplication(
            Assumptions(str(self.assumptions_path))
        )
        self.initial_inputs = self.application.inputs()
        initial_view = self.application.build_view_model(
            allocations=ALLOCATIONS,
            fund_returns=FUND_RETURNS,
        )
        self.window = ScenarioProjectionWindow(
            initial_view,
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
        self.assertIsInstance(self.window._run_button, ttk.Button)
        # Run is intentionally disabled until the user changes an input.
        # Create a valid pending edit, then exercise the real native button.
        self.window._pension_var.set(
            str(self.initial_inputs.starting_pension + 1000)
        )
        self.root.update_idletasks()
        self.assertTrue(self.window.workflow_state.run_enabled)
        self.window._run_button.invoke()
        self.root.update_idletasks()
        self.assertTrue(self.window.results_are_current)
        self.assertIsNotNone(self.window._last_workflow_result)

    def _reports_button(self) -> ttk.Button:
        self.assertIsInstance(self.window._reports_button, ttk.Button)
        return self.window._reports_button

    def _report_pack_button(self) -> ttk.Button:
        self.assertIsInstance(self.window._report_pack_button, ttk.Button)
        return self.window._report_pack_button

    def test_build_exposes_native_report_export_buttons(self) -> None:
        self.assertIsInstance(self._reports_button(), ttk.Button)
        self.assertIsInstance(self._report_pack_button(), ttk.Button)
        self.assertEqual(self.window._reports_button.cget("text"), "Export PDF reports…")
        self.assertEqual(
            self.window._report_pack_button.cget("text"),
            "Export PDF report pack…",
        )

    def test_report_suite_button_uses_current_published_result_without_recalculation(self) -> None:
        self._run_projection()
        published_result = self.window._current_workflow_result()
        calls = []

        def exporter(**kwargs):
            calls.append(kwargs)
            return {"scenario": self.directory / "retirement_scenario_projection.pdf"}

        original_run = self.window.controller.run
        run_calls = []

        def counted_run(*args, **kwargs):
            run_calls.append((args, kwargs))
            return original_run(*args, **kwargs)

        self.window.controller.run = counted_run
        self.window._report_suite_exporter = exporter

        self._reports_button().invoke()
        self.root.update_idletasks()

        self.assertEqual(len(calls), 1)
        self.assertIs(calls[0]["scenario_result"], published_result)
        self.assertIs(calls[0]["assumptions"], self.application.assumptions)
        self.assertEqual(calls[0]["allocations"], ALLOCATIONS)
        self.assertEqual(calls[0]["fund_returns"], FUND_RETURNS)
        self.assertEqual(calls[0]["directory"], str(self.directory))
        self.assertEqual(run_calls, [])
        self.assertEqual(len(self.dialog.infos), 1)
        self.assertEqual(self.dialog.infos[0][0], "PDF reports exported")
        self.assertFalse(self.dialog.errors)

    def test_report_pack_button_exports_suite_then_consolidated_pack(self) -> None:
        self._run_projection()
        published_result = self.window._current_workflow_result()
        suite_result = {
            "scenario": self.directory / "retirement_scenario_projection.pdf",
            "strategy": self.directory / "retirement_strategy_comparison.pdf",
        }
        suite_calls = []
        pack_calls = []

        def suite_exporter(**kwargs):
            suite_calls.append(kwargs)
            return suite_result

        def pack_exporter(actual_suite, destination):
            pack_calls.append((actual_suite, destination))
            return SimpleNamespace(path=destination)

        self.window._report_suite_exporter = suite_exporter
        self.window._report_pack_exporter = pack_exporter

        self._report_pack_button().invoke()
        self.root.update_idletasks()

        self.assertEqual(len(suite_calls), 1)
        self.assertIs(suite_calls[0]["scenario_result"], published_result)
        self.assertEqual(suite_calls[0]["directory"], str(self.directory))
        self.assertEqual(len(pack_calls), 1)
        self.assertIs(pack_calls[0][0], suite_result)
        self.assertEqual(
            pack_calls[0][1],
            self.directory / "RetirementPlanner_Report_Pack.pdf",
        )
        self.assertEqual(len(self.dialog.infos), 1)
        self.assertEqual(self.dialog.infos[0][0], "PDF report pack exported")
        self.assertFalse(self.dialog.errors)

    def test_cancelled_directory_selection_does_not_invoke_exporters(self) -> None:
        self._run_projection()
        self.file_dialog.directory = ""
        suite_calls = []
        pack_calls = []
        self.window._report_suite_exporter = lambda **kwargs: suite_calls.append(kwargs)
        self.window._report_pack_exporter = lambda *args: pack_calls.append(args)

        self._reports_button().invoke()
        self._report_pack_button().invoke()
        self.root.update_idletasks()

        self.assertEqual(len(self.file_dialog.calls), 2)
        self.assertFalse(suite_calls)
        self.assertFalse(pack_calls)
        self.assertFalse(self.dialog.errors)
        self.assertFalse(self.dialog.infos)

    def test_stale_results_block_both_exports_before_directory_selection(self) -> None:
        self._run_projection()
        self.window._pension_var.set("765000")
        self.root.update_idletasks()
        self.assertFalse(self.window.results_are_current)
        self.file_dialog.calls.clear()
        suite_calls = []
        pack_calls = []
        self.window._report_suite_exporter = lambda **kwargs: suite_calls.append(kwargs)
        self.window._report_pack_exporter = lambda *args: pack_calls.append(args)

        self._reports_button().invoke()
        self._report_pack_button().invoke()
        self.root.update_idletasks()

        # Stale results disable both native controls, so invoking them is a
        # no-op: no directory picker, exporter, or error dialog is required.
        self.assertEqual(self._reports_button().cget("state"), "disabled")
        self.assertEqual(self._report_pack_button().cget("state"), "disabled")
        self.assertFalse(self.file_dialog.calls)
        self.assertFalse(suite_calls)
        self.assertFalse(pack_calls)
        self.assertFalse(self.dialog.errors)
        self.assertFalse(self.dialog.infos)

    def test_existing_report_pack_is_not_overwritten(self) -> None:
        self._run_projection()
        existing_pack = self.directory / "RetirementPlanner_Report_Pack.pdf"
        existing_pack.write_bytes(b"existing report pack")
        original_bytes = existing_pack.read_bytes()
        suite_calls = []
        pack_calls = []
        self.window._report_suite_exporter = lambda **kwargs: suite_calls.append(kwargs)
        self.window._report_pack_exporter = lambda *args: pack_calls.append(args)

        self._report_pack_button().invoke()
        self.root.update_idletasks()

        self.assertFalse(suite_calls)
        self.assertFalse(pack_calls)
        self.assertEqual(existing_pack.read_bytes(), original_bytes)
        self.assertEqual(len(self.dialog.errors), 1)
        self.assertEqual(
            self.dialog.errors[0][0],
            "Could not export PDF report pack",
        )
        self.assertFalse(self.dialog.infos)

    def test_exporter_failures_are_reported_without_success_dialogs(self) -> None:
        self._run_projection()

        def failing_suite(**kwargs):
            raise OSError("simulated report write failure")

        self.window._report_suite_exporter = failing_suite
        self._reports_button().invoke()
        self.root.update_idletasks()

        self.assertEqual(self.dialog.errors[-1][0], "Could not export PDF reports")
        self.assertIn("simulated report write failure", self.dialog.errors[-1][1])

        def successful_suite(**kwargs):
            return {"scenario": self.directory / "scenario.pdf"}

        def failing_pack(suite, destination):
            raise ValueError("simulated report-pack composition failure")

        self.window._report_suite_exporter = successful_suite
        self.window._report_pack_exporter = failing_pack
        self._report_pack_button().invoke()
        self.root.update_idletasks()

        self.assertEqual(self.dialog.errors[-1][0], "Could not export PDF report pack")
        self.assertIn("simulated report-pack composition failure", self.dialog.errors[-1][1])
        self.assertFalse(self.dialog.infos)

    def test_closed_window_rejects_both_export_actions(self) -> None:
        self._run_projection()
        suite_calls = []
        pack_calls = []
        self.window._report_suite_exporter = lambda **kwargs: suite_calls.append(kwargs)
        self.window._report_pack_exporter = lambda *args: pack_calls.append(args)
        self.window.close()

        self.assertFalse(self.window._export_pdf_reports())
        self.assertFalse(self.window._export_pdf_report_pack())
        self.assertFalse(suite_calls)
        self.assertFalse(pack_calls)
        self.assertFalse(self.file_dialog.calls)


if __name__ == "__main__":
    unittest.main()

"""Sprint 299: native GUI preview/export workflow consistency tests.

Verify preview, report-suite export and report-pack export consume the same
published report snapshot, never trigger extra projections, and all reject
stale results consistently.
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


class Sprint299GuiReportWorkflowConsistencyTests(unittest.TestCase):
    """Exercise preview and PDF export through the same published result."""

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
        self.window = ScenarioProjectionWindow(
            self.application.build_view_model(
                allocations=ALLOCATIONS,
                fund_returns=FUND_RETURNS,
            ),
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

    def _run_projection(self):
        self.window._pension_var.set(str(self.initial_inputs.starting_pension + 1000))
        self.root.update_idletasks()
        self.assertTrue(self.window.workflow_state.run_enabled)
        self.window._run_button.invoke()
        self.root.update_idletasks()
        self.assertTrue(self.window.results_are_current)
        self.assertIsNotNone(self.window._last_workflow_result)
        return self.window._last_workflow_result

    def _preview_button(self) -> ttk.Button:
        self.assertIsInstance(self.window._report_preview_button, ttk.Button)
        return self.window._report_preview_button

    def _reports_button(self) -> ttk.Button:
        self.assertIsInstance(self.window._reports_button, ttk.Button)
        return self.window._reports_button

    def _report_pack_button(self) -> ttk.Button:
        self.assertIsInstance(self.window._report_pack_button, ttk.Button)
        return self.window._report_pack_button

    def _count_projection_runs(self):
        calls = []
        original_run = self.window.controller.run

        def counted_run(*args, **kwargs):
            calls.append((args, kwargs))
            return original_run(*args, **kwargs)

        self.window.controller.run = counted_run
        return calls

    def test_preview_and_report_suite_export_use_identical_published_report(self) -> None:
        published_result = self._run_projection()
        expected_text = published_result.report_text
        expected_snapshot = published_result.snapshot
        run_calls = self._count_projection_runs()
        export_calls = []

        self._preview_button().invoke()
        self.root.update_idletasks()
        preview_text = self.window._report_preview_text
        self.assertIsNotNone(preview_text)
        self.assertEqual(preview_text.get("1.0", "end-1c"), expected_text)

        self.window._report_suite_exporter = lambda **kwargs: (
            export_calls.append(kwargs)
            or {"scenario": self.directory / "scenario.pdf"}
        )
        self._reports_button().invoke()
        self.root.update_idletasks()

        self.assertEqual(len(export_calls), 1)
        exported_result = export_calls[0]["scenario_result"]
        self.assertIs(exported_result, published_result)
        self.assertIs(exported_result.snapshot, expected_snapshot)
        self.assertEqual(exported_result.report_text, preview_text.get("1.0", "end-1c"))
        self.assertEqual(run_calls, [])
        self.assertEqual(len(self.dialog.infos), 1)
        self.assertFalse(self.dialog.errors)

    def test_report_pack_suite_and_preview_share_one_result_without_recalculation(self) -> None:
        published_result = self._run_projection()
        expected_text = published_result.report_text
        run_calls = self._count_projection_runs()
        suite_calls = []
        pack_calls = []

        self._preview_button().invoke()
        self.root.update_idletasks()
        self.assertEqual(
            self.window._report_preview_text.get("1.0", "end-1c"),
            expected_text,
        )

        suite_result = {"scenario": self.directory / "scenario.pdf"}
        self.window._report_suite_exporter = lambda **kwargs: (
            suite_calls.append(kwargs) or suite_result
        )
        self.window._report_pack_exporter = lambda suite, destination: (
            pack_calls.append((suite, destination))
            or SimpleNamespace(path=destination)
        )
        self._report_pack_button().invoke()
        self.root.update_idletasks()

        self.assertEqual(len(suite_calls), 1)
        self.assertIs(suite_calls[0]["scenario_result"], published_result)
        self.assertEqual(suite_calls[0]["scenario_result"].report_text, expected_text)
        self.assertEqual(len(pack_calls), 1)
        self.assertIs(pack_calls[0][0], suite_result)
        self.assertEqual(
            pack_calls[0][1],
            self.directory / "RetirementPlanner_Report_Pack.pdf",
        )
        self.assertEqual(run_calls, [])
        self.assertEqual(len(self.dialog.infos), 1)
        self.assertFalse(self.dialog.errors)

    def test_repeated_preview_and_export_attempts_reuse_published_result(self) -> None:
        published_result = self._run_projection()
        run_calls = self._count_projection_runs()
        export_calls = []
        self.window._report_suite_exporter = lambda **kwargs: (
            export_calls.append(kwargs)
            or {"scenario": self.directory / f"scenario-{len(export_calls)}.pdf"}
        )

        self._preview_button().invoke()
        self.root.update_idletasks()
        preview = self.window._report_preview_window
        self.assertIsNotNone(preview)

        self._preview_button().invoke()
        self.root.update_idletasks()
        self.assertIs(self.window._report_preview_window, preview)

        self._reports_button().invoke()
        self._reports_button().invoke()
        self.root.update_idletasks()

        self.assertEqual(len(export_calls), 2)
        self.assertTrue(all(call["scenario_result"] is published_result for call in export_calls))
        self.assertEqual(run_calls, [])
        self.assertTrue(preview.winfo_exists())

    def test_stale_results_block_preview_and_both_export_workflows(self) -> None:
        self._run_projection()
        self.window._pension_var.set(str(self.initial_inputs.starting_pension + 2500))
        self.root.update_idletasks()

        self.assertFalse(self.window.results_are_current)
        self.assertEqual(str(self._preview_button().cget("state")), "disabled")
        self.assertEqual(str(self._reports_button().cget("state")), "disabled")
        self.assertEqual(str(self._report_pack_button().cget("state")), "disabled")

        self.file_dialog.calls.clear()
        suite_calls = []
        pack_calls = []
        self.window._report_suite_exporter = lambda **kwargs: suite_calls.append(kwargs)
        self.window._report_pack_exporter = lambda *args: pack_calls.append(args)

        self._preview_button().invoke()
        self._reports_button().invoke()
        self._report_pack_button().invoke()
        self.root.update_idletasks()

        self.assertIsNone(self.window._report_preview_window)
        self.assertFalse(self.file_dialog.calls)
        self.assertFalse(suite_calls)
        self.assertFalse(pack_calls)
        self.assertFalse(self.dialog.errors)
        self.assertFalse(self.dialog.infos)


if __name__ == "__main__":
    unittest.main()

"""Sprint 301: asynchronous GUI report-export resilience tests."""
from __future__ import annotations

import shutil
import tempfile
import threading
import time
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
FUND_RETURNS = {"Aviva": (0.10, 0.02, 0.08), "Sky": (0.20, 0.04, 0.16)}


class Sprint301ReportExportResilienceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.directory = Path(self.tempdir.name)
        if tk is None or ttk is None:
            self.tempdir.cleanup()
            self.skipTest("Tkinter is not installed")
        try:
            self.root = tk.Tk()
        except (tk.TclError, RuntimeError) as exc:
            self.tempdir.cleanup()
            self.skipTest(f"Tk display is unavailable: {exc}")
        self.root.withdraw()
        assumptions_path = self.directory / "assumptions.json"
        shutil.copy2(ROOT / "data" / "assumptions.json", assumptions_path)
        self.application = ScenarioProjectionApplication(Assumptions(str(assumptions_path)))
        self.initial_inputs = self.application.inputs()
        self.dialog = RecordingDialog()
        self.file_dialog = RecordingFileDialog(str(self.directory))
        self.window = ScenarioProjectionWindow(
            self.application.build_view_model(
                allocations=ALLOCATIONS, fund_returns=FUND_RETURNS
            ),
            root=self.root,
            application=self.application,
            allocations=ALLOCATIONS,
            fund_returns=FUND_RETURNS,
            dialog=self.dialog,
            file_dialog=self.file_dialog,
        )
        self.window.build()
        self.window._pension_var.set(str(self.initial_inputs.starting_pension + 1000))
        self.root.update_idletasks()
        self.window._run_button.invoke()
        self.root.update_idletasks()
        self.assertTrue(self.window.results_are_current)

    def tearDown(self) -> None:
        try:
            if getattr(self, "root", None) is not None:
                self.root.destroy()
        except (tk.TclError, AttributeError):
            pass
        self.tempdir.cleanup()

    def _wait_for(self, predicate, timeout: float = 5.0) -> None:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            try:
                self.root.update()
            except tk.TclError:
                return
            if predicate():
                return
            time.sleep(0.01)
        self.fail("Timed out waiting for asynchronous report export")

    def test_export_runs_off_ui_thread_and_duplicate_requests_are_blocked(self) -> None:
        entered = threading.Event()
        release = threading.Event()
        calls = []
        ui_thread = threading.get_ident()

        def slow_exporter(**kwargs):
            calls.append((threading.get_ident(), kwargs))
            entered.set()
            if not release.wait(5):
                raise TimeoutError("test export was not released")
            return {"scenario": self.directory / "scenario.pdf"}

        self.window._report_suite_exporter = slow_exporter
        self.window._reports_button.invoke()
        self.assertTrue(entered.wait(2), "export worker did not start")

        # Tk must continue servicing events while the exporter is blocked.
        self.root.update()
        self.assertEqual(len(calls), 1)
        self.assertNotEqual(calls[0][0], ui_thread)
        self.assertTrue(self.window._report_export_in_progress)
        self.assertEqual(str(self.window._reports_button.cget("state")), "disabled")
        self.assertEqual(str(self.window._report_pack_button.cget("state")), "disabled")
        self.assertIn("Exporting", self.window._report_status_var.get())

        self.window._report_pack_button.invoke()
        self.root.update()
        self.assertEqual(len(calls), 1, "a second export must not start concurrently")

        release.set()
        self._wait_for(lambda: not self.window._report_export_in_progress)
        self.assertEqual(len(self.dialog.infos), 1)
        self.assertFalse(self.dialog.errors)
        self.assertEqual(str(self.window._reports_button.cget("state")), "normal")
        self.assertEqual(str(self.window._report_pack_button.cget("state")), "normal")

    def test_failed_export_restores_controls_and_allows_retry(self) -> None:
        attempts = []

        def flaky_exporter(**kwargs):
            attempts.append(kwargs)
            if len(attempts) == 1:
                raise OSError("simulated Sprint 301 report stage failure")
            return {"scenario": self.directory / "scenario.pdf"}

        self.window._report_suite_exporter = flaky_exporter
        self.window._reports_button.invoke()
        self._wait_for(lambda: not self.window._report_export_in_progress)

        self.assertEqual(len(attempts), 1)
        self.assertEqual(len(self.dialog.errors), 1)
        self.assertIn("simulated Sprint 301 report stage failure", self.dialog.errors[0][1])
        self.assertFalse(self.dialog.infos)
        self.assertEqual(str(self.window._reports_button.cget("state")), "normal")

        self.window._reports_button.invoke()
        self._wait_for(lambda: not self.window._report_export_in_progress)
        self.assertEqual(len(attempts), 2)
        self.assertEqual(len(self.dialog.infos), 1)
        self.assertEqual(len(self.dialog.errors), 1)

    def test_report_pack_reports_suite_and_pack_progress_and_completes(self) -> None:
        suite_entered = threading.Event()
        release_suite = threading.Event()
        pack_entered = threading.Event()
        release_pack = threading.Event()
        suite_result = {"scenario": self.directory / "scenario.pdf"}

        def suite_exporter(**kwargs):
            suite_entered.set()
            if not release_suite.wait(5):
                raise TimeoutError("suite stage was not released")
            return suite_result

        def pack_exporter(suite, destination):
            self.assertIs(suite, suite_result)
            pack_entered.set()
            if not release_pack.wait(5):
                raise TimeoutError("pack stage was not released")
            return destination

        self.window._report_suite_exporter = suite_exporter
        self.window._report_pack_exporter = pack_exporter
        self.window._report_pack_button.invoke()
        self.assertTrue(suite_entered.wait(2))
        self.root.update()
        self.assertIn("suite", self.window._report_status_var.get().lower())

        release_suite.set()
        self.assertTrue(pack_entered.wait(2))
        self.root.update()
        self.assertIn("pack", self.window._report_status_var.get().lower())

        release_pack.set()
        self._wait_for(lambda: not self.window._report_export_in_progress)
        self.assertEqual(len(self.dialog.infos), 1)
        self.assertFalse(self.dialog.errors)


if __name__ == "__main__":
    unittest.main()

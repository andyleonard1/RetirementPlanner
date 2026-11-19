"""Sprint 302: cooperative report-export cancellation and publication safety."""
from __future__ import annotations

import shutil
import tempfile
import threading
import time
import unittest
from pathlib import Path

try:
    import tkinter as tk
except ImportError:
    tk = None

from reportlab.pdfgen import canvas

from planner.assumptions import Assumptions
from planner.gui.scenario_projection_application import ScenarioProjectionApplication
from planner.gui.scenario_projection_window import ScenarioProjectionWindow
from planner.gui.testability import RecordingDialog, RecordingFileDialog
from planner.projection.scenario_projection_workflow import ScenarioProjectionApplication as WorkflowApplication
from planner.reporting.report_pack import export_report_pack
from planner.reporting.export_control import ReportExportCancelled
from planner.reporting.report_suite import ReportSuiteExportResult, export_report_suite


ROOT = Path(__file__).resolve().parents[1]
ALLOCATIONS = {"Aviva": 1.0}
FUND_RETURNS = {"Aviva": (0.05, 0.05, 0.05)}


def _make_suite(directory: Path) -> ReportSuiteExportResult:
    names = (
        "retirement_scenario_projection.pdf",
        "retirement_strategy_comparison.pdf",
        "retirement_recommendation.pdf",
        "retirement_health_check.pdf",
        "retirement_goals.pdf",
    )
    paths = []
    for name in names:
        path = directory / name
        pdf = canvas.Canvas(str(path))
        pdf.drawString(72, 720, name)
        pdf.save()
        paths.append(path)
    return ReportSuiteExportResult(*paths)


class Sprint302ReportExportCancellationTests(unittest.TestCase):
    def test_cancelled_suite_removes_staging_and_preserves_existing_reports(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            previous = _make_suite(target)
            original = {path: path.read_bytes() for path in previous.paths.values()}
            workflow = WorkflowApplication(Assumptions()).run_report_workflow(
                allocations=ALLOCATIONS, fund_returns=FUND_RETURNS
            )
            cancellation = threading.Event()

            def request_cancel(message: str) -> None:
                if message.startswith("Generating report 1"):
                    cancellation.set()

            with self.assertRaises(ReportExportCancelled):
                export_report_suite(
                    assumptions=Assumptions(),
                    scenario_result=workflow,
                    allocations=ALLOCATIONS,
                    fund_returns=FUND_RETURNS,
                    directory=target,
                    monte_carlo_iterations=2,
                    monte_carlo_seed=1,
                    overwrite=True,
                    cancellation_event=cancellation,
                    progress_callback=request_cancel,
                )

            for path, data in original.items():
                self.assertEqual(path.read_bytes(), data)
            self.assertEqual(list(target.glob(".retirement-planner-report-suite-*")), [])

    def test_cancelled_pack_preserves_existing_pack_and_removes_temporary_file(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            suite = _make_suite(target)
            output = target / "RetirementPlanner_Report_Pack.pdf"
            output.write_bytes(b"previous approved pack")
            cancellation = threading.Event()
            cancellation.set()

            with self.assertRaises(ReportExportCancelled):
                export_report_pack(suite, output, overwrite=True, cancellation_event=cancellation)

            self.assertEqual(output.read_bytes(), b"previous approved pack")
            self.assertFalse(output.with_name(f".{output.name}.tmp").exists())


class Sprint302GuiCancellationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.directory = Path(self.tempdir.name)
        if tk is None:
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
        self.dialog = RecordingDialog()
        self.window = ScenarioProjectionWindow(
            self.application.build_view_model(allocations=ALLOCATIONS, fund_returns=FUND_RETURNS),
            root=self.root,
            application=self.application,
            allocations=ALLOCATIONS,
            fund_returns=FUND_RETURNS,
            dialog=self.dialog,
            file_dialog=RecordingFileDialog(str(self.directory)),
        )
        self.window.build()
        inputs = self.application.inputs()
        self.window._pension_var.set(str(inputs.starting_pension + 1000))
        self.root.update_idletasks()
        self.window._run_button.invoke()
        self.root.update_idletasks()
        self.assertTrue(self.window.results_are_current)

    def tearDown(self) -> None:
        try:
            self.window.close()
            self.root.destroy()
        except (tk.TclError, AttributeError):
            pass
        self.tempdir.cleanup()

    def _wait_for(self, predicate, timeout: float = 5.0) -> None:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            self.root.update()
            if predicate():
                return
            time.sleep(0.01)
        self.fail("Timed out waiting for report export cancellation")

    def test_cancelled_report_pack_restores_previous_suite_and_pack(self) -> None:
        suite_file = self.directory / "retirement_scenario_projection.pdf"
        suite_file.write_bytes(b"previous successful scenario report")
        pack_file = self.directory / "RetirementPlanner_Report_Pack.pdf"
        pack_file.write_bytes(b"previous successful report pack")
        previous_suite = suite_file.read_bytes()
        previous_pack = pack_file.read_bytes()
        self.dialog.confirm_overwrite = True
        suite_entered = threading.Event()
        pack_entered = threading.Event()

        def suite_exporter(**kwargs):
            suite_entered.set()
            suite_file.write_bytes(b"replacement scenario report")
            return {"scenario_projection": suite_file}

        def pack_exporter(suite, destination, *, cancellation_event, overwrite=False):
            pack_entered.set()
            if not cancellation_event.wait(5):
                raise TimeoutError("pack cancellation was not requested")
            raise ReportExportCancelled("Report pack export cancelled before publication.")

        self.window._report_suite_exporter = suite_exporter
        self.window._report_pack_exporter = pack_exporter
        self.window._report_pack_button.invoke()
        self.assertTrue(suite_entered.wait(2))
        self.assertTrue(pack_entered.wait(2))
        self.root.update()
        self.window._report_cancel_button.invoke()
        self._wait_for(lambda: not self.window._report_export_in_progress)

        self.assertEqual(suite_file.read_bytes(), previous_suite)
        self.assertEqual(pack_file.read_bytes(), previous_pack)
        self.assertIn("cancelled", self.window._report_status_var.get().lower())
        self.assertFalse(self.dialog.errors)
        self.assertFalse(self.dialog.infos)

    def test_gui_cancel_requests_cooperative_stop_and_restores_controls(self) -> None:
        entered = threading.Event()
        observed = threading.Event()

        def slow_exporter(*, cancellation_event, **kwargs):
            entered.set()
            cancellation = cancellation_event
            if not cancellation.wait(5):
                raise TimeoutError("cancel was not requested")
            observed.set()
            raise ReportExportCancelled("Report export cancelled before publication.")

        self.window._report_suite_exporter = slow_exporter
        self.window._reports_button.invoke()
        self.assertTrue(entered.wait(2))
        self.root.update()
        self.assertTrue(self.window._report_export_in_progress)
        self.assertEqual(str(self.window._report_cancel_button.cget("state")), "normal")

        self.window._report_cancel_button.invoke()
        self.assertTrue(observed.wait(2))
        self._wait_for(lambda: not self.window._report_export_in_progress)

        self.assertIn("cancelled", self.window._report_status_var.get().lower())
        self.assertFalse(self.dialog.errors)
        self.assertFalse(self.dialog.infos)
        self.assertEqual(str(self.window._reports_button.cget("state")), "normal")
        self.assertEqual(str(self.window._report_pack_button.cget("state")), "normal")
        self.assertEqual(str(self.window._report_cancel_button.cget("state")), "disabled")


if __name__ == "__main__":
    unittest.main()

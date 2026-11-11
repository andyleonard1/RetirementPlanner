"""Sprint 296: report preview content integrity tests.

Verify the native preview always displays the report text belonging to the
currently published workflow result, including after repeated projections.
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


class Sprint296ReportPreviewContentIntegrityTests(unittest.TestCase):
    """Verify preview text remains tied to the exact published result."""

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

    def _run_projection(self, pension_delta: float) -> object:
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

    def _close_preview(self, preview) -> None:
        preview.destroy()
        self.root.update_idletasks()
        self.assertIsNone(self.window._report_preview_window)
        self.assertIsNone(self.window._report_preview_text)

    def test_preview_text_matches_the_published_workflow_result_exactly(self) -> None:
        result = self._run_projection(1000)
        expected_text = result.report_text

        self.assertEqual(self.window.current_result_report_text(), expected_text)
        self.assertEqual(self.window.current_result_snapshot()["text"], expected_text)
        self.assertEqual(self.window.current_result_report_payload(), result.report_payload)

        preview = self._open_preview()
        self.assertEqual(
            self.window._report_preview_text.get("1.0", "end-1c"),
            expected_text,
        )
        self.assertEqual(
            self.window._report_preview_text.get("1.0", "end-1c"),
            self.window.current_result_report_text(),
        )
        self._close_preview(preview)

    def test_repeated_projections_replace_all_preview_content_with_latest_result(self) -> None:
        first_result = self._run_projection(1000)
        first_text = first_result.report_text
        first_snapshot = first_result.snapshot
        first_preview = self._open_preview()
        self.assertEqual(
            self.window._report_preview_text.get("1.0", "end-1c"),
            first_text,
        )

        # Editing inputs invalidates and closes the old preview before the next
        # published result is produced.
        self.window._pension_var.set(
            str(self.initial_inputs.starting_pension + 2500)
        )
        self.root.update_idletasks()
        self.assertFalse(first_preview.winfo_exists())
        self.assertIsNone(self.window._report_preview_window)
        self.assertIsNone(self.window._report_preview_text)

        second_result = self._run_projection(2500)
        self.assertIsNot(second_result, first_result)
        self.assertIsNot(second_result.snapshot, first_snapshot)
        self.assertNotEqual(second_result.report_text, first_text)
        self.assertEqual(
            self.window.current_result_report_text(),
            second_result.report_text,
        )
        self.assertEqual(
            self.window.current_result_snapshot()["text"],
            second_result.report_text,
        )

        second_preview = self._open_preview()
        self.assertEqual(
            self.window._report_preview_text.get("1.0", "end-1c"),
            second_result.report_text,
        )
        self.assertNotEqual(
            self.window._report_preview_text.get("1.0", "end-1c"),
            first_text,
        )
        self._close_preview(second_preview)

    def test_report_payload_is_a_defensive_copy_of_the_published_result(self) -> None:
        result = self._run_projection(1000)
        first_copy = self.window.current_result_report_payload()
        first_copy["sprint296_test_mutation"] = "must not reach published result"

        second_copy = self.window.current_result_report_payload()
        self.assertNotIn("sprint296_test_mutation", second_copy)
        self.assertNotIn("sprint296_test_mutation", result.report_payload)
        self.assertEqual(second_copy, result.report_payload)


if __name__ == "__main__":
    unittest.main()

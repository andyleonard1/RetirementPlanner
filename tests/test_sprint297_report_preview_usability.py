"""Sprint 297: report preview usability and accessibility tests.

Exercise long-report presentation, keyboard access, read-only behaviour and
empty-report handling through the native Tk preview.
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


class Sprint297ReportPreviewUsabilityTests(unittest.TestCase):
    """Verify the native report preview is usable without changing its content."""

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
        self.window._pension_var.set(str(self.initial_inputs.starting_pension + 1000))
        self.root.update_idletasks()
        self.assertTrue(self.window.workflow_state.run_enabled)
        self.window._run_button.invoke()
        self.root.update_idletasks()
        self.assertTrue(self.window.results_are_current)

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

    def test_long_report_wraps_and_exposes_vertical_scrolling(self) -> None:
        self._run_projection()
        long_report = "\n\n".join(
            f"Section {index}: " + ("A detailed retirement planning explanation " * 24)
            for index in range(1, 36)
        )
        self.window.current_result_report_text = lambda: long_report

        self._open_preview()
        text = self.window._report_preview_text
        self.assertEqual(text.get("1.0", "end-1c"), long_report)
        self.assertEqual(str(text.cget("wrap")), "word")
        self.assertEqual(str(text.cget("state")), "disabled")
        self.assertTrue(text.cget("yscrollcommand"))

        scrollbars = [
            child
            for child in self.window._report_preview_window.winfo_children()[0].winfo_children()
            if isinstance(child, ttk.Scrollbar)
        ]
        self.assertTrue(scrollbars, "long report preview should provide a vertical scrollbar")
        self.assertEqual(str(scrollbars[0].cget("orient")), "vertical")

    def test_preview_is_read_only_and_text_widget_can_receive_keyboard_focus(self) -> None:
        self._run_projection()
        self._open_preview()
        text = self.window._report_preview_text

        self.assertEqual(str(text.cget("state")), "disabled")
        self.assertTrue(text.cget("takefocus"))
        original_text = text.get("1.0", "end-1c")
        next_widget_path = text.tk.call("tk_focusNext", text._w)
        self.assertTrue(next_widget_path)
        next_widget = text.nametowidget(next_widget_path)
        self.assertTrue(next_widget.winfo_exists())
        self.assertEqual(text.get("1.0", "end-1c"), original_text)

    def test_escape_closes_preview_and_releases_widget_references(self) -> None:
        self._run_projection()
        preview = self._open_preview()

        # Tk does not dispatch synthetic key events to an unmapped window.
        # Map the test root and preview, then deliver Escape through Tk's event loop.
        self.root.deiconify()
        preview.deiconify()
        self.root.update()
        preview.focus_force()
        preview.event_generate("<Escape>", when="tail")
        self.root.update()

        self.assertFalse(preview.winfo_exists())
        self.assertIsNone(self.window._report_preview_window)
        self.assertIsNone(self.window._report_preview_text)

    def test_empty_report_is_not_presented_as_a_successful_blank_preview(self) -> None:
        self._run_projection()
        self.window.current_result_report_text = lambda: ""

        opened = self.window._preview_report()
        self.root.update_idletasks()

        self.assertFalse(opened)
        self.assertIsNone(self.window._report_preview_window)
        self.assertIsNone(self.window._report_preview_text)
        self.assertIn("empty", self.window._report_status_var.get().lower())

    def test_window_close_protocol_releases_preview_references(self) -> None:
        self._run_projection()
        preview = self._open_preview()

        close_command = preview.protocol("WM_DELETE_WINDOW")
        self.assertTrue(close_command)
        preview.tk.call(close_command)
        self.root.update_idletasks()

        self.assertFalse(preview.winfo_exists())
        self.assertIsNone(self.window._report_preview_window)
        self.assertIsNone(self.window._report_preview_text)


if __name__ == "__main__":
    unittest.main()

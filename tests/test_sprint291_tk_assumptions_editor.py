"""Sprint 291: real Tk widget interaction coverage for the assumptions editor.

These tests create native Tk widgets and invoke the controls exposed to users.
They skip only when the host cannot create a Tk display (for example, a
headless Linux runner); the Windows desktop test run is the primary GUI gate.
"""
from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

try:
    import tkinter as tk
    from tkinter import ttk
except ImportError:  # Some headless Python distributions omit the optional Tk package.
    tk = None
    ttk = None

from planner.assumptions import Assumptions
from planner.gui.scenario_projection_application import ScenarioProjectionApplication
from planner.gui.scenario_projection_window import ScenarioProjectionWindow


ROOT = Path(__file__).resolve().parents[1]
ALLOCATIONS = {"Aviva": 0.75, "Sky": 0.25}
FUND_RETURNS = {
    "Aviva": [0.10, 0.02, 0.08],
    "Sky": [0.20, 0.04, 0.16],
}


class _CloseDialog:
    def __init__(self, answer: bool):
        self.answer = answer
        self.calls: list[tuple[str, str]] = []

    def askyesno(self, title: str, message: str, **kwargs) -> bool:
        self.calls.append((title, message))
        return self.answer


class Sprint291TkAssumptionsEditorTests(unittest.TestCase):
    """Exercise the actual Text, Label and ttk.Button widgets."""

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

        self.application = ScenarioProjectionApplication(Assumptions(str(self.path)))
        self.view = self.application.build_view_model(
            allocations=ALLOCATIONS,
            fund_returns=FUND_RETURNS,
        )
        self.window = ScenarioProjectionWindow(
            self.view,
            root=self.root,
            application=self.application,
            allocations=ALLOCATIONS,
            fund_returns=FUND_RETURNS,
        )
        self.window._open_assumptions_editor()
        self.editor = self.window._assumptions_editor
        self.text = self.window._assumptions_text
        self.root.update_idletasks()
        self.editor.withdraw()

    def tearDown(self) -> None:
        try:
            if tk is not None and getattr(self, "root", None) is not None:
                self.root.destroy()
        except tk.TclError:
            pass
        self.tempdir.cleanup()

    def _widgets(self, parent=None):
        parent = self.editor if parent is None else parent
        for child in parent.winfo_children():
            yield child
            yield from self._widgets(child)

    def _button(self, label: str) -> ttk.Button:
        for widget in self._widgets():
            if isinstance(widget, ttk.Button) and widget.cget("text") == label:
                return widget
        self.fail(f"assumptions editor button not found: {label}")

    def _status_texts(self) -> list[str]:
        values = []
        for widget in self._widgets():
            if isinstance(widget, ttk.Label):
                variable_name = widget.cget("textvariable")
                if variable_name:
                    try:
                        values.append(str(self.editor.getvar(variable_name)))
                    except tk.TclError:
                        pass
        return values

    def _set_document(self, document: dict) -> str:
        raw = json.dumps(document, ensure_ascii=False, separators=(",", ":"))
        self.text.delete("1.0", "end")
        self.text.insert("1.0", raw)
        self.root.update_idletasks()
        return raw

    def test_editor_opens_real_widgets_with_named_actions_and_focus_support(self) -> None:
        self.assertTrue(self.editor.winfo_exists())
        self.assertEqual(self.editor.title(), "Edit all assumptions")
        self.assertEqual(self.text.get("1.0", "end-1c"), self.window.controller.assumptions_json().rstrip("\n"))

        expected = {
            "Validate", "Format", "Apply", "Apply & Save",
            "Reload document", "Discard changes", "Close",
        }
        buttons = {
            widget.cget("text"): widget
            for widget in self._widgets()
            if isinstance(widget, ttk.Button)
        }
        self.assertTrue(expected <= buttons.keys())
        for label in expected:
            self.assertTrue(str(buttons[label].cget("takefocus")).strip() not in {"", "0", "false"})
        self.assertTrue(str(self.text.cget("takefocus")).strip() not in {"", "0", "false"})

    def test_validate_and_format_use_widgets_without_mutating_active_or_saved_data(self) -> None:
        before = deepcopy(self.application.assumptions.data)
        document = deepcopy(before)
        document["goals"][0]["name"] = "Retirement – café"
        document["target_net_income"] += 123
        self._set_document(document)

        self._button("Validate").invoke()
        self.root.update_idletasks()
        self.assertTrue(any("Valid assumptions document" in value for value in self._status_texts()))
        self.assertEqual(self.application.assumptions.data, before)
        self.assertEqual(self.path.read_bytes(), self.disk_baseline)

        self._button("Format").invoke()
        self.root.update_idletasks()
        formatted = self.text.get("1.0", "end-1c")
        self.assertEqual(json.loads(formatted), document)
        self.assertIn("Retirement – café", formatted)
        self.assertTrue(any("Formatted and validated" in value for value in self._status_texts()))
        self.assertEqual(self.application.assumptions.data, before)
        self.assertEqual(self.path.read_bytes(), self.disk_baseline)

    def test_apply_button_changes_memory_but_not_the_saved_file(self) -> None:
        before = deepcopy(self.application.assumptions.data)
        document = deepcopy(before)
        document["target_net_income"] += 987
        self._set_document(document)

        self._button("Apply").invoke()
        self.root.update_idletasks()

        self.assertEqual(self.application.assumptions.data, document)
        self.assertEqual(self.path.read_bytes(), self.disk_baseline)
        self.assertTrue(self.application.assumptions.has_changes())
        self.assertTrue(any("Applied and validated in memory" in value for value in self._status_texts()))

    def test_apply_and_save_button_persists_only_after_validation(self) -> None:
        document = deepcopy(self.application.assumptions.data)
        document["target_net_income"] += 654
        self._set_document(document)

        self._button("Apply & Save").invoke()
        self.root.update_idletasks()

        self.assertEqual(self.application.assumptions.data, document)
        self.assertEqual(json.loads(self.path.read_text(encoding="utf-8")), document)
        self.assertFalse(self.application.assumptions.has_changes())
        self.assertTrue(any("Applied, validated and saved" in value for value in self._status_texts()))

    def test_invalid_document_is_rejected_without_partial_or_disk_mutation(self) -> None:
        before = deepcopy(self.application.assumptions.data)
        invalid = deepcopy(before)
        invalid["target_net_income"] += 1000
        invalid["starting_pension"] = -1
        self._set_document(invalid)

        self._button("Apply").invoke()
        self.root.update_idletasks()

        self.assertEqual(self.application.assumptions.data, before)
        self.assertEqual(self.path.read_bytes(), self.disk_baseline)
        self.assertTrue(any("Not applied:" in value for value in self._status_texts()))

    def test_discard_button_restores_saved_baseline_and_refreshes_editor_text(self) -> None:
        before = deepcopy(self.application.assumptions.data)
        edited = deepcopy(before)
        edited["goals"][0]["target"] += 4321
        self._set_document(edited)
        self._button("Apply").invoke()
        self.root.update_idletasks()
        self.assertEqual(self.application.assumptions.data, edited)

        self._button("Discard changes").invoke()
        self.root.update_idletasks()

        self.assertEqual(self.application.assumptions.data, before)
        self.assertEqual(json.loads(self.text.get("1.0", "end-1c")), before)
        self.assertEqual(self.path.read_bytes(), self.disk_baseline)
        self.assertFalse(self.application.assumptions.has_changes())

    def test_reload_document_replaces_pending_text_with_current_memory_document(self) -> None:
        before = deepcopy(self.application.assumptions.data)
        edited = deepcopy(before)
        edited["target_net_income"] += 111
        self._set_document(edited)

        self._button("Reload document").invoke()
        self.root.update_idletasks()

        self.assertEqual(json.loads(self.text.get("1.0", "end-1c")), before)
        self.assertEqual(self.application.assumptions.data, before)
        self.assertTrue(any("Reloaded current in-memory assumptions" in value for value in self._status_texts()))

    def test_close_prompts_for_unapplied_text_and_honours_cancel_or_discard(self) -> None:
        document = deepcopy(self.application.assumptions.data)
        document["target_net_income"] += 222
        self._set_document(document)

        cancel_dialog = _CloseDialog(False)
        self.window._dialog = cancel_dialog
        self._button("Close").invoke()
        self.root.update_idletasks()
        self.assertEqual(len(cancel_dialog.calls), 1)
        self.assertTrue(self.editor.winfo_exists())

        discard_dialog = _CloseDialog(True)
        self.window._dialog = discard_dialog
        self._button("Close").invoke()
        self.root.update_idletasks()
        self.assertEqual(len(discard_dialog.calls), 1)
        self.assertFalse(self.editor.winfo_exists())
        self.assertEqual(self.application.assumptions.data, json.loads(self.disk_baseline))

if __name__ == "__main__":
    unittest.main()

"""Sprint 278 GUI assumptions editor wiring and lifecycle coverage.

These tests cover the GUI/editor boundary and controller contract. They do not
claim to exercise a visible Tk display or validate financial calculations.
"""
from __future__ import annotations

import ast
import json
import shutil
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

from planner.assumptions import Assumptions
from planner.gui.scenario_projection_application import ScenarioProjectionApplication
from planner.gui.scenario_projection_controller import ScenarioProjectionGuiController

ROOT = Path(__file__).resolve().parents[1]
WINDOW_SOURCE = ROOT / "planner" / "gui" / "scenario_projection_window.py"


class Sprint278GuiAssumptionsCoverageTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        source = ROOT / "data" / "assumptions.json"
        self.path = Path(self.tempdir.name) / "assumptions.json"
        shutil.copy2(source, self.path)
        self.application = ScenarioProjectionApplication(Assumptions(str(self.path)))
        self.controller = ScenarioProjectionGuiController(self.application, {}, {})

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    @staticmethod
    def _editor_method() -> ast.FunctionDef:
        tree = ast.parse(WINDOW_SOURCE.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "_open_assumptions_editor":
                return node
        raise AssertionError("GUI assumptions editor method was not found")

    def test_editor_exposes_all_expected_actions_with_callbacks(self) -> None:
        method = self._editor_method()
        buttons: dict[str, ast.expr | None] = {}
        for node in ast.walk(method):
            if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
                continue
            if node.func.attr != "Button":
                continue
            values = {keyword.arg: keyword.value for keyword in node.keywords if keyword.arg}
            label = values.get("text")
            if isinstance(label, ast.Constant) and isinstance(label.value, str):
                buttons[label.value] = values.get("command")
        expected = {
            "Validate", "Format", "Apply", "Apply & Save",
            "Reload document", "Discard changes", "Close",
        }
        self.assertTrue(expected <= buttons.keys(), f"missing editor actions: {expected - buttons.keys()}")
        for label in expected:
            self.assertIsNotNone(buttons[label], f"{label} has no callback")

    def test_editor_wires_validate_format_apply_and_persist_to_controller(self) -> None:
        source = ast.unparse(self._editor_method())
        for call in (
            "self.controller.validate_assumptions_json",
            "self.controller.format_assumptions_json",
            "self.controller.apply_assumptions_json",
            "self.controller.save()",
            "self.controller.assumptions_json()",
            "self.controller.discard_assumptions_changes()",
            "self.controller.assumptions_text_has_unapplied_changes",
        ):
            self.assertIn(call, source)
        self.assertIn("Applied, validated and saved to assumptions.json.", source)
        self.assertIn("Not applied:", source)

    def test_validation_and_formatting_are_non_mutating_for_unicode_nested_values(self) -> None:
        before = deepcopy(self.application.assumptions.data)
        candidate = deepcopy(before)
        candidate["goals"][0]["name"] = "Retirement – café"
        candidate["annual_spending_schedule"] = {"2030": 42000, "2040": 31500}
        raw = json.dumps(candidate, ensure_ascii=False, separators=(",", ":"))
        self.assertEqual(self.controller.validate_assumptions_json(raw), candidate)
        formatted = self.controller.format_assumptions_json(raw)
        self.assertEqual(json.loads(formatted), candidate)
        self.assertEqual(self.application.assumptions.data, before)
        self.assertIn("Retirement – café", formatted)

    def test_invalid_nested_schedule_is_rejected_without_partial_application(self) -> None:
        before = deepcopy(self.application.assumptions.data)
        candidate = deepcopy(before)
        candidate["target_net_income"] += 5000
        candidate["isa_return_schedule"] = {"2031": True}
        with self.assertRaises(ValueError):
            self.controller.apply_assumptions_json(json.dumps(candidate))
        self.assertEqual(self.application.assumptions.data, before)
        self.assertEqual(self.controller.assumptions_changes(), ())

    def test_apply_save_reload_lifecycle_preserves_complete_document(self) -> None:
        candidate = deepcopy(self.application.assumptions.data)
        candidate["target_net_income"] += 1250
        candidate["annual_spending_schedule_enabled"] = True
        candidate["annual_spending_schedule"] = {"2030": 42500}
        candidate["isa_allowance_schedule_enabled"] = True
        candidate["isa_allowance_schedule"] = {"2033/34": 45000}
        self.controller.apply_assumptions_json(json.dumps(candidate))
        self.assertTrue(self.controller.assumptions_changes())
        self.controller.save()
        self.assertEqual(self.controller.assumptions_changes(), ())
        self.controller.reload_saved()
        persisted = json.loads(self.path.read_text(encoding="utf-8"))
        self.assertEqual(persisted, candidate)
        self.assertEqual(self.application.assumptions.data, candidate)

    def test_editor_status_distinguishes_invalid_pending_text_from_applied_changes(self) -> None:
        baseline_text = self.controller.assumptions_json()
        self.assertEqual(
            self.controller.assumptions_editor_status(baseline_text),
            "Editor matches the active assumptions; no unsaved changes.",
        )
        self.assertIn("unapplied text changes", self.controller.assumptions_editor_status("{invalid"))
        candidate = deepcopy(self.application.assumptions.data)
        candidate["target_net_income"] += 1
        self.controller.apply_assumptions_json(json.dumps(candidate))
        status = self.controller.assumptions_editor_status(self.controller.assumptions_json())
        self.assertIn("1 applied assumption change(s) are unsaved.", status)


if __name__ == "__main__":
    unittest.main()

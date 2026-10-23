"""Sprint 278: integration coverage for the complete GUI assumptions editor workflow."""
from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

from planner.assumptions import Assumptions
from planner.gui.scenario_projection_application import ScenarioProjectionApplication
from planner.gui.scenario_projection_controller import ScenarioProjectionGuiController


class Sprint278GuiAssumptionsWorkflowMatrixTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        source = Path(__file__).resolve().parents[1] / "data" / "assumptions.json"
        self.path = Path(self.tempdir.name) / "assumptions.json"
        shutil.copy2(source, self.path)
        self.controller = ScenarioProjectionGuiController(
            ScenarioProjectionApplication(Assumptions(str(self.path))), {}, {}
        )

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def _document(self) -> dict:
        return json.loads(self.controller.assumptions_json())

    def test_validate_and_format_leave_active_and_persisted_state_unchanged(self) -> None:
        assumptions = self.controller.application.assumptions
        active_before = deepcopy(assumptions.data)
        disk_before = self.path.read_bytes()
        document = self._document()
        document["target_net_income"] += 321
        text = json.dumps(document)

        validated = self.controller.validate_assumptions_json(text)
        formatted = self.controller.format_assumptions_json(text)

        self.assertEqual(validated, document)
        self.assertEqual(json.loads(formatted), document)
        self.assertTrue(formatted.endswith("\n"))
        self.assertEqual(assumptions.data, active_before)
        self.assertEqual(assumptions._baseline_data, active_before)
        self.assertEqual(self.path.read_bytes(), disk_before)

    def test_apply_is_in_memory_only_until_explicit_save(self) -> None:
        disk_before = self.path.read_bytes()
        document = self._document()
        document["target_net_income"] += 654
        document["goals"][2]["target"] += 1000

        self.controller.apply_assumptions_json(json.dumps(document))

        self.assertEqual(self.controller.application.assumptions.data, document)
        self.assertEqual(self.path.read_bytes(), disk_before)
        self.assertTrue(self.controller.assumptions_changes())
        self.assertIn("unsaved", self.controller.assumptions_editor_status(self.controller.assumptions_json()))

        self.controller.save()
        self.assertEqual(json.loads(self.path.read_text(encoding="utf-8")), document)
        self.assertEqual(self.controller.assumptions_changes(), ())

    def test_reload_saved_discards_active_edits_and_restores_disk_document(self) -> None:
        original = self._document()
        edited = deepcopy(original)
        edited["target_net_income"] += 4321
        self.controller.apply_assumptions_json(json.dumps(edited))
        self.assertNotEqual(self.controller.application.assumptions.data, original)

        self.controller.reload_saved()

        self.assertEqual(self.controller.application.assumptions.data, original)
        self.assertEqual(self.controller.assumptions_changes(), ())
        self.assertEqual(json.loads(self.path.read_text(encoding="utf-8")), original)

    def test_discard_restores_persisted_baseline_including_nested_values(self) -> None:
        original = self._document()
        edited = deepcopy(original)
        edited["goals"][2]["target"] += 12345
        self.controller.apply_assumptions_json(json.dumps(edited))
        self.assertIn("goals[2].target", self.controller.assumptions_changes())

        self.controller.discard_assumptions_changes()

        self.assertEqual(self.controller.application.assumptions.data, original)
        self.assertEqual(self.controller.assumptions_changes(), ())
        self.assertEqual(json.loads(self.path.read_text(encoding="utf-8")), original)

    def test_editor_status_covers_clean_unapplied_applied_and_combined_states(self) -> None:
        clean_text = self.controller.assumptions_json()
        self.assertEqual(
            self.controller.assumptions_editor_status(clean_text),
            "Editor matches the active assumptions; no unsaved changes.",
        )

        text_only = self._document()
        text_only["target_net_income"] += 1
        text_only_json = json.dumps(text_only)
        self.assertEqual(
            self.controller.assumptions_editor_status(text_only_json),
            "Editor has unapplied text changes.",
        )

        self.controller.apply_assumptions_json(json.dumps({**self._document(), "target_net_income": self._document()["target_net_income"] + 2}))
        applied_text = self.controller.assumptions_json()
        self.assertEqual(
            self.controller.assumptions_editor_status(applied_text),
            "1 applied assumption change(s) are unsaved.",
        )
        pending = json.loads(applied_text)
        pending["inflation_rate"] += 0.001
        self.assertEqual(
            self.controller.assumptions_editor_status(json.dumps(pending)),
            "Editor has unapplied text; 1 applied assumption change(s) are unsaved.",
        )

    def test_malformed_editor_text_is_reported_as_pending_and_never_mutates_state(self) -> None:
        before = deepcopy(self.controller.application.assumptions.data)
        self.assertTrue(self.controller.assumptions_text_has_unapplied_changes("{not json"))
        self.assertEqual(
            self.controller.assumptions_editor_status("{not json"),
            "Editor has unapplied text changes.",
        )
        with self.assertRaises(ValueError):
            self.controller.apply_assumptions_json("{not json")
        self.assertEqual(self.controller.application.assumptions.data, before)

    def test_invalid_apply_preserves_active_state_baseline_and_saved_file(self) -> None:
        assumptions = self.controller.application.assumptions
        active_before = deepcopy(assumptions.data)
        baseline_before = deepcopy(assumptions._baseline_data)
        disk_before = self.path.read_bytes()
        invalid = self._document()
        invalid["starting_pension"] = -1

        with self.assertRaises(ValueError):
            self.controller.apply_assumptions_json(json.dumps(invalid))

        self.assertEqual(assumptions.data, active_before)
        self.assertEqual(assumptions._baseline_data, baseline_before)
        self.assertEqual(self.path.read_bytes(), disk_before)


if __name__ == "__main__":
    unittest.main()

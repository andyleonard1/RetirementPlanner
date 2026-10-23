import json
from copy import deepcopy
import tempfile
import unittest
from pathlib import Path

from planner.assumptions import Assumptions
from planner.gui.scenario_projection_application import ScenarioProjectionApplication
from planner.gui.scenario_projection_controller import ScenarioProjectionGuiController


class Sprint171GuiAssumptionsEditorTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        source = Path(__file__).resolve().parents[1] / "data" / "assumptions.json"
        target = Path(self.tempdir.name) / "assumptions.json"
        target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
        app = ScenarioProjectionApplication(Assumptions(str(target)))
        self.controller = ScenarioProjectionGuiController(app, {}, {})

    def tearDown(self):
        self.tempdir.cleanup()

    def test_complete_assumptions_document_can_be_round_tripped(self):
        document = json.loads(self.controller.assumptions_json())
        document["target_net_income"] = 42000
        document["inflation_rate"] = 0.03
        self.controller.apply_assumptions_json(json.dumps(document))
        self.assertEqual(self.controller.application.assumptions.get("target_net_income"), 42000)
        self.assertEqual(self.controller.application.assumptions.get("inflation_rate"), 0.03)

    def test_invalid_complete_document_is_atomic(self):
        before = dict(self.controller.application.assumptions.data)
        document = json.loads(self.controller.assumptions_json())
        document["starting_pension"] = -1
        with self.assertRaises(ValueError):
            self.controller.apply_assumptions_json(json.dumps(document))
        self.assertEqual(self.controller.application.assumptions.data, before)

    def test_nested_goal_edits_are_supported(self):
        document = json.loads(self.controller.assumptions_json())
        document["goals"][2]["target"] = 600000
        self.controller.apply_assumptions_json(json.dumps(document))
        self.assertEqual(self.controller.application.assumptions.data["goals"][2]["target"], 600000)

    def test_non_object_json_is_rejected(self):
        with self.assertRaises(ValueError):
            self.controller.apply_assumptions_json("[]")


if __name__ == "__main__":
    unittest.main()

class Sprint172GuiAssumptionsChangeTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        source = Path(__file__).resolve().parents[1] / "data" / "assumptions.json"
        target = Path(self.tempdir.name) / "assumptions.json"
        target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
        app = ScenarioProjectionApplication(Assumptions(str(target)))
        self.controller = ScenarioProjectionGuiController(app, {}, {})

    def tearDown(self):
        self.tempdir.cleanup()

    def test_assumption_changes_report_nested_paths(self):
        document = json.loads(self.controller.assumptions_json())
        document["goals"][2]["target"] += 1
        self.controller.apply_assumptions_json(json.dumps(document))
        self.assertIn("goals[2].target", self.controller.assumptions_changes())

    def test_discard_assumptions_changes_restores_saved_baseline(self):
        original = self.controller.application.assumptions.get("target_net_income")
        document = json.loads(self.controller.assumptions_json())
        document["target_net_income"] = original + 5000
        self.controller.apply_assumptions_json(json.dumps(document))
        self.assertTrue(self.controller.assumptions_changes())
        self.controller.discard_assumptions_changes()
        self.assertEqual(self.controller.application.assumptions.get("target_net_income"), original)
        self.assertEqual(self.controller.assumptions_changes(), ())

    def test_discard_is_atomic_when_saved_baseline_is_corrupted(self):
        document = json.loads(self.controller.assumptions_json())
        before = dict(self.controller.application.assumptions.data)
        self.controller.application.assumptions.data["target_net_income"] = 42000
        self.controller.application.assumptions._baseline_data["target_net_income"] = "invalid"
        with self.assertRaises(ValueError):
            self.controller.discard_assumptions_changes()
        self.assertEqual(self.controller.application.assumptions.data["target_net_income"], 42000)
        self.controller.application.assumptions._baseline_data = before

    def test_changes_are_empty_after_explicit_save(self):
        document = json.loads(self.controller.assumptions_json())
        document["target_net_income"] += 1000
        self.controller.apply_assumptions_json(json.dumps(document))
        self.assertTrue(self.controller.assumptions_changes())
        self.controller.save()
        self.assertEqual(self.controller.assumptions_changes(), ())

class Sprint173GuiAssumptionsValidationTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        source = Path(__file__).resolve().parents[1] / "data" / "assumptions.json"
        target = Path(self.tempdir.name) / "assumptions.json"
        target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
        app = ScenarioProjectionApplication(Assumptions(str(target)))
        self.controller = ScenarioProjectionGuiController(app, {}, {})

    def tearDown(self):
        self.tempdir.cleanup()

    def test_validate_assumptions_json_does_not_mutate_active_state(self):
        before = deepcopy(self.controller.application.assumptions.data)
        document = json.loads(self.controller.assumptions_json())
        document["target_net_income"] += 1234
        self.controller.validate_assumptions_json(json.dumps(document))
        self.assertEqual(self.controller.application.assumptions.data, before)

    def test_format_assumptions_json_returns_canonical_valid_document(self):
        document = json.loads(self.controller.assumptions_json())
        text = json.dumps(document, separators=(",", ":"))
        formatted = self.controller.format_assumptions_json(text)
        self.assertEqual(json.loads(formatted), document)
        self.assertIn("\n    ", formatted)

    def test_invalid_document_is_rejected_by_validation_without_mutation(self):
        before = deepcopy(self.controller.application.assumptions.data)
        document = json.loads(self.controller.assumptions_json())
        document["starting_pension"] = -1
        with self.assertRaises(ValueError):
            self.controller.validate_assumptions_json(json.dumps(document))
        self.assertEqual(self.controller.application.assumptions.data, before)

class Sprint174GuiAssumptionsReloadTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        source = Path(__file__).resolve().parents[1] / "data" / "assumptions.json"
        target = Path(self.tempdir.name) / "assumptions.json"
        target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
        app = ScenarioProjectionApplication(Assumptions(str(target)))
        self.controller = ScenarioProjectionGuiController(app, {}, {})
        self.target = target

    def tearDown(self):
        self.tempdir.cleanup()

    def test_reload_saved_is_atomic_when_disk_json_is_invalid(self):
        assumptions = self.controller.application.assumptions
        document = json.loads(self.controller.assumptions_json())
        document["target_net_income"] += 1000
        self.controller.apply_assumptions_json(json.dumps(document))
        before = deepcopy(assumptions.data)
        baseline = deepcopy(assumptions._baseline_data)
        self.target.write_text("{invalid", encoding="utf-8")
        with self.assertRaises(ValueError):
            self.controller.reload_saved()
        self.assertEqual(assumptions.data, before)
        self.assertEqual(assumptions._baseline_data, baseline)

    def test_reload_saved_is_atomic_when_disk_document_fails_validation(self):
        assumptions = self.controller.application.assumptions
        document = json.loads(self.controller.assumptions_json())
        document["target_net_income"] += 1000
        self.controller.apply_assumptions_json(json.dumps(document))
        before = deepcopy(assumptions.data)
        baseline = deepcopy(assumptions._baseline_data)
        disk_document = json.loads(self.target.read_text(encoding="utf-8"))
        disk_document["starting_pension"] = -1
        self.target.write_text(json.dumps(disk_document), encoding="utf-8")
        with self.assertRaises(ValueError):
            self.controller.reload_saved()
        self.assertEqual(assumptions.data, before)
        self.assertEqual(assumptions._baseline_data, baseline)

class Sprint176GuiAssumptionsEditorStatusTests(Sprint171GuiAssumptionsEditorTests):
    def test_editor_status_reports_text_only_changes(self):
        document = json.loads(self.controller.assumptions_json())
        document["target_net_income"] += 1
        self.assertEqual(
            self.controller.assumptions_editor_status(json.dumps(document)),
            "Editor has unapplied text changes.",
        )

    def test_editor_status_reports_applied_unsaved_changes(self):
        document = json.loads(self.controller.assumptions_json())
        document["target_net_income"] += 1
        self.controller.apply_assumptions_json(json.dumps(document))
        self.assertIn("1 applied assumption change(s) are unsaved.", self.controller.assumptions_editor_status(self.controller.assumptions_json()))

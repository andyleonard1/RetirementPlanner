import json
import tempfile
import unittest
from pathlib import Path

from planner.assumptions import Assumptions
from planner.gui.scenario_projection_application import ScenarioProjectionApplication
from planner.gui.scenario_projection_controller import ScenarioProjectionGuiController


class Sprint175GuiAssumptionsEditorCloseTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        source = Path(__file__).resolve().parents[1] / "data" / "assumptions.json"
        target = Path(self.tempdir.name) / "assumptions.json"
        target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
        app = ScenarioProjectionApplication(Assumptions(str(target)))
        self.controller = ScenarioProjectionGuiController(app, {}, {})

    def tearDown(self):
        self.tempdir.cleanup()

    def test_identical_editor_document_has_no_unapplied_changes(self):
        self.assertFalse(
            self.controller.assumptions_text_has_unapplied_changes(
                self.controller.assumptions_json()
            )
        )

    def test_valid_changed_document_has_unapplied_changes(self):
        document = json.loads(self.controller.assumptions_json())
        document["target_net_income"] += 1000
        self.assertTrue(
            self.controller.assumptions_text_has_unapplied_changes(
                json.dumps(document)
            )
        )

    def test_invalid_changed_document_counts_as_pending_work(self):
        text = self.controller.assumptions_json().replace("{", "{\n", 1)
        text += "not-json"
        self.assertTrue(self.controller.assumptions_text_has_unapplied_changes(text))

    def test_non_text_editor_document_is_rejected(self):
        with self.assertRaises(TypeError):
            self.controller.assumptions_text_has_unapplied_changes(None)


if __name__ == "__main__":
    unittest.main()

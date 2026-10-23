import shutil
import tempfile
import unittest
from pathlib import Path

from planner.assumptions import Assumptions
from planner.gui.scenario_projection_application import ScenarioProjectionApplication, ScenarioProjectionWorkflowResult
from planner.gui.scenario_projection_controller import ScenarioProjectionGuiController, ScenarioProjectionRunResult


class Sprint192GuiSharedWorkflowBoundaryTests(unittest.TestCase):
    def setUp(self):
        self._tempdir = tempfile.TemporaryDirectory()
        source = Path(__file__).resolve().parents[1] / "data" / "assumptions.json"
        target = Path(self._tempdir.name) / "assumptions.json"
        shutil.copy2(source, target)
        self.application = ScenarioProjectionApplication(Assumptions(str(target)))
        self.controller = ScenarioProjectionGuiController(
            self.application,
            {"Aviva": 0.75, "Sky": 0.25},
            {"Aviva": (0.10, 0.02, 0.08), "Sky": (0.20, 0.04, 0.16)},
        )

    def tearDown(self):
        self._tempdir.cleanup()

    def test_controller_run_publishes_shared_workflow_result(self):
        result = self.controller.run("700000", "64", "92", ("central",))
        self.assertIsInstance(result, ScenarioProjectionRunResult)
        self.assertIsInstance(result.workflow_result, ScenarioProjectionWorkflowResult)
        self.assertIs(result.view_model, result.workflow_result.view_model)
        self.assertEqual(result.inputs, result.workflow_result.inputs)

    def test_controller_workflow_snapshot_matches_run_view_model_report(self):
        result = self.controller.run("700000", "64", "92", ("central", "optimistic"))
        self.assertEqual(result.workflow_result.report_payload, result.view_model.report_payload())
        self.assertEqual(result.workflow_result.report_text, result.view_model.report_text())
        self.assertEqual(result.workflow_result.snapshot["text"], result.workflow_result.report_text)

    def test_failed_unified_workflow_restores_previous_inputs(self):
        original = self.application.run_report_workflow
        def failing_workflow(**kwargs):
            raise ValueError("simulated report workflow failure")
        self.application.run_report_workflow = failing_workflow
        with self.assertRaises(ValueError):
            self.controller.run("710000", "65", "91", ("central",))
        self.assertEqual(self.application.inputs().starting_pension, 660000.0)
        self.assertEqual(self.application.inputs().retirement_age, 63)
        self.assertEqual(self.application.inputs().projection_end_age, 90)
        self.application.run_report_workflow = original


if __name__ == "__main__":
    unittest.main()

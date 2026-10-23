import importlib
import tempfile
import unittest
from pathlib import Path

from planner.assumptions import Assumptions
from planner.projection.scenario_projection_workflow import (
    ScenarioProjectionApplication,
    ScenarioProjectionInputs,
    ScenarioProjectionWorkflowResult,
)
from planner.gui.scenario_projection_application import (
    ScenarioProjectionApplication as GuiApplication,
    ScenarioProjectionInputs as GuiInputs,
    ScenarioProjectionWorkflowResult as GuiWorkflowResult,
)


class Sprint195NeutralWorkflowBoundaryTests(unittest.TestCase):
    def setUp(self):
        source = Path(__file__).resolve().parents[1] / "data" / "assumptions.json"
        self._tempdir = tempfile.TemporaryDirectory()
        target = Path(self._tempdir.name) / "assumptions.json"
        target.write_bytes(source.read_bytes())
        self.assumptions_path = target

    def tearDown(self):
        self._tempdir.cleanup()

    def test_workflow_contract_is_defined_outside_gui_package(self):
        module = importlib.import_module("planner.projection.scenario_projection_workflow")
        self.assertEqual(module.ScenarioProjectionApplication.__module__, module.__name__)
        self.assertEqual(module.ScenarioProjectionInputs.__module__, module.__name__)
        self.assertEqual(module.ScenarioProjectionWorkflowResult.__module__, module.__name__)

    def test_gui_compatibility_imports_preserve_exact_workflow_types(self):
        self.assertIs(GuiApplication, ScenarioProjectionApplication)
        self.assertIs(GuiInputs, ScenarioProjectionInputs)
        self.assertIs(GuiWorkflowResult, ScenarioProjectionWorkflowResult)

    def test_public_cli_and_gui_modules_depend_on_neutral_workflow_boundary(self):
        scenario_report = importlib.import_module("scenario_report")
        gui_controller = importlib.import_module("planner.gui.scenario_projection_controller")
        self.assertIs(scenario_report.ScenarioProjectionApplication, ScenarioProjectionApplication)
        self.assertIs(gui_controller.ScenarioProjectionApplication, ScenarioProjectionApplication)


if __name__ == "__main__":
    unittest.main()

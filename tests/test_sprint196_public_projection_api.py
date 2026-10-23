import importlib
import unittest

from planner.projection import (
    ScenarioProjectionApplication,
    ScenarioProjectionInputs,
    ScenarioProjectionWorkflowResult,
)


class Sprint196PublicProjectionApiTests(unittest.TestCase):
    def test_public_projection_package_exports_canonical_workflow_types(self):
        module = importlib.import_module("planner.projection")
        canonical = importlib.import_module("planner.projection.scenario_projection_workflow")
        self.assertEqual(
            module.__all__,
            [
                "ScenarioProjectionApplication",
                "ScenarioProjectionInputs",
                "ScenarioProjectionWorkflowResult",
            ],
        )
        self.assertIs(module.ScenarioProjectionApplication, canonical.ScenarioProjectionApplication)
        self.assertIs(module.ScenarioProjectionInputs, canonical.ScenarioProjectionInputs)
        self.assertIs(module.ScenarioProjectionWorkflowResult, canonical.ScenarioProjectionWorkflowResult)

    def test_public_projection_import_does_not_require_gui_package(self):
        module = importlib.import_module("planner.projection")
        self.assertFalse(module.ScenarioProjectionApplication.__module__.startswith("planner.gui"))
        self.assertFalse(module.ScenarioProjectionInputs.__module__.startswith("planner.gui"))
        self.assertFalse(module.ScenarioProjectionWorkflowResult.__module__.startswith("planner.gui"))

    def test_first_party_cli_and_gui_surfaces_use_public_projection_api(self):
        scenario_report = importlib.import_module("scenario_report")
        controller = importlib.import_module("planner.gui.scenario_projection_controller")
        window = importlib.import_module("planner.gui.scenario_projection_window")
        gui_compat = importlib.import_module("planner.gui.scenario_projection_application")
        self.assertIs(scenario_report.ScenarioProjectionApplication, ScenarioProjectionApplication)
        self.assertIs(controller.ScenarioProjectionApplication, ScenarioProjectionApplication)
        self.assertIs(controller.ScenarioProjectionInputs, ScenarioProjectionInputs)
        self.assertIs(controller.ScenarioProjectionWorkflowResult, ScenarioProjectionWorkflowResult)
        self.assertIs(window.ScenarioProjectionApplication, ScenarioProjectionApplication)
        self.assertIs(window.ScenarioProjectionInputs, ScenarioProjectionInputs)
        self.assertIs(gui_compat.ScenarioProjectionApplication, ScenarioProjectionApplication)


if __name__ == "__main__":
    unittest.main()

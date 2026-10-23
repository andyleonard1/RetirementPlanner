import copy
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from planner.assumptions import Assumptions
from planner.gui.scenario_projection_application import ScenarioProjectionApplication
from planner.gui.scenario_projection_controller import ScenarioProjectionGuiController


class Sprint177GuiAssumptionsProjectionIntegrationTests(unittest.TestCase):
    """Prove flexible GUI assumptions drive the real projection pipeline."""

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

    def _run_central(self):
        inputs = self.application.inputs()
        return self.controller.run(
            str(inputs.starting_pension),
            str(inputs.retirement_age),
            str(inputs.projection_end_age),
            ("central",),
        ).view_model

    def test_flexible_document_starting_pension_changes_real_projection(self):
        baseline = self._run_central()
        document = copy.deepcopy(self.application.assumptions.data)
        document["starting_pension"] = 760000.0

        self.controller.apply_assumptions_json(json.dumps(document))
        updated = self._run_central()

        self.assertEqual(self.application.assumptions.get("starting_pension"), 760000.0)
        self.assertNotEqual(
            baseline.scenario_cards[0].ending_balance,
            updated.scenario_cards[0].ending_balance,
        )
        self.assertGreater(
            updated.scenario_cards[0].ending_balance,
            baseline.scenario_cards[0].ending_balance,
        )

    def test_flexible_document_non_primary_starting_savings_changes_real_projection(self):
        baseline = self._run_central()
        document = copy.deepcopy(self.application.assumptions.data)
        document["starting_savings"] = 200000.0

        self.controller.apply_assumptions_json(json.dumps(document))
        updated = self._run_central()

        self.assertEqual(self.application.assumptions.get("starting_savings"), 200000.0)
        self.assertNotEqual(
            baseline.scenario_cards[0].ending_balance,
            updated.scenario_cards[0].ending_balance,
        )
        self.assertGreater(
            updated.scenario_cards[0].ending_balance,
            baseline.scenario_cards[0].ending_balance,
        )

    def test_nested_goal_edit_round_trips_without_changing_projection_calculation_boundary(self):
        baseline = self._run_central()
        document = copy.deepcopy(self.application.assumptions.data)
        document["goals"][2]["target"] = 600000

        self.controller.apply_assumptions_json(json.dumps(document))
        round_trip = json.loads(self.controller.assumptions_json())
        updated = self._run_central()

        self.assertEqual(round_trip["goals"][2]["target"], 600000)
        self.assertEqual(
            baseline.scenario_cards[0].ending_balance,
            updated.scenario_cards[0].ending_balance,
        )
        self.assertIn("goals[2].target", self.controller.assumptions_changes())


if __name__ == "__main__":
    unittest.main()

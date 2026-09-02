import unittest

from planner.assumptions import Assumptions
from planner.gui.scenario_projection_application import (
    ScenarioProjectionApplication,
    ScenarioProjectionInputs,
)


class ScenarioProjectionApplicationTests(unittest.TestCase):
    def setUp(self):
        self.app = ScenarioProjectionApplication(Assumptions())

    def test_inputs_reflect_assumptions(self):
        inputs = self.app.inputs()
        self.assertEqual(inputs.starting_pension, 660000.0)
        self.assertEqual(inputs.retirement_age, 63)
        self.assertEqual(inputs.projection_end_age, 90)
        self.assertEqual(inputs.scenarios, ("conservative", "central", "optimistic"))

    def test_inputs_reject_negative_pension(self):
        with self.assertRaises(ValueError):
            ScenarioProjectionInputs(-1, 63, 90)

    def test_inputs_reject_invalid_age_range(self):
        with self.assertRaises(ValueError):
            ScenarioProjectionInputs(660000, 70, 69)

    def test_inputs_reject_empty_scenarios(self):
        with self.assertRaises(ValueError):
            ScenarioProjectionInputs(660000, 63, 90, ())

    def test_apply_inputs_updates_assumptions_in_memory(self):
        inputs = ScenarioProjectionInputs(700000, 64, 92, ("central",))
        self.app.apply_inputs(inputs)
        self.assertEqual(self.app.assumptions.get("starting_pension"), 700000)
        self.assertEqual(self.app.assumptions.get("retirement_age"), 64)
        self.assertEqual(self.app.assumptions.get("projection_end_age"), 92)
        self.assertTrue(self.app.assumptions.has_changes())

    def test_application_requires_assumptions(self):
        with self.assertRaises(TypeError):
            ScenarioProjectionApplication(object())

    def test_build_view_model_uses_requested_scenarios(self):
        view = self.app.build_view_model(
            allocations={"Aviva": 0.75, "Sky": 0.25},
            fund_returns={"Aviva": [0.10, 0.02, 0.08], "Sky": [0.20, 0.04, 0.16]},
            scenarios=("central", "optimistic"),
        )
        self.assertEqual(view.scenario_names, ("central", "optimistic"))

    def test_build_view_model_preserves_calculation_boundary(self):
        before = self.app.assumptions.changes()
        self.app.build_view_model(
            allocations={"Aviva": 0.75, "Sky": 0.25},
            fund_returns={"Aviva": [0.10, 0.02, 0.08], "Sky": [0.20, 0.04, 0.16]},
            scenarios=("central",),
        )
        self.assertEqual(self.app.assumptions.changes(), before)


if __name__ == "__main__":
    unittest.main()

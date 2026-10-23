import shutil
import tempfile
import unittest
from pathlib import Path

from planner.assumptions import Assumptions
from planner.gui.scenario_projection_application import ScenarioProjectionApplication
from planner.gui.scenario_projection_controller import ScenarioProjectionGuiController, ScenarioProjectionRunResult


class ScenarioProjectionGuiControllerTests(unittest.TestCase):
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
        self.controller = ScenarioProjectionGuiController(
            self.application,
            {"Aviva": 0.75, "Sky": 0.25},
            {"Aviva": (0.10, 0.02, 0.08), "Sky": (0.20, 0.04, 0.16)},
        )

    def test_controller_rejects_wrong_application_type(self):
        with self.assertRaises(TypeError):
            ScenarioProjectionGuiController(object(), {}, {})

    def test_controller_copies_input_data(self):
        allocations = {"Aviva": 0.75, "Sky": 0.25}
        returns = {"Aviva": [0.1, 0.02, 0.08], "Sky": [0.2, 0.04, 0.16]}
        controller = ScenarioProjectionGuiController(self.application, allocations, returns)
        allocations["Aviva"] = 1.0
        returns["Aviva"][0] = 9.0
        self.assertEqual(controller.allocations["Aviva"], 0.75)
        self.assertEqual(controller.fund_returns["Aviva"][0], 0.1)

    def test_parse_inputs_accepts_currency_formatting(self):
        inputs = self.controller.parse_inputs("£710,000", "65", "91", ("central",))
        self.assertEqual(inputs.starting_pension, 710000.0)
        self.assertEqual(inputs.retirement_age, 65)
        self.assertEqual(inputs.projection_end_age, 91)

    def test_parse_inputs_rejects_unknown_scenario(self):
        with self.assertRaises(ValueError):
            self.controller.parse_inputs("700000", "64", "92", ("extreme",))

    def test_initial_selected_scenarios_match_application(self):
        self.assertEqual(self.controller.selected_scenarios, ("conservative", "central", "optimistic"))

    def test_run_returns_immutable_run_result(self):
        result = self.controller.run("700000", "64", "92", ("central",))
        self.assertIsInstance(result, ScenarioProjectionRunResult)
        self.assertEqual(result.inputs.scenarios, ("central",))
        self.assertEqual(result.view_model.scenario_names, ("central",))

    def test_run_updates_selected_scenario_state(self):
        self.controller.run("700000", "64", "92", ("optimistic",))
        self.assertEqual(self.controller.selected_scenarios, ("optimistic",))

    def test_run_applies_inputs_through_application(self):
        self.controller.run("£710,000", "65", "91", ("conservative", "central"))
        assumptions = self.application.assumptions
        self.assertEqual(assumptions.get("starting_pension"), 710000.0)
        self.assertEqual(assumptions.get("retirement_age"), 65)
        self.assertEqual(assumptions.get("projection_end_age"), 91)

    def test_run_rejects_invalid_numeric_input(self):
        with self.assertRaises(ValueError):
            self.controller.run("bad", "64", "92", ("central",))

    def test_run_rejects_empty_scenario_selection(self):
        with self.assertRaises(ValueError):
            self.controller.run("700000", "64", "92", ())

    def test_run_deduplicates_selected_scenarios(self):
        result = self.controller.run("700000", "64", "92", ("central", "central"))
        self.assertEqual(result.inputs.scenarios, ("central",))

    def test_save_is_explicit(self):
        self.controller.run("710000", "65", "91", ("central",))
        self.assertTrue(self.application.assumptions.has_changes())
        self.controller.save()
        self.assertFalse(self.application.assumptions.has_changes())


if __name__ == "__main__":
    unittest.main()

class ScenarioProjectionGuiControllerReloadTests(unittest.TestCase):
    def test_reload_saved_restores_disk_values_and_selection(self):
        import json
        import tempfile
        from pathlib import Path
        from planner.assumptions import Assumptions
        from planner.gui.scenario_projection_application import ScenarioProjectionApplication
        from planner.gui.scenario_projection_controller import ScenarioProjectionGuiController

        with tempfile.TemporaryDirectory() as directory:
            source = Path("data/assumptions.json")
            target = Path(directory) / "assumptions.json"
            target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
            assumptions = Assumptions(str(target))
            application = ScenarioProjectionApplication(assumptions)
            controller = ScenarioProjectionGuiController(
                application,
                {"Aviva": 0.75, "Sky": 0.25},
                {"Aviva": (0.10, 0.02, 0.08), "Sky": (0.20, 0.04, 0.16)},
            )
            application.apply_inputs(
                application.inputs().__class__(710000.0, 65, 91)
            )
            self.assertTrue(assumptions.has_changes())
            restored = controller.reload_saved()
            self.assertEqual(restored.starting_pension, 660000.0)
            self.assertEqual(restored.retirement_age, 63)
            self.assertEqual(restored.projection_end_age, 90)
            self.assertFalse(assumptions.has_changes())
            self.assertEqual(controller.selected_scenarios, ("conservative", "central", "optimistic"))

class ScenarioProjectionGuiControllerRobustnessTests(unittest.TestCase):
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

    def test_parse_inputs_rejects_non_finite_pension(self):
        for value in ("nan", "inf", "-inf"):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    self.controller.parse_inputs(value, "63", "90", ("central",))

    def test_run_supports_one_selected_scenario(self):
        result = self.controller.run("660000", "63", "90", ("central",))
        self.assertEqual(result.view_model.scenario_names, ("central",))

    def test_run_supports_two_selected_scenarios(self):
        result = self.controller.run("660000", "63", "90", ("conservative", "optimistic"))
        self.assertEqual(result.view_model.scenario_names, ("conservative", "optimistic"))

    def test_run_supports_three_selected_scenarios(self):
        result = self.controller.run("660000", "63", "90", ("conservative", "central", "optimistic"))
        self.assertEqual(result.view_model.scenario_names, ("conservative", "central", "optimistic"))

    def test_failed_rebuild_restores_previous_inputs(self):
        original_build = self.application.build_view_model
        def failing_build(**kwargs):
            raise ValueError("simulated rebuild failure")
        self.application.build_view_model = failing_build
        with self.assertRaises(ValueError):
            self.controller.run("710000", "65", "91", ("central",))
        self.assertEqual(self.application.inputs().starting_pension, 660000.0)
        self.assertEqual(self.application.inputs().retirement_age, 63)
        self.assertEqual(self.application.inputs().projection_end_age, 90)
        self.application.build_view_model = original_build

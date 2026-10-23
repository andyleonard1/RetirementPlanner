import copy
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from planner.assumptions import Assumptions
from planner.gui.scenario_projection_application import ScenarioProjectionApplication
from planner.gui.scenario_projection_controller import ScenarioProjectionGuiController


class Sprint179GuiAssumptionsScenarioIntegrityTests(unittest.TestCase):
    """Prove multi-field flexible GUI edits remain coherent end-to-end."""

    def setUp(self):
        self._tempdir = tempfile.TemporaryDirectory()
        source = Path(__file__).resolve().parents[1] / "data" / "assumptions.json"
        target = Path(self._tempdir.name) / "assumptions.json"
        shutil.copy2(source, target)
        self.path = target
        self.application = ScenarioProjectionApplication(Assumptions(str(target)))
        self.controller = ScenarioProjectionGuiController(
            self.application,
            {"Aviva": 0.75, "Sky": 0.25},
            {"Aviva": (0.10, 0.02, 0.08), "Sky": (0.20, 0.04, 0.16)},
        )

    def tearDown(self):
        self._tempdir.cleanup()

    def _run(self, scenarios=("conservative", "central", "optimistic")):
        inputs = self.application.inputs()
        return self.controller.run(
            str(inputs.starting_pension),
            str(inputs.retirement_age),
            str(inputs.projection_end_age),
            scenarios,
        ).view_model

    def test_multiple_assumptions_apply_as_one_coherent_projection_input(self):
        baseline = self._run(("central",))
        document = copy.deepcopy(self.application.assumptions.data)
        document.update(
            {
                "starting_pension": 720000.0,
                "starting_savings": 120000.0,
                "starting_isa": 180000.0,
                "spending_phase_1": 40000,
                "withdrawal_strategy": "ISA_FIRST",
            }
        )

        self.controller.apply_assumptions_json(json.dumps(document))
        updated = self._run(("central",))

        self.assertNotEqual(
            baseline.scenario_cards[0].ending_balance,
            updated.scenario_cards[0].ending_balance,
        )
        self.assertEqual(self.application.assumptions.get("starting_pension"), 720000.0)
        self.assertEqual(self.application.assumptions.get("starting_savings"), 120000.0)
        self.assertEqual(self.application.assumptions.get("starting_isa"), 180000.0)
        self.assertEqual(self.application.assumptions.get("spending_phase_1"), 40000)
        self.assertEqual(self.application.assumptions.get("withdrawal_strategy"), "ISA_FIRST")
        self.assertEqual(
            self.controller.assumptions_changes(),
            tuple(sorted(self.controller.assumptions_changes())),
        )

    def test_same_flexible_document_produces_all_requested_scenarios(self):
        document = copy.deepcopy(self.application.assumptions.data)
        document.update(
            {
                "starting_savings": 100000.0,
                "starting_isa": 150000.0,
                "spending_phase_1": 36000,
            }
        )
        self.controller.apply_assumptions_json(json.dumps(document))

        view = self._run()
        cards = view.scenario_cards

        self.assertEqual(tuple(card.name for card in cards), ("conservative", "central", "optimistic"))
        self.assertEqual(len(cards), 3)
        self.assertTrue(all(card.ending_balance is not None for card in cards))
        self.assertEqual(len(self.controller.assumptions_changes()), 3)

    def test_saved_multi_assumption_document_round_trips_without_cross_field_drift(self):
        document = copy.deepcopy(self.application.assumptions.data)
        document.update(
            {
                "starting_pension": 710000.0,
                "starting_savings": 95000.0,
                "starting_isa": 165000.0,
                "withdrawal_strategy": "ISA_FIRST",
                "inflation_link_spending": False,
                "spending_phase_2": 30000,
            }
        )
        self.controller.apply_assumptions_json(json.dumps(document))
        before = self._run(("central",)).scenario_cards[0].ending_balance
        self.controller.save()
        self.controller.reload_saved()

        persisted = json.loads(self.path.read_text(encoding="utf-8"))
        self.assertEqual(persisted, self.application.assumptions.data)
        self.assertEqual(self.controller.assumptions_changes(), ())
        self.assertEqual(self._run(("central",)).scenario_cards[0].ending_balance, before)
        for key, value in document.items():
            self.assertEqual(self.application.assumptions.get(key), value)


if __name__ == "__main__":
    unittest.main()

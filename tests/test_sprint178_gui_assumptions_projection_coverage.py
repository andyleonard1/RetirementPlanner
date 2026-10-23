import copy
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from planner.assumptions import Assumptions
from planner.gui.scenario_projection_application import ScenarioProjectionApplication
from planner.gui.scenario_projection_controller import ScenarioProjectionGuiController
from planner.planner import RetirementPlanner
from planner.funds.portfolio_historical_statistics import PortfolioHistoricalStatisticsCalculator


class Sprint178GuiAssumptionsProjectionCoverageTests(unittest.TestCase):
    """Lock down broader flexible-assumption propagation through projections."""

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

    def _run_central(self):
        inputs = self.application.inputs()
        return self.controller.run(
            str(inputs.starting_pension),
            str(inputs.retirement_age),
            str(inputs.projection_end_age),
            ("central",),
        ).view_model.scenario_cards[0].ending_balance

    def _edit_and_run(self, key, value):
        document = copy.deepcopy(self.application.assumptions.data)
        document[key] = value
        self.controller.apply_assumptions_json(json.dumps(document))
        return self._run_central()

    def test_withdrawal_strategy_flows_from_flexible_document_into_projection(self):
        baseline = self._run_central()
        updated = self._edit_and_run("withdrawal_strategy", "ISA_FIRST")

        self.assertNotEqual(baseline, updated)
        self.assertEqual(self.application.assumptions.get("withdrawal_strategy"), "ISA_FIRST")

    def test_starting_isa_flows_from_flexible_document_into_projection(self):
        statistics = PortfolioHistoricalStatisticsCalculator().calculate(
            self.controller.allocations, self.controller.fund_returns
        )
        baseline_result = RetirementPlanner(self.application.assumptions).run_with_portfolio_statistics(
            statistics, "central"
        )
        baseline_isa = baseline_result.timeline[-1].isa_closing

        document = copy.deepcopy(self.application.assumptions.data)
        document["starting_isa"] = 300000
        self.controller.apply_assumptions_json(json.dumps(document))
        updated_result = RetirementPlanner(self.application.assumptions).run_with_portfolio_statistics(
            statistics, "central"
        )
        updated_isa = updated_result.timeline[-1].isa_closing

        self.assertNotEqual(baseline_isa, updated_isa)
        self.assertGreater(updated_isa, baseline_isa)
        self.assertEqual(self.application.assumptions.get("starting_isa"), 300000)

    def test_spending_and_inflation_linkage_flow_from_flexible_document_into_projection(self):
        baseline = self._run_central()
        document = copy.deepcopy(self.application.assumptions.data)
        document["spending_phase_1"] = 45000
        document["inflation_link_spending"] = False
        self.controller.apply_assumptions_json(json.dumps(document))
        updated = self._run_central()

        self.assertNotEqual(baseline, updated)
        self.assertEqual(self.application.assumptions.get("spending_phase_1"), 45000)
        self.assertFalse(self.application.assumptions.get("inflation_link_spending"))

    def test_saved_flexible_assumptions_reload_into_projection_unchanged(self):
        baseline = self._run_central()
        document = copy.deepcopy(self.application.assumptions.data)
        document["starting_isa"] = 300000
        document["withdrawal_strategy"] = "ISA_FIRST"
        self.controller.apply_assumptions_json(json.dumps(document))
        changed = self._run_central()
        self.assertNotEqual(baseline, changed)

        self.controller.save()
        self.controller.reload_saved()
        reloaded = self._run_central()

        self.assertEqual(changed, reloaded)
        with self.path.open("r", encoding="utf-8") as handle:
            persisted = json.load(handle)
        self.assertEqual(persisted["starting_isa"], 300000)
        self.assertEqual(persisted["withdrawal_strategy"], "ISA_FIRST")


if __name__ == "__main__":
    unittest.main()

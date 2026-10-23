import copy
import os
import tempfile
import unittest

from planner.assumptions import AssumptionChange, Assumptions
from planner.planner import RetirementPlanner
from planner.recommendations.report_adapter import RecommendationReportAdapter
from planner.risk_engine import RiskEngine
from planner.scenarios.scenario import Scenario
from planner.scenarios.scenario_manager import ScenarioManager


class TestProjectionAudit(unittest.TestCase):

    def setUp(self):
        self.base = Assumptions()

    def test_planner_result_contains_no_changes_for_base_projection(self):
        result = RetirementPlanner(self.base).run()
        self.assertEqual(result.assumption_changes, ())

    def test_planner_result_captures_changed_assumption(self):
        assumptions = copy.deepcopy(self.base)
        original = assumptions.get("target_net_income")
        assumptions.set("target_net_income", original + 1000)

        result = RetirementPlanner(assumptions).run()

        self.assertIn(
            AssumptionChange(
                "target_net_income",
                original,
                original + 1000,
            ),
            result.assumption_changes,
        )

    def test_retirement_age_scenario_change_is_captured(self):
        assumptions = copy.deepcopy(self.base)
        assumptions.set("retirement_age", 62)

        result = RetirementPlanner(assumptions).run()

        self.assertIn(
            AssumptionChange(
                "retirement_age",
                self.base.get("retirement_age"),
                62,
            ),
            result.assumption_changes,
        )

    def test_report_adapter_exposes_projection_changes(self):
        assumptions = copy.deepcopy(self.base)
        assumptions.set("retirement_age", 62)
        result = RetirementPlanner(assumptions).run()

        manager = ScenarioManager()
        for age in (62, 63, 64):
            scenario_assumptions = copy.deepcopy(self.base)
            scenario_assumptions.set("retirement_age", age)
            manager.add(Scenario(f"Retire {age}", scenario_assumptions))

        decision = manager.decision_summary()
        recommendations = manager.recommendations()
        risk = RiskEngine().analyse(result.timeline)
        report = RecommendationReportAdapter().build(
            assumptions, result, decision, recommendations, risk
        )

        self.assertEqual(len(report["assumption_changes"]), 1)
        self.assertEqual(report["assumption_changes"][0]["path"], "retirement_age")
        self.assertEqual(report["assumption_changes"][0]["after"], 62)

    def test_saved_configuration_is_clean_for_next_projection(self):
        with tempfile.TemporaryDirectory() as directory:
            filename = os.path.join(directory, "assumptions.json")
            source = "data/assumptions.json"
            with open(source, "r", encoding="utf-8") as source_file:
                with open(filename, "w", encoding="utf-8") as target_file:
                    target_file.write(source_file.read())

            assumptions = Assumptions(filename)
            assumptions.set("retirement_age", 62)
            assumptions.save()

            result = RetirementPlanner(assumptions).run()
            self.assertEqual(result.assumption_changes, ())

    def test_projection_audit_is_a_snapshot(self):
        assumptions = copy.deepcopy(self.base)
        assumptions.set("retirement_age", 62)
        result = RetirementPlanner(assumptions).run()

        assumptions.set("retirement_age", 63)

        self.assertEqual(result.assumption_changes[0].after, 62)


if __name__ == "__main__":
    unittest.main()

import copy
import io
import unittest
from contextlib import redirect_stdout

from planner.assumptions import Assumptions
from planner.planner import RetirementPlanner
from planner.recommendations.report_adapter import RecommendationReportAdapter
from planner.risk_engine import RiskEngine
from planner.scenarios.scenario import Scenario
from planner.scenarios.scenario_manager import ScenarioManager
from planner.services.retirement_solver import RetirementSolver
from reports.recommendation_report import RecommendationReport


class TestProjectionAuditContext(unittest.TestCase):

    def setUp(self):
        self.base = Assumptions()

    def test_direct_projection_defaults_to_user_assumption_context(self):
        assumptions = copy.deepcopy(self.base)
        assumptions.set("target_net_income", assumptions.get("target_net_income") + 1000)

        result = RetirementPlanner(assumptions).run()

        self.assertEqual(result.audit_context, "user")

    def test_scenario_projection_is_marked_as_scenario(self):
        assumptions = copy.deepcopy(self.base)
        assumptions.set("retirement_age", 62)
        manager = ScenarioManager()
        manager.add(Scenario("Retire 62", assumptions))

        result = manager.run_all()[0]

        self.assertEqual(result.audit_context, "scenario")

    def test_solver_projection_is_marked_as_recommendation(self):
        result = RetirementSolver(self.base)._run_at_age(62)

        self.assertEqual(result.audit_context, "recommendation")

    def test_report_adapter_labels_user_changes(self):
        assumptions = copy.deepcopy(self.base)
        assumptions.set("target_net_income", assumptions.get("target_net_income") + 1000)
        result = RetirementPlanner(assumptions).run()

        report = RecommendationReportAdapter().build(
            assumptions,
            result,
            None,
            [],
            RiskEngine().analyse(result.timeline),
        )

        self.assertEqual(report["assumption_changes"][0]["category"], "USER ASSUMPTION")

    def test_report_adapter_labels_scenario_changes(self):
        assumptions = copy.deepcopy(self.base)
        assumptions.set("retirement_age", 62)
        result = RetirementPlanner(assumptions, audit_context="scenario").run()

        report = RecommendationReportAdapter().build(
            assumptions,
            result,
            None,
            [],
            RiskEngine().analyse(result.timeline),
        )

        self.assertEqual(report["assumption_changes"][0]["category"], "SCENARIO")

    def test_console_report_includes_change_category(self):
        assumptions = copy.deepcopy(self.base)
        assumptions.set("retirement_age", 62)
        result = RetirementPlanner(assumptions, audit_context="recommendation").run()

        report = RecommendationReportAdapter().build(
            assumptions,
            result,
            None,
            [],
            RiskEngine().analyse(result.timeline),
        )

        output = io.StringIO()
        with redirect_stdout(output):
            RecommendationReport().print(report)

        self.assertIn("[RECOMMENDATION] retirement_age", output.getvalue())


if __name__ == "__main__":
    unittest.main()

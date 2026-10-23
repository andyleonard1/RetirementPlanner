import copy
import io
import unittest
from types import SimpleNamespace
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

    def test_report_adapter_describes_retirement_age_scenario_change(self):
        assumptions = copy.deepcopy(self.base)
        assumptions.set("retirement_age", 62)
        result = RetirementPlanner(assumptions, audit_context="scenario").run()
        report = RecommendationReportAdapter().build(
            assumptions, result, None, [], RiskEngine().analyse(result.timeline)
        )
        change = report["assumption_changes"][0]
        self.assertEqual(
            change["description"],
            "Retirement age selected for scenario analysis.",
        )

    def test_report_adapter_describes_recommendation_change(self):
        assumptions = copy.deepcopy(self.base)
        assumptions.set("retirement_age", 62)
        result = RetirementPlanner(assumptions, audit_context="recommendation").run()
        report = RecommendationReportAdapter().build(
            assumptions, result, None, [], RiskEngine().analyse(result.timeline)
        )
        self.assertIn(
            "recommendation solver",
            report["assumption_changes"][0]["description"],
        )

    def test_report_adapter_formats_missing_change_values(self):
        class FakeChange:
            path = "new_assumption"
            before = None
            after = 42

        result = copy.deepcopy(self.base)
        result = SimpleNamespace(
            summary={"ending_assets": 0, "ending_pension": 0, "ending_isa": 0, "ending_savings": 0, "total_tax": 0},
            timeline=[], assumption_changes=(FakeChange(),), audit_context="user"
        )
        report = RecommendationReportAdapter().build(
            self.base, result, None, [], SimpleNamespace(rating="LOW", score=0, risks=[])
        )
        self.assertEqual(report["assumption_changes"][0]["before_display"], "not set")
        self.assertEqual(report["assumption_changes"][0]["after_display"], "42")

    def test_console_report_includes_human_description_and_values(self):
        assumptions = copy.deepcopy(self.base)
        assumptions.set("retirement_age", 62)
        result = RetirementPlanner(assumptions, audit_context="scenario").run()
        report = RecommendationReportAdapter().build(
            assumptions, result, None, [], RiskEngine().analyse(result.timeline)
        )
        output = io.StringIO()
        with redirect_stdout(output):
            RecommendationReport().print(report)
        text = output.getvalue()
        self.assertIn("Retirement age selected for scenario analysis.", text)
        self.assertIn("retirement_age: 63 -> 62", text)

    def test_report_adapter_describes_common_user_assumption(self):
        assumptions = copy.deepcopy(self.base)
        assumptions.set("target_net_income", assumptions.get("target_net_income") + 1000)
        result = RetirementPlanner(assumptions).run()
        report = RecommendationReportAdapter().build(
            assumptions, result, None, [], RiskEngine().analyse(result.timeline)
        )
        self.assertEqual(
            report["assumption_changes"][0]["description"],
            "Target net income changed for this projection.",
        )

    def test_report_adapter_formats_float_values_without_noise(self):
        adapter = RecommendationReportAdapter()
        self.assertEqual(adapter._format_change_value(0.0400), "0.04")

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

        self.assertIn("[RECOMMENDATION] Retirement age evaluated by the recommendation solver.", output.getvalue())


if __name__ == "__main__":
    unittest.main()

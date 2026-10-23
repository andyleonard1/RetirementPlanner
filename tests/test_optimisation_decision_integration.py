import unittest
from types import SimpleNamespace

from planner.optimisation_decision_support import OptimisationDecisionSupport
from planner.planner_result import PlannerResult
from planner.recommendations.recommendation import Recommendation
from planner.recommendations.report_adapter import RecommendationReportAdapter


class OptimisationDecisionIntegrationTests(unittest.TestCase):

    def make_decision(self):
        return OptimisationDecisionSupport().assess({
            "personal_allowance": [(63, 10000), (64, 11000)],
            "basic_rate_band": [(63, 20000), (64, 21000)],
        })

    def make_report_inputs(self):
        assumptions = SimpleNamespace(
            get=lambda key: "pension_first" if key == "withdrawal_strategy" else 63
        )
        result = SimpleNamespace(
            summary={
                "ending_assets": 900000,
                "ending_pension": 500000,
                "ending_isa": 250000,
                "ending_savings": 150000,
                "total_tax": 100000,
            },
            assumption_changes=(),
            audit_context="user",
            optimisation_decision=self.make_decision(),
        )
        decision = SimpleNamespace(recommended_age=63, total_score=82.5)
        recommendations = [Recommendation(1, "Age", "Age 63 is recommended.", "63")]
        risk = SimpleNamespace(rating="LOW", score=10, risks=[])
        return assumptions, result, decision, recommendations, risk

    def test_planner_result_has_optional_optimisation_decision(self):
        result = PlannerResult(timeline=[], summary={})
        self.assertIsNone(result.optimisation_decision)

    def test_adapter_exposes_optimisation_decision(self):
        inputs = self.make_report_inputs()
        report = RecommendationReportAdapter().build(*inputs)
        self.assertEqual(report["optimisation_decision"]["higher_policy"], "basic_rate_band")

    def test_adapter_preserves_materiality(self):
        inputs = self.make_report_inputs()
        report = RecommendationReportAdapter().build(*inputs)
        self.assertTrue(report["optimisation_decision"]["material"])

    def test_adapter_exposes_recommendation_text(self):
        inputs = self.make_report_inputs()
        report = RecommendationReportAdapter().build(*inputs)
        self.assertIn("basic_rate_band", report["optimisation_decision"]["recommendation"])

    def test_adapter_exposes_explanation_text(self):
        inputs = self.make_report_inputs()
        report = RecommendationReportAdapter().build(*inputs)
        self.assertIn("average difference", report["optimisation_decision"]["explanation"])

    def test_adapter_remains_backward_compatible_without_decision(self):
        assumptions, result, decision, recommendations, risk = self.make_report_inputs()
        del result.optimisation_decision
        report = RecommendationReportAdapter().build(
            assumptions, result, decision, recommendations, risk
        )
        self.assertIsNone(report["optimisation_decision"])


if __name__ == "__main__":
    unittest.main()

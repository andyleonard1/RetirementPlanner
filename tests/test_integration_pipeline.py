import copy
import os
import tempfile
import unittest

from planner.assumptions import Assumptions
from planner.planner import RetirementPlanner
from planner.risk_engine import RiskEngine
from planner.scenarios.scenario import Scenario
from planner.scenarios.scenario_manager import ScenarioManager
from planner.chart_engine import ChartEngine
from planner.recommendations.report_adapter import RecommendationReportAdapter
from reports.pdf_report import PDFReport


class TestIntegrationPipeline(unittest.TestCase):
    """Exercise the principal application pipeline with real components."""

    def setUp(self):
        self.assumptions = Assumptions()

    def _manager(self, ages=(62, 63, 64)):
        manager = ScenarioManager()
        for age in ages:
            assumptions = copy.deepcopy(self.assumptions)
            assumptions.set("retirement_age", age)
            manager.add(
                Scenario(
                    name=f"Retire {age}",
                    assumptions=assumptions,
                )
            )
        return manager

    def test_real_planner_produces_complete_result(self):
        result = RetirementPlanner(self.assumptions).run()

        self.assertTrue(result.timeline)
        self.assertEqual(len(result.timeline), 28)
        self.assertIn("ending_assets", result.summary)
        self.assertIn("ending_pension", result.summary)
        self.assertIn("ending_isa", result.summary)
        self.assertIn("ending_savings", result.summary)
        self.assertEqual(result.success, result.summary["success"])

    def test_scenario_to_decision_to_recommendation_pipeline(self):
        manager = self._manager()

        decision = manager.decision_summary()
        comparisons = manager.retirement_age_comparison()
        recommendations = manager.recommendations()

        self.assertIsNotNone(decision)
        self.assertEqual(len(comparisons), 3)
        self.assertEqual(
            [item.retirement_age for item in comparisons],
            [62, 63, 64],
        )
        self.assertTrue(recommendations)
        self.assertIn(
            decision.recommended_age,
            [item.retirement_age for item in comparisons],
        )
        self.assertTrue(
            next(
                item.success
                for item in comparisons
                if item.retirement_age == decision.recommended_age
            )
        )

    def test_real_recommendation_and_risk_feed_report_adapter(self):
        manager = self._manager()
        decision = manager.decision_summary()
        recommendations = manager.recommendations()

        recommended_age = (
            decision.recommended_age
            if decision is not None
            else self.assumptions.get("retirement_age")
        )
        assumptions = copy.deepcopy(self.assumptions)
        assumptions.set("retirement_age", recommended_age)

        result = RetirementPlanner(assumptions).run()
        risk = RiskEngine().analyse(result.timeline)
        report = RecommendationReportAdapter().build(
            assumptions,
            result,
            decision,
            recommendations,
            risk,
        )

        for key in (
            "strategy",
            "confidence",
            "reasons",
            "ending_assets",
            "ending_pension",
            "ending_isa",
            "ending_savings",
            "total_tax",
            "risk_rating",
            "risk_score",
            "risk_messages",
            "recommended_age",
        ):
            self.assertIn(key, report)

        self.assertEqual(report["recommended_age"], recommended_age)
        self.assertEqual(report["ending_assets"], result.summary["ending_assets"])
        self.assertEqual(report["risk_score"], risk.score)

    def test_real_timeline_generates_charts_and_pdf(self):
        result = RetirementPlanner(self.assumptions).run()
        manager = self._manager()
        decision = manager.decision_summary()
        comparisons = manager.retirement_age_comparison()

        with tempfile.TemporaryDirectory() as directory:
            charts = os.path.join(directory, "charts")
            ChartEngine(charts).create_all(result.timeline)

            self.assertTrue(os.path.exists(os.path.join(charts, "pension.png")))
            self.assertTrue(os.path.exists(os.path.join(charts, "assets.png")))

            filename = os.path.join(directory, "integration-report.pdf")
            cwd = os.getcwd()
            try:
                os.chdir(directory)
                PDFReport().create(
                    result,
                    decision,
                    comparisons,
                    filename,
                )
            finally:
                os.chdir(cwd)

            self.assertTrue(os.path.exists(filename))
            self.assertGreater(os.path.getsize(filename), 1000)


if __name__ == "__main__":
    unittest.main()

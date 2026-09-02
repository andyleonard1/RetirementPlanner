import unittest
from types import SimpleNamespace

from planner.recommendations.recommendation import Recommendation
from planner.recommendations.report_adapter import RecommendationReportAdapter
from planner.risk_engine import RiskEngine


class TestRecommendationReportAdapter(unittest.TestCase):

    def setUp(self):
        self.assumptions = SimpleNamespace(
            get=lambda key: "pension_first"
            if key == "withdrawal_strategy"
            else 63
        )

        self.result = SimpleNamespace(
            summary={
                "ending_assets": 900000,
                "ending_pension": 500000,
                "ending_isa": 250000,
                "ending_savings": 150000,
                "total_tax": 100000,
            },
            timeline=[],
        )

        self.decision = SimpleNamespace(
            recommended_age=62,
            total_score=82.5,
        )

        self.recommendations = [
            Recommendation(
                priority=1,
                title="Recommended Retirement Age",
                message="Age 62 is the recommended age.",
                impact="Score 82.5",
            ),
            Recommendation(
                priority=4,
                title="Plan Successful",
                message="Scenario succeeds.",
                impact="£900,000",
            ),
        ]

        self.risk = SimpleNamespace(
            rating="LOW",
            score=10,
            risks=["Pension never exhausted."],
        )

    def test_build_maps_current_objects_to_report_contract(self):
        report = RecommendationReportAdapter().build(
            self.assumptions,
            self.result,
            self.decision,
            self.recommendations,
            self.risk,
        )

        self.assertEqual(report["recommended_age"], 62)
        self.assertEqual(report["confidence"], "HIGH")
        self.assertEqual(report["ending_assets"], 900000)
        self.assertEqual(report["risk_rating"], "LOW")
        self.assertEqual(report["risk_score"], 10)
        self.assertEqual(
            report["reasons"],
            ["Age 62 is the recommended age."],
        )

    def test_confidence_thresholds(self):
        adapter = RecommendationReportAdapter()

        self.assertEqual(adapter._confidence(95), "VERY HIGH")
        self.assertEqual(adapter._confidence(80), "HIGH")
        self.assertEqual(adapter._confidence(65), "MEDIUM")
        self.assertEqual(adapter._confidence(40), "LOW")

    def test_empty_recommendations_still_produce_report_reasons(self):
        report = RecommendationReportAdapter().build(
            self.assumptions,
            self.result,
            self.decision,
            [],
            self.risk,
        )

        self.assertTrue(report["reasons"])


if __name__ == "__main__":
    unittest.main()

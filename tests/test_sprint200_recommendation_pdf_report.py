import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from pypdf import PdfReader

from planner.assumptions import Assumptions
from planner.planner import RetirementPlanner
from planner.recommendations.report_adapter import RecommendationReportAdapter
from planner.recommendations.recommendation_quality import RecommendationQualityEngine
from planner.risk_engine import RiskEngine
from planner.scenarios.scenario import Scenario
from planner.scenarios.scenario_manager import ScenarioManager
from reports.recommendation_pdf_report import RecommendationPDFReport
from recommend import build_scenarios


class Sprint200RecommendationPDFReportTests(unittest.TestCase):
    def make_report(self):
        assumptions = Assumptions()
        manager = ScenarioManager()
        for scenario in build_scenarios(assumptions):
            manager.add(scenario)
        decision = manager.decision_summary()
        recommendations = manager.recommendations()
        recommended_age = decision.recommended_age if decision is not None else assumptions.get("retirement_age")
        recommended_assumptions = Assumptions()
        recommended_assumptions.data = assumptions.data.copy()
        recommended_assumptions.set("retirement_age", recommended_age)
        result = RetirementPlanner(recommended_assumptions).run()
        recommendations.insert(0, RecommendationQualityEngine().build(decision, result.optimisation_decision))
        risk = RiskEngine().analyse(result.timeline)
        return RecommendationReportAdapter().build(
            recommended_assumptions, result, decision, recommendations, risk
        )

    def test_pdf_contains_recommendation_and_risk_sections(self):
        report = self.make_report()
        with tempfile.TemporaryDirectory() as directory:
            path = RecommendationPDFReport().create(report, Path(directory) / "recommendation.pdf")
            text = "\n".join(page.extract_text() or "" for page in PdfReader(path).pages)
        self.assertIn("Recommendation Report", text)
        self.assertIn("Recommendation Summary", text)
        self.assertIn("Why this recommendation?", text)
        self.assertIn("Projected Position", text)
        self.assertIn("Retirement Risk", text)
        self.assertIn(str(report["recommended_age"]), text)
        self.assertIn(str(report["confidence"]), text)

    def test_pdf_renderer_does_not_mutate_supplied_report(self):
        report = self.make_report()
        before = repr(report)
        with tempfile.TemporaryDirectory() as directory:
            RecommendationPDFReport().create(report, Path(directory) / "recommendation.pdf")
        self.assertEqual(before, repr(report))

    def test_pdf_keeps_report_pagination_clean(self):
        report = self.make_report()
        with tempfile.TemporaryDirectory() as directory:
            path = RecommendationPDFReport().create(
                report, Path(directory) / "recommendation.pdf"
            )
            pages = PdfReader(path).pages
            page_text = [page.extract_text() or "" for page in pages]

        self.assertEqual(len(pages), 3)
        self.assertTrue(any("Retirement Risk" in text for text in page_text))
        self.assertTrue(any("Decision Support" in text for text in page_text))
        self.assertTrue(any("Configuration Changes" in text for text in page_text))
        self.assertIn("Target spending achieved every year.", page_text[1])

    def test_recommend_cli_can_export_pdf(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "recommendation.pdf"
            completed = subprocess.run(
                [sys.executable, "recommend.py", "--pdf", str(path)],
                capture_output=True,
                text=True,
                timeout=90,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertIn("PDF recommendation report exported", completed.stdout)
            self.assertTrue(path.exists())
            self.assertGreater(len(PdfReader(path).pages), 0)

    def test_invalid_recommendation_inputs_are_rejected(self):
        report = RecommendationPDFReport()
        with self.assertRaises(TypeError):
            report.create(object())
        with self.assertRaises(ValueError):
            report.create({"strategy": "ISA_FIRST"})


if __name__ == "__main__":
    unittest.main()

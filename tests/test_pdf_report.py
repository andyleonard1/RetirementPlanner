import base64
import os
import tempfile
import unittest
from dataclasses import dataclass
from types import SimpleNamespace

from reports.pdf_report import PDFReport
from planner.scenarios.decision_summary import DecisionSummary
from planner.scenarios.retirement_age_comparison import RetirementAgeComparison
from planner.recommendations.sensitivity_runner import SensitivitySummary, SensitivityRun
from planner.recommendations.sensitivity_grid import SensitivityCase
from planner.recommendations.sensitivity_driver_analysis import SensitivityDriverAnalysis


# Minimal valid 1x1 PNG used to keep the PDF test self-contained.
PNG_1X1 = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
)


@dataclass
class FakeResult:
    summary: dict
    success: bool


class TestPDFReport(unittest.TestCase):

    def test_create_uses_current_planner_and_scenario_objects(self):

        result = FakeResult(
            summary={
                "strategy": "pension_first",
                "ending_pension": 500000,
                "ending_savings": 50000,
                "ending_isa": 100000,
                "ending_assets": 650000,
                "total_tax": 20000,
                "failure_reason": None,
            },
            success=True,
        )

        decision = DecisionSummary(
            recommended_age=60,
            ending_pension=500000,
            ending_isa=100000,
            ending_savings=50000,
            ending_assets=650000,
            later_age=61,
            later_ending_assets=700000,
            additional_assets_from_waiting=50000,
            earliest_age_score=95.0,
            ending_assets_score=80.0,
            waiting_efficiency_score=70.0,
            total_score=84.0,
        )

        comparisons = [
            RetirementAgeComparison(
                retirement_age=60,
                success=True,
                ending_assets=650000,
                ending_pension=500000,
                ending_isa=100000,
                ending_savings=50000,
                total_tax=20000,
            ),
            RetirementAgeComparison(
                retirement_age=61,
                success=True,
                ending_assets=700000,
                ending_pension=540000,
                ending_isa=110000,
                ending_savings=50000,
                total_tax=22000,
                change_from_previous_age=50000,
            ),
        ]

        with tempfile.TemporaryDirectory() as directory:
            charts = os.path.join(directory, "charts")
            os.makedirs(charts)

            with open(os.path.join(charts, "pension.png"), "wb") as handle:
                handle.write(PNG_1X1)

            with open(os.path.join(charts, "assets.png"), "wb") as handle:
                handle.write(PNG_1X1)

            filename = os.path.join(directory, "RetirementReport.pdf")
            cwd = os.getcwd()
            try:
                os.chdir(directory)
                PDFReport().create(result, decision, comparisons, filename)
            finally:
                os.chdir(cwd)

            self.assertTrue(os.path.exists(filename))
            self.assertGreater(os.path.getsize(filename), 0)

    def test_create_accepts_sensitivity_analysis(self):

        result = FakeResult(
            summary={
                "strategy": "pension_first",
                "ending_pension": 500000,
                "ending_savings": 50000,
                "ending_isa": 100000,
                "ending_assets": 650000,
                "total_tax": 20000,
                "failure_reason": None,
            },
            success=True,
        )

        runs = tuple(
            SensitivityRun(
                SensitivityCase(0.04, 35000, 0.04),
                age,
            )
            for age in (56, 56, 58, 67)
        )

        sensitivity = SensitivitySummary(
            runs=runs,
            recommended_ages=(56, 56, 58, 67),
            min_age=56,
            max_age=67,
            most_common_age=56,
            most_common_count=2,
            total_cases=4,
        )

        drivers = SensitivityDriverAnalysis().analyse(runs)

        decision = DecisionSummary(
            recommended_age=56,
            ending_pension=500000,
            ending_isa=100000,
            ending_savings=50000,
            ending_assets=650000,
            later_age=57,
            later_ending_assets=700000,
            additional_assets_from_waiting=50000,
            earliest_age_score=95.0,
            ending_assets_score=80.0,
            waiting_efficiency_score=70.0,
            total_score=84.0,
        )

        with tempfile.TemporaryDirectory() as directory:
            charts = os.path.join(directory, "charts")
            os.makedirs(charts)
            for name in ("pension.png", "assets.png"):
                with open(os.path.join(charts, name), "wb") as handle:
                    handle.write(PNG_1X1)

            filename = os.path.join(directory, "SensitivityReport.pdf")
            cwd = os.getcwd()
            try:
                os.chdir(directory)
                PDFReport().create(
                    result,
                    decision,
                    [],
                    filename,
                    sensitivity=sensitivity,
                    driver_analysis=drivers,
                )
            finally:
                os.chdir(cwd)

            self.assertTrue(os.path.exists(filename))
            self.assertGreater(os.path.getsize(filename), 0)


if __name__ == "__main__":
    unittest.main()

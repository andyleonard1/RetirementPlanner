import unittest
from io import StringIO
from contextlib import redirect_stdout

from planner.report import ConsoleReport
from planner.scenarios.decision_summary import DecisionSummary
from planner.scenarios.retirement_age_comparison import RetirementAgeComparison


class TestConsoleReport(unittest.TestCase):

    def setUp(self):

        self.report = ConsoleReport()

        self.timeline = []

        self.summary = {
            "strategy": "pension_first",
            "ending_pension": 500000,
            "ending_savings": 50000,
            "ending_isa": 100000,
            "ending_assets": 650000,
            "gross_pension": 300000,
            "net_pension": 280000,
            "state_pension": 150000,
            "total_tax": 20000,
        }

    # -------------------------------------------------

    def test_report_can_run_without_decision(self):

        output = StringIO()

        with redirect_stdout(output):

            self.report.print(
                self.timeline,
                self.summary,
            )

        self.assertIn(
            "RETIREMENT SUMMARY",
            output.getvalue(),
        )

    # -------------------------------------------------

    def test_report_includes_retirement_age_comparison(self):

        age_comparison = [
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

        output = StringIO()

        with redirect_stdout(output):

            self.report.print(
                self.timeline,
                self.summary,
                age_comparison=age_comparison,
            )

        text = output.getvalue()

        self.assertIn(
            "RETIREMENT AGE COMPARISON",
            text,
        )

        self.assertIn(
            "60",
            text,
        )

        self.assertIn(
            "SUCCESS",
            text,
        )

        self.assertIn(
            "£650,000",
            text,
        )

        self.assertIn(
            "£50,000",
            text,
        )

    # -------------------------------------------------

    def test_report_includes_decision_summary(self):

        decision = DecisionSummary(
            recommended_age=60,
            ending_pension=500000,
            ending_isa=100000,
            ending_savings=50000,
            ending_assets=650000,
            later_age=61,
            later_ending_assets=700000,
            additional_assets_from_waiting=50000,
        )

        output = StringIO()

        with redirect_stdout(output):

            self.report.print(
                self.timeline,
                self.summary,
                decision,
            )

        text = output.getvalue()

        self.assertIn(
            "RETIREMENT DECISION",
            text,
        )

        self.assertIn(
            "Recommended Age",
            text,
        )

        self.assertIn(
            "60",
            text,
        )

        self.assertIn(
            "£650,000",
            text,
        )

        self.assertIn(
            "£50,000",
            text,
        )


if __name__ == "__main__":
    unittest.main()

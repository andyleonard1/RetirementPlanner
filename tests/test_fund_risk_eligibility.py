import unittest

from planner.funds.fund_import import ImportedFundReturn
from planner.funds.fund_risk_eligibility import FundRiskEligibilityAnalyzer


def history(fund, start, end):
    return [
        ImportedFundReturn(fund, year, 0.05)
        for year in range(start, end + 1)
    ]


class FundRiskEligibilityTests(unittest.TestCase):
    def test_sufficient_history_is_risk_eligible(self):
        result = FundRiskEligibilityAnalyzer().analyze(
            history("A", 2020, 2024)
        )[0]

        self.assertTrue(result.eligible)
        self.assertEqual(result.reason, "Eligible for risk analysis.")

    def test_short_history_is_excluded(self):
        result = FundRiskEligibilityAnalyzer().analyze(
            history("A", 2022, 2024)
        )[0]

        self.assertFalse(result.eligible)
        self.assertIn("Excluded from risk analysis", result.reason)

    def test_missing_year_excludes_fund(self):
        records = history("A", 2020, 2024)
        records = [record for record in records if record.year != 2022]

        result = FundRiskEligibilityAnalyzer().analyze(records)[0]

        self.assertFalse(result.eligible)
        self.assertIn("Excluded from risk analysis", result.reason)

    def test_projection_only_requirement_does_not_block_risk(self):
        result = FundRiskEligibilityAnalyzer(
            risk_minimum_years=5,
            projection_minimum_years=10,
        ).analyze(history("A", 2020, 2024))[0]

        self.assertTrue(result.eligible)

    def test_eligible_funds_returns_only_eligible_identifiers(self):
        records = history("A", 2020, 2024) + history("B", 2022, 2024)

        result = FundRiskEligibilityAnalyzer().eligible_funds(records)

        self.assertEqual(result, ("A",))

    def test_multiple_funds_are_independent(self):
        records = history("A", 2020, 2024) + history("B", 2020, 2024)
        result = FundRiskEligibilityAnalyzer().analyze(records)

        self.assertEqual([item.fund_identifier for item in result], ["A", "B"])
        self.assertTrue(all(item.eligible for item in result))


if __name__ == "__main__":
    unittest.main()

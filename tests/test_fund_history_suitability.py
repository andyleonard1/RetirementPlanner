import unittest

from planner.funds.fund_history_suitability import FundHistorySuitabilityAnalyzer
from planner.funds.fund_import import ImportedFundReturn


def history(fund, start, end):
    return [
        ImportedFundReturn(fund, year, 0.05)
        for year in range(start, end + 1)
    ]


class FundHistorySuitabilityTests(unittest.TestCase):
    def test_five_continuous_years_are_suitable_for_risk_only(self):
        result = FundHistorySuitabilityAnalyzer().analyze(
            history("A", 2020, 2024)
        )[0]
        self.assertTrue(result.suitable_for_risk_metrics)
        self.assertFalse(result.suitable_for_projection)

    def test_ten_continuous_years_are_suitable_for_projection(self):
        result = FundHistorySuitabilityAnalyzer().analyze(
            history("A", 2015, 2024)
        )[0]
        self.assertTrue(result.suitable_for_risk_metrics)
        self.assertTrue(result.suitable_for_projection)

    def test_missing_year_blocks_risk_suitability(self):
        records = history("A", 2020, 2024)
        records = [record for record in records if record.year != 2022]
        result = FundHistorySuitabilityAnalyzer().analyze(records)[0]
        self.assertFalse(result.suitable_for_risk_metrics)
        self.assertFalse(result.suitable_for_projection)
        self.assertIn("missing years", result.reason)

    def test_short_history_is_not_suitable(self):
        result = FundHistorySuitabilityAnalyzer().analyze(
            history("A", 2022, 2024)
        )[0]
        self.assertFalse(result.suitable_for_risk_metrics)
        self.assertFalse(result.suitable_for_projection)

    def test_projection_threshold_is_configurable(self):
        result = FundHistorySuitabilityAnalyzer(
            risk_minimum_years=3,
            projection_minimum_years=4,
        ).analyze(history("A", 2021, 2024))[0]
        self.assertTrue(result.suitable_for_risk_metrics)
        self.assertTrue(result.suitable_for_projection)

    def test_multiple_funds_are_assessed_independently(self):
        records = history("A", 2015, 2024) + history("B", 2022, 2024)
        result = FundHistorySuitabilityAnalyzer().analyze(records)
        self.assertEqual([item.fund_identifier for item in result], ["A", "B"])
        self.assertTrue(result[0].suitable_for_projection)
        self.assertFalse(result[1].suitable_for_risk_metrics)

if __name__ == "__main__":
    unittest.main()

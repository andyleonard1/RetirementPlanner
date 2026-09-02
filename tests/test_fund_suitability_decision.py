import unittest

from planner.funds.fund_import import ImportedFundReturn
from planner.funds.fund_suitability_decision import (
    FundSuitabilityDecisionEngine,
)


def history(fund, start, end):
    return [
        ImportedFundReturn(fund, year, 0.05)
        for year in range(start, end + 1)
    ]


class FundSuitabilityDecisionTests(unittest.TestCase):
    def test_ten_year_history_is_suitable_for_both(self):
        result = FundSuitabilityDecisionEngine().decide(
            history("A", 2015, 2024)
        )[0]

        self.assertTrue(result.risk_modelling)
        self.assertTrue(result.projection_modelling)
        self.assertEqual(result.status, "suitable_for_risk_and_projection")
        self.assertIn("both risk and fund-informed projection", result.reason)

    def test_five_year_history_is_risk_only(self):
        result = FundSuitabilityDecisionEngine().decide(
            history("A", 2020, 2024)
        )[0]

        self.assertTrue(result.risk_modelling)
        self.assertFalse(result.projection_modelling)
        self.assertEqual(result.status, "suitable_for_risk_only")
        self.assertIn("risk metrics", result.reason)

    def test_short_history_is_not_suitable(self):
        result = FundSuitabilityDecisionEngine().decide(
            history("A", 2022, 2024)
        )[0]

        self.assertFalse(result.risk_modelling)
        self.assertFalse(result.projection_modelling)
        self.assertEqual(result.status, "not_suitable")

    def test_gap_in_history_is_not_suitable(self):
        records = history("A", 2015, 2024)
        records = [r for r in records if r.year != 2019]

        result = FundSuitabilityDecisionEngine().decide(records)[0]

        self.assertFalse(result.risk_modelling)
        self.assertFalse(result.projection_modelling)
        self.assertEqual(result.status, "not_suitable")
        self.assertIn("missing years", result.reason)

    def test_thresholds_are_configurable(self):
        result = FundSuitabilityDecisionEngine(
            risk_minimum_years=3,
            projection_minimum_years=4,
        ).decide(history("A", 2021, 2024))[0]

        self.assertTrue(result.risk_modelling)
        self.assertTrue(result.projection_modelling)

    def test_multiple_funds_have_independent_decisions(self):
        result = FundSuitabilityDecisionEngine().decide(
            history("A", 2015, 2024) + history("B", 2020, 2024)
        )

        self.assertEqual([d.fund_identifier for d in result], ["A", "B"])
        self.assertEqual(
            result[0].status,
            "suitable_for_risk_and_projection",
        )
        self.assertEqual(result[1].status, "suitable_for_risk_only")


if __name__ == "__main__":
    unittest.main()

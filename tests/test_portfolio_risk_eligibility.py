import unittest
from planner.funds.fund_import import ImportedFundReturn
from planner.funds.portfolio_risk_eligibility import PortfolioRiskEligibilityIntegrator


def history(fund, start, end):
    return [ImportedFundReturn(fund, year, 0.05) for year in range(start, end + 1)]


class PortfolioRiskEligibilityIntegratorTests(unittest.TestCase):
    def setUp(self):
        self.integrator = PortfolioRiskEligibilityIntegrator()

    def test_eligible_fund_is_included(self):
        result = self.integrator.evaluate(history("A", 2020, 2024))
        self.assertEqual(result.included_funds, ("A",))
        self.assertEqual(result.excluded_funds, ())

    def test_ineligible_fund_is_excluded(self):
        result = self.integrator.evaluate(history("A", 2022, 2024))
        self.assertEqual(result.included_funds, ())
        self.assertEqual(result.excluded_funds, ("A",))
        self.assertEqual(len(result.exclusion_reasons), 1)

    def test_mixed_portfolio_is_split(self):
        result = self.integrator.evaluate(
            history("A", 2020, 2024) + history("B", 2022, 2024)
        )
        self.assertEqual(result.included_funds, ("A",))
        self.assertEqual(result.excluded_funds, ("B",))

    def test_excluded_fund_records_are_removed(self):
        records = history("A", 2020, 2024) + history("B", 2022, 2024)
        filtered = self.integrator.filter_records(records)
        self.assertEqual({r.fund_identifier for r in filtered}, {"A"})

    def test_all_eligible_records_are_preserved(self):
        records = history("A", 2020, 2024) + history("B", 2020, 2024)
        self.assertEqual(len(self.integrator.filter_records(records)), 10)

    def test_empty_portfolio_is_safe(self):
        result = self.integrator.evaluate([])
        self.assertEqual(result.included_funds, ())
        self.assertEqual(result.excluded_funds, ())
        self.assertEqual(result.exclusion_reasons, ())


if __name__ == "__main__":
    unittest.main()

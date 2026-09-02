import unittest

from planner.funds.fund_model import (
    Fund,
    FundAllocation,
    FundPortfolio,
)


class FundModelTests(unittest.TestCase):
    def test_single_fund_can_form_a_portfolio(self):
        fund = Fund("Example Provider", "Example Fund")
        portfolio = FundPortfolio.from_allocations([
            FundAllocation(fund, 100.0),
        ])
        self.assertEqual(len(portfolio.allocations), 1)
        self.assertEqual(portfolio.allocations[0].percentage, 100.0)

    def test_multiple_funds_are_supported(self):
        a = Fund("Provider A", "Fund A", "GB000A")
        b = Fund("Provider B", "Fund B", "GB000B")
        portfolio = FundPortfolio.from_allocations([
            FundAllocation(a, 60.0),
            FundAllocation(b, 40.0),
        ])
        self.assertEqual(len(portfolio.allocations), 2)

    def test_allocations_must_total_100_percent(self):
        fund = Fund("Provider", "Fund")
        with self.assertRaises(ValueError):
            FundPortfolio.from_allocations([
                FundAllocation(fund, 70.0),
            ])

    def test_negative_allocation_is_rejected(self):
        fund = Fund("Provider", "Fund")
        with self.assertRaises(ValueError):
            FundPortfolio.from_allocations([
                FundAllocation(fund, -1.0),
                FundAllocation(fund, 101.0),
            ])

    def test_charge_cannot_be_negative(self):
        with self.assertRaises(ValueError):
            Fund("Provider", "Fund", annual_charge=-0.01).validate()

    def test_provider_is_required(self):
        with self.assertRaises(ValueError):
            Fund("", "Fund").validate()

    def test_name_is_required(self):
        with self.assertRaises(ValueError):
            Fund("Provider", "").validate()


if __name__ == "__main__":
    unittest.main()

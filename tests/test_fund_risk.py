import unittest
from planner.funds.fund_history import AnnualFundReturn
from planner.funds.fund_risk import FundRiskAnalyzer

class FundRiskAnalyzerTests(unittest.TestCase):
    def test_single_return_volatility_is_zero(self):
        r = FundRiskAnalyzer([AnnualFundReturn(2024, 0.10)]).summary()
        self.assertEqual(r.volatility, 0.0)

    def test_volatility_is_sample_standard_deviation(self):
        r = FundRiskAnalyzer([
            AnnualFundReturn(2021, 0.10),
            AnnualFundReturn(2022, 0.20),
            AnnualFundReturn(2023, 0.30),
        ]).summary()
        self.assertAlmostEqual(r.volatility, 0.10)

    def test_negative_years_and_rate(self):
        r = FundRiskAnalyzer([
            AnnualFundReturn(2021, 0.10),
            AnnualFundReturn(2022, -0.20),
            AnnualFundReturn(2023, -0.05),
            AnnualFundReturn(2024, 0.15),
        ]).summary()
        self.assertEqual(r.negative_years, 2)
        self.assertAlmostEqual(r.negative_year_rate, 0.5)

    def test_maximum_drawdown(self):
        r = FundRiskAnalyzer([
            AnnualFundReturn(2021, 0.20),
            AnnualFundReturn(2022, -0.30),
            AnnualFundReturn(2023, 0.10),
        ]).summary()
        self.assertAlmostEqual(r.maximum_drawdown, 0.30)

    def test_downside_deviation(self):
        r = FundRiskAnalyzer([
            AnnualFundReturn(2021, 0.10),
            AnnualFundReturn(2022, -0.20),
            AnnualFundReturn(2023, -0.10),
        ]).summary()
        self.assertAlmostEqual(r.downside_deviation, ((0.04 + 0.01) / 3) ** 0.5)

    def test_empty_returns_rejected(self):
        with self.assertRaises(ValueError):
            FundRiskAnalyzer([])

if __name__ == "__main__":
    unittest.main()

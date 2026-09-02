import unittest

from planner.funds.portfolio_risk import PortfolioRiskAnalyzer


class PortfolioRiskAnalyzerTests(unittest.TestCase):
    def test_weighted_return(self):
        result = PortfolioRiskAnalyzer(
            {"a": 0.60, "b": 0.40},
            {"a": (0.10, 0.20), "b": (0.00, 0.10)},
        ).summary()
        self.assertAlmostEqual(result.weighted_average_return, 0.11)

    def test_portfolio_return_is_calculated_year_by_year(self):
        result = PortfolioRiskAnalyzer(
            {"a": 0.50, "b": 0.50},
            {"a": (0.20, -0.20), "b": (0.00, 0.00)},
        ).summary()
        self.assertAlmostEqual(result.weighted_average_return, 0.0)

    def test_portfolio_volatility(self):
        result = PortfolioRiskAnalyzer(
            {"a": 0.50, "b": 0.50},
            {"a": (0.10, 0.30), "b": (0.10, 0.30)},
        ).summary()
        self.assertAlmostEqual(result.portfolio_volatility, 0.1414213562373095)

    def test_negative_year_metrics(self):
        result = PortfolioRiskAnalyzer(
            {"a": 0.50, "b": 0.50},
            {"a": (0.10, -0.20, 0.05), "b": (0.00, -0.10, 0.10)},
        ).summary()
        self.assertEqual(result.negative_years, 1)
        self.assertAlmostEqual(result.negative_year_rate, 1 / 3)

    def test_maximum_drawdown(self):
        result = PortfolioRiskAnalyzer(
            {"a": 0.50, "b": 0.50},
            {"a": (0.20, -0.30), "b": (0.20, -0.30)},
        ).summary()
        self.assertAlmostEqual(result.maximum_drawdown, 0.30)

    def test_downside_deviation(self):
        result = PortfolioRiskAnalyzer(
            {"a": 0.50, "b": 0.50},
            {"a": (0.10, -0.20), "b": (0.10, -0.10)},
        ).summary()
        self.assertAlmostEqual(
            result.downside_deviation,
            ((0.0 + 0.15**2) / 2) ** 0.5,
        )

    def test_allocations_must_total_one(self):
        with self.assertRaises(ValueError):
            PortfolioRiskAnalyzer(
                {"a": 0.60, "b": 0.60},
                {"a": (0.10,), "b": (0.10,)},
            )

    def test_fund_histories_must_be_aligned(self):
        with self.assertRaises(ValueError):
            PortfolioRiskAnalyzer(
                {"a": 0.50, "b": 0.50},
                {"a": (0.10, 0.20), "b": (0.10,)},
            )

    def test_fund_sets_must_match(self):
        with self.assertRaises(ValueError):
            PortfolioRiskAnalyzer(
                {"a": 1.0},
                {"b": (0.10,)},
            )


if __name__ == "__main__":
    unittest.main()

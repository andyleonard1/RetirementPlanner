import unittest

from planner.funds.portfolio_historical_statistics import (
    PortfolioHistoricalStatisticsCalculator,
)


class PortfolioHistoricalStatisticsTests(unittest.TestCase):
    def setUp(self):
        self.calculator = PortfolioHistoricalStatisticsCalculator()
        self.allocations = {"Aviva": 0.75, "Sky": 0.25}

    def test_weighted_average_return(self):
        result = self.calculator.calculate(
            self.allocations, {"Aviva": [0.10] * 5, "Sky": [0.20] * 5}
        )
        self.assertAlmostEqual(result.weighted_average_return, 0.125)

    def test_cumulative_return_compounds_portfolio_returns(self):
        result = self.calculator.calculate(
            self.allocations, {"Aviva": [0.10, 0.10], "Sky": [0.20, 0.20]}
        )
        self.assertAlmostEqual(result.cumulative_return, 1.265625 - 1.0)

    def test_annualised_return_is_geometric(self):
        result = self.calculator.calculate(
            self.allocations, {"Aviva": [0.10, 0.10], "Sky": [0.20, 0.20]}
        )
        self.assertAlmostEqual(result.annualised_return, 0.125)

    def test_minimum_and_maximum_portfolio_years(self):
        result = self.calculator.calculate(
            self.allocations, {"Aviva": [-0.10, 0.10], "Sky": [0.20, -0.20]}
        )
        self.assertAlmostEqual(result.minimum_return, -0.025)
        self.assertAlmostEqual(result.maximum_return, 0.025)

    def test_volatility_uses_sample_standard_deviation(self):
        result = self.calculator.calculate(
            self.allocations, {"Aviva": [0.10, 0.12], "Sky": [0.20, 0.18]}
        )
        self.assertAlmostEqual(result.volatility, 0.007071067811865481)

    def test_volatility_is_none_with_one_year(self):
        result = self.calculator.calculate(
            self.allocations, {"Aviva": [0.10], "Sky": [0.20]}
        )
        self.assertIsNone(result.volatility)
        self.assertFalse(result.sufficient_for_volatility)

    def test_negative_years_and_rate_are_reported(self):
        result = self.calculator.calculate(
            self.allocations, {"Aviva": [-0.10, 0.10], "Sky": [-0.20, 0.20]}
        )
        self.assertEqual(result.negative_years, 1)
        self.assertAlmostEqual(result.negative_year_rate, 0.5)

    def test_allocations_are_preserved(self):
        result = self.calculator.calculate(
            self.allocations, {"Aviva": [0.10] * 2, "Sky": [0.20] * 2}
        )
        self.assertEqual(result.allocations, (("Aviva", 0.75), ("Sky", 0.25)))

    def test_empty_allocations_raise(self):
        with self.assertRaises(ValueError):
            self.calculator.calculate({}, {})

    def test_allocations_must_total_one(self):
        with self.assertRaises(ValueError):
            self.calculator.calculate(
                {"Aviva": 0.70, "Sky": 0.25},
                {"Aviva": [0.1], "Sky": [0.2]},
            )

    def test_negative_allocations_raise(self):
        with self.assertRaises(ValueError):
            self.calculator.calculate(
                {"Aviva": 1.10, "Sky": -0.10},
                {"Aviva": [0.1], "Sky": [0.2]},
            )

    def test_funds_must_match_allocations(self):
        with self.assertRaises(ValueError):
            self.calculator.calculate(
                self.allocations, {"Aviva": [0.1]}
            )

    def test_histories_must_have_equal_lengths(self):
        with self.assertRaises(ValueError):
            self.calculator.calculate(
                self.allocations, {"Aviva": [0.1, 0.2], "Sky": [0.2]}
            )

    def test_actual_and_estimated_counts_are_reported(self):
        result = self.calculator.calculate(
            self.allocations,
            {"Aviva": [0.10, 0.12], "Sky": [0.20, 0.18]},
            actual_observations={"Aviva": 2, "Sky": 1},
        )
        self.assertEqual(result.actual_observation_count, 3)
        self.assertEqual(result.estimated_observation_count, 1)

    def test_no_actual_observation_map_defaults_to_all_actual(self):
        result = self.calculator.calculate(
            self.allocations, {"Aviva": [0.10, 0.12], "Sky": [0.20, 0.18]}
        )
        self.assertEqual(result.actual_observation_count, 4)
        self.assertEqual(result.estimated_observation_count, 0)

    def test_observation_count_is_year_count(self):
        result = self.calculator.calculate(
            self.allocations, {"Aviva": [0.10] * 5, "Sky": [0.20] * 5}
        )
        self.assertEqual(result.observation_count, 5)


if __name__ == "__main__":
    unittest.main()

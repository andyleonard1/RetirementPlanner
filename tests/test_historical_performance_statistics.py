import unittest

from planner.funds.historical_fund_returns import HistoricalFundReturn
from planner.funds.historical_performance_statistics import (
    HistoricalPerformanceStatisticsCalculator,
)


class HistoricalPerformanceStatisticsTests(unittest.TestCase):
    def setUp(self):
        self.calculator = HistoricalPerformanceStatisticsCalculator()
        self.fund = "GB00BRDCMN86:GBP"

    def returns(self, *values, data_type="actual"):
        return tuple(
            HistoricalFundReturn(self.fund, 2020 + i, value, "test", data_type)
            for i, value in enumerate(values)
        )

    def test_empty_history_returns_no_statistics(self):
        result = self.calculator.calculate(self.fund, ())
        self.assertEqual(result.observation_count, 0)
        self.assertIsNone(result.cumulative_return)
        self.assertIsNone(result.annualised_return)
        self.assertIsNone(result.volatility)

    def test_single_return_has_cumulative_return(self):
        result = self.calculator.calculate(self.fund, self.returns(0.10))
        self.assertAlmostEqual(result.cumulative_return, 0.10)
        self.assertAlmostEqual(result.annualised_return, 0.10)

    def test_two_returns_calculate_cumulative_return(self):
        result = self.calculator.calculate(self.fund, self.returns(0.10, 0.20))
        self.assertAlmostEqual(result.cumulative_return, 0.32)

    def test_annualised_return_is_geometric(self):
        result = self.calculator.calculate(self.fund, self.returns(0.10, 0.20))
        self.assertAlmostEqual(result.annualised_return, (1.32 ** 0.5) - 1.0)

    def test_minimum_and_maximum_are_reported(self):
        result = self.calculator.calculate(
            self.fund, self.returns(-0.10, 0.05, 0.20)
        )
        self.assertAlmostEqual(result.minimum_return, -0.10)
        self.assertAlmostEqual(result.maximum_return, 0.20)

    def test_volatility_requires_two_observations(self):
        result = self.calculator.calculate(self.fund, self.returns(0.10))
        self.assertFalse(result.sufficient_for_volatility)
        self.assertIsNone(result.volatility)

    def test_volatility_uses_sample_standard_deviation(self):
        result = self.calculator.calculate(self.fund, self.returns(0.10, 0.20))
        self.assertAlmostEqual(result.volatility, 0.07071067811865477)

    def test_actual_and_estimated_counts_are_preserved(self):
        observations = (
            HistoricalFundReturn(self.fund, 2020, 0.10, "source", "actual"),
            HistoricalFundReturn(self.fund, 2021, 0.20, "source", "estimated"),
        )
        result = self.calculator.calculate(self.fund, observations)
        self.assertEqual(result.actual_observation_count, 1)
        self.assertEqual(result.estimated_observation_count, 1)

    def test_actual_only_excludes_estimates(self):
        observations = (
            HistoricalFundReturn(self.fund, 2020, 0.10, "source", "actual"),
            HistoricalFundReturn(self.fund, 2021, 0.20, "source", "estimated"),
        )
        result = self.calculator.calculate(
            self.fund, observations, actual_only=True
        )
        self.assertEqual(result.observation_count, 1)
        self.assertAlmostEqual(result.cumulative_return, 0.10)

    def test_observations_are_sorted_by_year(self):
        observations = (
            HistoricalFundReturn(self.fund, 2022, 0.20, "source"),
            HistoricalFundReturn(self.fund, 2020, 0.10, "source"),
        )
        result = self.calculator.calculate(self.fund, observations)
        self.assertEqual(
            [item.year for item in result.source_observations],
            [2020, 2022],
        )

    def test_other_funds_are_excluded(self):
        observations = self.returns(0.10) + (
            HistoricalFundReturn("OTHER", 2020, 0.50, "source"),
        )
        result = self.calculator.calculate(self.fund, observations)
        self.assertEqual(result.observation_count, 1)
        self.assertAlmostEqual(result.cumulative_return, 0.10)

    def test_provenance_is_preserved(self):
        observation = HistoricalFundReturn(
            self.fund, 2020, 0.10, "Financial Times / Aviva"
        )
        result = self.calculator.calculate(self.fund, (observation,))
        self.assertEqual(result.source_observations[0].source, observation.source)

    def test_negative_and_positive_returns_compound(self):
        result = self.calculator.calculate(self.fund, self.returns(-0.20, 0.25))
        self.assertAlmostEqual(result.cumulative_return, 0.0)

    def test_statistics_do_not_fabricate_volatility(self):
        result = self.calculator.calculate(self.fund, ())
        self.assertFalse(result.sufficient_for_volatility)
        self.assertIsNone(result.volatility)


if __name__ == "__main__":
    unittest.main()

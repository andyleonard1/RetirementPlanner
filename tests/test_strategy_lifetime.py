import unittest

from planner.simulation.strategy_lifetime import LifetimeStrategyAggregator
from planner.simulation.withdrawal_strategy_comparison import StrategyOutcome


class LifetimeStrategyAggregatorTests(unittest.TestCase):
    def setUp(self):
        self.aggregator = LifetimeStrategyAggregator()

    def test_aggregates_tax_across_years(self):
        result = self.aggregator.aggregate(
            "tax_free",
            [
                StrategyOutcome("tax_free", 30000, 3000, 2000, 29000),
                StrategyOutcome("tax_free", 31000, 3200, 1500, 29300),
            ],
        )
        self.assertEqual(result.total_tax, 6200)

    def test_aggregates_net_income(self):
        result = self.aggregator.aggregate(
            "standard",
            [
                StrategyOutcome("standard", 35000, 5000, 0, 30000),
                StrategyOutcome("standard", 35000, 5100, 0, 29900),
            ],
        )
        self.assertEqual(result.total_net_income, 59900)

    def test_aggregates_tax_free_cash(self):
        result = self.aggregator.aggregate(
            "phased",
            [
                StrategyOutcome("phased", 32000, 3500, 3000, 31500),
                StrategyOutcome("phased", 32000, 3400, 2000, 30600),
            ],
        )
        self.assertEqual(result.total_tax_free_cash, 5000)

    def test_records_year_count(self):
        result = self.aggregator.aggregate(
            "standard",
            [StrategyOutcome("standard", 35000, 5000, 0, 30000)],
        )
        self.assertEqual(result.years, 1)

    def test_empty_sequence_is_rejected(self):
        with self.assertRaises(ValueError):
            self.aggregator.aggregate("empty", [])


if __name__ == "__main__":
    unittest.main()

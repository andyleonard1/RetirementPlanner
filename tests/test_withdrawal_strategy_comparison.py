import unittest

from planner.simulation.withdrawal_strategy_comparison import (
    StrategyOutcome,
    WithdrawalStrategyComparator,
)


class WithdrawalStrategyComparatorTests(unittest.TestCase):
    def setUp(self):
        self.comparator = WithdrawalStrategyComparator()

    def test_identifies_lowest_tax_strategy(self):
        result = self.comparator.compare([
            StrategyOutcome("standard", 35000, 5000, 0, 30000),
            StrategyOutcome("tax_free", 30000, 3000, 5000, 32000),
        ])
        self.assertEqual(result.lowest_tax_strategy, "tax_free")

    def test_identifies_highest_net_income_strategy(self):
        result = self.comparator.compare([
            StrategyOutcome("standard", 35000, 5000, 0, 30000),
            StrategyOutcome("tax_free", 30000, 3000, 5000, 32000),
        ])
        self.assertEqual(result.highest_net_income_strategy, "tax_free")

    def test_reports_tax_saving(self):
        result = self.comparator.compare([
            StrategyOutcome("standard", 35000, 5000, 0, 30000),
            StrategyOutcome("tax_free", 30000, 3000, 5000, 32000),
        ])
        self.assertEqual(result.tax_saving_vs_highest_tax, 2000)

    def test_preserves_all_strategy_results(self):
        outcomes = [
            StrategyOutcome("a", 30000, 4000, 1000, 27000),
            StrategyOutcome("b", 32000, 3500, 2000, 30500),
        ]
        result = self.comparator.compare(outcomes)
        self.assertEqual(result.strategies, tuple(outcomes))

    def test_empty_input_is_rejected(self):
        with self.assertRaises(ValueError):
            self.comparator.compare([])

    def test_negative_tax_is_rejected(self):
        with self.assertRaises(ValueError):
            self.comparator.compare([
                StrategyOutcome("bad", 30000, -1, 0, 30000)
            ])

    def test_negative_pension_is_rejected(self):
        with self.assertRaises(ValueError):
            self.comparator.compare([
                StrategyOutcome("bad", -1, 0, 0, 0)
            ])


if __name__ == "__main__":
    unittest.main()

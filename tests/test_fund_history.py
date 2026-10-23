import unittest

from planner.funds.fund_history import AnnualFundReturn, FundHistory


class FundHistoryTests(unittest.TestCase):
    def test_summary_counts_years(self):
        history = FundHistory([
            AnnualFundReturn(2021, 0.10),
            AnnualFundReturn(2022, -0.05),
        ])
        self.assertEqual(history.summary().years, 2)

    def test_arithmetic_mean_is_calculated(self):
        history = FundHistory([
            AnnualFundReturn(2021, 0.10),
            AnnualFundReturn(2022, 0.20),
        ])
        self.assertAlmostEqual(history.summary().arithmetic_mean, 0.15)

    def test_annualised_return_is_compounded(self):
        history = FundHistory([
            AnnualFundReturn(2021, 0.10),
            AnnualFundReturn(2022, 0.10),
        ])
        self.assertAlmostEqual(
            history.summary().annualised_return,
            0.10,
        )

    def test_best_and_worst_returns(self):
        history = FundHistory([
            AnnualFundReturn(2021, 0.15),
            AnnualFundReturn(2022, -0.20),
            AnnualFundReturn(2023, 0.05),
        ])
        summary = history.summary()
        self.assertEqual(summary.best_return, 0.15)
        self.assertEqual(summary.worst_return, -0.20)

    def test_empty_history_is_rejected(self):
        with self.assertRaises(ValueError):
            FundHistory([])

    def test_duplicate_years_are_rejected(self):
        with self.assertRaises(ValueError):
            FundHistory([
                AnnualFundReturn(2022, 0.10),
                AnnualFundReturn(2022, 0.20),
            ])


if __name__ == "__main__":
    unittest.main()

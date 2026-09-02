import unittest

from planner.simulation.tax_free_cash import (
    TaxFreeCashConfig,
    TaxFreeCashStrategy,
)


class TaxFreeCashStrategyTests(unittest.TestCase):
    def test_uses_available_tax_free_cash(self):
        strategy = TaxFreeCashStrategy(
            TaxFreeCashConfig(allowance=10000, annual_tax_free_cash=3000)
        )
        plan = strategy.plan_year(
            target_net_income=35000,
            taxable_pension_required=34000,
            tax_paid=4000,
        )
        self.assertEqual(plan.tax_free_cash, 3000)
        self.assertEqual(plan.remaining_allowance, 7000)

    def test_cannot_use_more_than_remaining_allowance(self):
        strategy = TaxFreeCashStrategy(
            TaxFreeCashConfig(allowance=2000, annual_tax_free_cash=5000)
        )
        plan = strategy.plan_year(35000, 34000, 4000)
        self.assertEqual(plan.tax_free_cash, 2000)
        self.assertEqual(plan.remaining_allowance, 0)

    def test_can_disable_tax_free_cash(self):
        strategy = TaxFreeCashStrategy(
            TaxFreeCashConfig(allowance=10000, annual_tax_free_cash=3000)
        )
        plan = strategy.plan_year(
            35000, 34000, 4000, use_tax_free_cash=False
        )
        self.assertEqual(plan.tax_free_cash, 0)
        self.assertEqual(plan.remaining_allowance, 10000)

    def test_tax_free_cash_is_not_taxed(self):
        strategy = TaxFreeCashStrategy(
            TaxFreeCashConfig(allowance=5000, annual_tax_free_cash=5000)
        )
        plan = strategy.plan_year(35000, 30000, 5000)
        self.assertEqual(plan.tax_free_cash, 5000)
        self.assertEqual(plan.tax_paid, 5000)

    def test_invalid_allowance_is_rejected(self):
        with self.assertRaises(ValueError):
            TaxFreeCashStrategy(TaxFreeCashConfig(allowance=-1))

    def test_invalid_annual_amount_is_rejected(self):
        with self.assertRaises(ValueError):
            TaxFreeCashStrategy(
                TaxFreeCashConfig(allowance=1000, annual_tax_free_cash=-1)
            )

    def test_negative_tax_is_rejected(self):
        strategy = TaxFreeCashStrategy(TaxFreeCashConfig(allowance=1000))
        with self.assertRaises(ValueError):
            strategy.plan_year(35000, 30000, -1)


if __name__ == "__main__":
    unittest.main()

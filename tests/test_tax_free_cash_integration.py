import unittest

from planner.simulation.tax_free_cash import (
    TaxFreeCashConfig,
    TaxFreeCashStrategy,
)
from planner.simulation.tax_free_cash_integration import (
    TaxFreeCashIntegration,
)


class TaxFreeCashIntegrationTests(unittest.TestCase):
    def setUp(self):
        strategy = TaxFreeCashStrategy(
            TaxFreeCashConfig(
                allowance=10000.0,
                annual_tax_free_cash=2500.0,
            )
        )
        self.integration = TaxFreeCashIntegration(strategy)

    def test_adapter_returns_strategy_plan(self):
        result = self.integration.apply(
            35000.0,
            30000.0,
            4000.0,
        )
        self.assertEqual(result.plan.tax_free_cash, 2500.0)
        self.assertEqual(result.plan.remaining_allowance, 7500.0)

    def test_adapter_preserves_taxable_pension_amount(self):
        result = self.integration.apply(
            35000.0,
            30000.0,
            4000.0,
        )
        self.assertEqual(
            result.taxable_income_before_tax_free_cash,
            30000.0,
        )

    def test_adapter_can_disable_tax_free_cash(self):
        result = self.integration.apply(
            35000.0,
            30000.0,
            4000.0,
            use_tax_free_cash=False,
        )
        self.assertEqual(result.plan.tax_free_cash, 0.0)
        self.assertEqual(result.plan.remaining_allowance, 10000.0)

    def test_adapter_consumes_allowance_progressively(self):
        first = self.integration.apply(35000.0, 30000.0, 4000.0)
        self.assertEqual(first.plan.remaining_allowance, 7500.0)

        second_strategy = TaxFreeCashStrategy(
            TaxFreeCashConfig(
                allowance=first.plan.remaining_allowance,
                annual_tax_free_cash=2500.0,
            )
        )
        second = TaxFreeCashIntegration(second_strategy).apply(
            35000.0,
            30000.0,
            4000.0,
        )
        self.assertEqual(second.plan.tax_free_cash, 2500.0)
        self.assertEqual(second.plan.remaining_allowance, 5000.0)


if __name__ == "__main__":
    unittest.main()

"""Sprint 280 regression tests for pension funding and State Pension forecasts."""

import unittest

from planner.assumptions import Assumptions
from planner.cashflow_engine import CashFlowEngine
from planner.models import RetirementYear
from planner.state_pension import StatePensionEngine


class Sprint280PensionFundingForecastIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.assumptions = Assumptions()
        values = {
            "state_pension_full": 10_000.0,
            "state_pension_growth": 0.035,
            "state_pension_earnings_growth": 0.03,
            "inflation_rate": 0.025,
            "state_pension_triple_lock_enabled": True,
            "state_pension_earnings_growth_schedule_enabled": False,
            "state_pension_earnings_growth_schedule": {},
            "phase_1_end_age": 90,
            "phase_2_end_age": 100,
            "spending_phase_1": 30_000.0,
            "spending_phase_2": 30_000.0,
            "spending_phase_3": 30_000.0,
            "inflation_link_spending": True,
        }
        for key, value in values.items():
            self.assumptions.set(key, value)

    @staticmethod
    def year(age, calendar_year, inflation_rate, inflation_factor=1.0):
        return RetirementYear(
            age=age,
            calendar_year=calendar_year,
            spouse_age=age - 2,
            inflation_rate=inflation_rate,
            inflation_factor=inflation_factor,
        )

    def test_projected_year_cpi_drives_triple_lock_instead_of_static_base_cpi(self):
        self.assumptions.set("inflation_rate", 0.02)
        year = self.year(68, 2030, inflation_rate=0.06)

        StatePensionEngine(self.assumptions).apply([year])

        self.assertEqual(year.your_state_pension, 10_600.00)

    def test_year_specific_cpi_and_earnings_schedule_compound_year_by_year(self):
        self.assumptions.set("state_pension_earnings_growth_schedule_enabled", True)
        self.assumptions.set("state_pension_earnings_growth_schedule", {"2031": 0.07})
        years = [
            self.year(68, 2030, inflation_rate=0.06),
            self.year(69, 2031, inflation_rate=0.02),
        ]

        StatePensionEngine(self.assumptions).apply(years)

        self.assertEqual(years[0].your_state_pension, 10_600.00)
        # 2030 uses 6% CPI; 2031 uses the scheduled 7% earnings rate.
        self.assertEqual(years[1].your_state_pension, 11_342.00)
        self.assertEqual(years[1].spouse_state_pension, 11_342.00)

    def test_triple_lock_disabled_uses_legacy_growth_despite_high_projected_inflation(self):
        self.assumptions.set("state_pension_triple_lock_enabled", False)
        year = self.year(68, 2030, inflation_rate=0.08)

        StatePensionEngine(self.assumptions).apply([year])

        self.assertEqual(year.your_state_pension, 10_350.00)

    def test_inflated_spending_less_state_pension_sets_required_pension_income(self):
        year = self.year(68, 2030, inflation_rate=0.04, inflation_factor=1.04)
        year.savings_interest = 500.0
        StatePensionEngine(self.assumptions).apply([year])

        CashFlowEngine(self.assumptions).apply([year])

        self.assertEqual(year.target_spending, 31_200.00)
        self.assertEqual(year.your_state_pension, 10_400.00)
        self.assertEqual(year.cash_available, 10_900.00)
        self.assertEqual(year.required_pension_income, 20_300.00)

    def test_cash_income_above_inflated_spending_does_not_require_negative_pension_income(self):
        year = self.year(68, 2030, inflation_rate=0.025, inflation_factor=1.0)
        year.savings_interest = 1_000.0
        year.your_state_pension = 35_000.0

        CashFlowEngine(self.assumptions).apply([year])

        self.assertEqual(year.required_pension_income, 0)


if __name__ == "__main__":
    unittest.main()

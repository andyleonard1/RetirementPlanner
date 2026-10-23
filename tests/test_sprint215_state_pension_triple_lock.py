import unittest

from planner.assumptions import Assumptions
from planner.models import RetirementYear
from planner.state_pension import StatePensionEngine
from planner.cashflow_engine import CashFlowEngine


class TestSprint215StatePensionTripleLock(unittest.TestCase):

    def setUp(self):
        self.assumptions = Assumptions()
        self.assumptions.set("state_pension_full", 10000.0)
        self.assumptions.set("state_pension_growth", 0.035)
        self.assumptions.set("state_pension_earnings_growth", 0.03)
        self.assumptions.set("inflation_rate", 0.025)
        self.assumptions.set("state_pension_triple_lock_enabled", True)

    def make_year(self, age, year=2030):
        return RetirementYear(age=age, calendar_year=year, spouse_age=age - 2)

    def test_uses_highest_of_earnings_cpi_and_floor(self):
        self.assumptions.set("state_pension_earnings_growth", 0.04)
        self.assumptions.set("inflation_rate", 0.02)
        year = self.make_year(68)
        StatePensionEngine(self.assumptions).apply([year])
        self.assertEqual(year.your_state_pension, 10400.00)

    def test_cpi_can_drive_triple_lock(self):
        self.assumptions.set("state_pension_earnings_growth", 0.02)
        self.assumptions.set("inflation_rate", 0.04)
        year = self.make_year(68)
        StatePensionEngine(self.assumptions).apply([year])
        self.assertEqual(year.your_state_pension, 10400.00)

    def test_two_point_five_percent_floor_can_drive_triple_lock(self):
        self.assumptions.set("state_pension_earnings_growth", 0.01)
        self.assumptions.set("inflation_rate", 0.015)
        year = self.make_year(68)
        StatePensionEngine(self.assumptions).apply([year])
        self.assertEqual(year.your_state_pension, 10250.00)

    def test_disabled_mode_retains_legacy_growth(self):
        self.assumptions.set("state_pension_growth", 0.035)
        self.assumptions.set("state_pension_earnings_growth", 0.05)
        self.assumptions.set("inflation_rate", 0.06)
        self.assumptions.set("state_pension_triple_lock_enabled", False)
        year = self.make_year(68)
        StatePensionEngine(self.assumptions).apply([year])
        self.assertEqual(year.your_state_pension, 10350.00)

    def test_spouse_uses_same_annual_triple_lock(self):
        self.assumptions.set("state_pension_earnings_growth", 0.04)
        self.assumptions.set("inflation_rate", 0.025)
        year = self.make_year(69)
        StatePensionEngine(self.assumptions).apply([year])
        self.assertEqual(year.spouse_state_pension, 10816.00)

    def test_required_pension_income_reflects_inflated_spending_and_state_pension(self):
        self.assumptions.set("phase_1_end_age", 90)
        self.assumptions.set("phase_2_end_age", 100)
        self.assumptions.set("spending_phase_1", 30000.0)
        self.assumptions.set("spending_phase_2", 30000.0)
        self.assumptions.set("spending_phase_3", 30000.0)
        self.assumptions.set("inflation_link_spending", True)
        self.assumptions.set("state_pension_full", 10000.0)
        self.assumptions.set("state_pension_earnings_growth", 0.04)
        self.assumptions.set("inflation_rate", 0.03)
        self.assumptions.set("state_pension_triple_lock_enabled", True)

        year = self.make_year(68)
        year.inflation_factor = 1.03
        StatePensionEngine(self.assumptions).apply([year])
        year.savings_interest = 0.0
        CashFlowEngine(self.assumptions).apply([year])

        self.assertEqual(year.target_spending, 30900.00)
        self.assertEqual(year.your_state_pension, 10400.00)
        self.assertEqual(year.required_pension_income, 20500.00)


if __name__ == "__main__":
    unittest.main()

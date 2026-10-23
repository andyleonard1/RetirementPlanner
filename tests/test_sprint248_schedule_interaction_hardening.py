import unittest

from planner.assumptions import Assumptions
from planner.models import RetirementYear
from planner.planner import RetirementPlanner
from planner.property_sale_engine import PropertySaleEngine
from planner.state_pension import StatePensionEngine
from planner.cashflow_engine import CashFlowEngine


class Sprint248ScheduleInteractionHardeningTests(unittest.TestCase):
    """Protect precedence and downstream flow when multiple schedules coexist."""

    def setUp(self):
        self.assumptions = Assumptions()
        values = {
            "current_age": 65,
            "retirement_age": 65,
            "projection_end_age": 70,
            "spouse_current_age": 62,
            "current_calendar_year": 2026,
            "starting_pension": 200000.0,
            "starting_savings": 50000.0,
            "starting_isa": 40000.0,
            "expected_investment_return": 0.04,
            "platform_charge": 0.01,
            "fund_charge": 0.005,
            "savings_interest_rate": 0.03,
            "isa_growth_rate": 0.04,
            "inflation": 0.025,
            "inflation_link_spending": True,
            "inflation_link_tax": True,
            "inflation_link_isa": True,
            "state_pension_full": 10000.0,
            "state_pension_growth": 0.03,
            "state_pension_earnings_growth": 0.03,
            "state_pension_triple_lock_enabled": True,
            "property_sale": 100000.0,
            "property_sale_age": 67,
            "annual_isa_allowance": 20000.0,
            "withdrawal_strategy": "PENSION_FIRST",
            "max_pension_income": 30000.0,
            "spending_phase_1": 20000.0,
            "spending_phase_2": 18000.0,
            "spending_phase_3": 16000.0,
            "phase_1_end_age": 67,
            "phase_2_end_age": 69,
        }
        for key, value in values.items():
            self.assumptions[key] = value

    def execute_projection(self):
        return RetirementPlanner(self.assumptions).run()

    def test_all_schedules_can_target_one_calendar_year_without_cross_over(self):
        self.assumptions["annual_spending_schedule_enabled"] = True
        self.assumptions["annual_spending_schedule"] = {"2028": 25000.0}
        self.assumptions["investment_return_schedule_enabled"] = True
        self.assumptions["investment_return_schedule"] = {"2028": 0.10}
        self.assumptions["isa_return_schedule_enabled"] = True
        self.assumptions["isa_return_schedule"] = {"2028": 0.08}
        self.assumptions["state_pension_earnings_growth_schedule_enabled"] = True
        self.assumptions["state_pension_earnings_growth_schedule"] = {"2028": 0.06}
        self.assumptions["isa_allowance_schedule_enabled"] = True
        self.assumptions["isa_allowance_schedule"] = {"2028/29": 30000.0}

        result = self.execute_projection()
        year = next(y for y in result.timeline if y.calendar_year == 2028)

        self.assertAlmostEqual(year.target_spending, 25000.0 * 1.025**2, places=2)
        self.assertAlmostEqual(year.pension_growth, year.opening_pension * (0.10 - 0.015), delta=0.01)
        self.assertAlmostEqual(year.isa_growth_rate, 0.08)
        self.assertAlmostEqual(year.isa_growth, year.isa_opening * 0.08, places=2)
        self.assertAlmostEqual(year.property_sale_to_isa, 30000.0 * year.inflation_factor, places=2)
        self.assertAlmostEqual(year.property_sale_to_savings, 100000.0 - year.property_sale_to_isa, places=2)

        # Age 67 is the first payable year, so its opening State Pension
        # does not compound the same year; the scheduled 2028 rate affects
        # subsequent accumulation (covered separately below).
        self.assertEqual(year.your_state_pension, 10000.0)

    def test_investment_schedule_is_gross_before_platform_and_fund_charges(self):
        self.assumptions["investment_return_schedule_enabled"] = True
        self.assumptions["investment_return_schedule"] = {"2027": 0.10}
        result = self.execute_projection()
        year = next(y for y in result.timeline if y.calendar_year == 2027)
        self.assertAlmostEqual(year.pension_growth, year.opening_pension * 0.085, delta=0.01)

    def test_isa_return_schedule_applies_to_opening_balance_before_same_year_contribution(self):
        self.assumptions["isa_return_schedule_enabled"] = True
        self.assumptions["isa_return_schedule"] = {"2028": 0.08}
        self.assumptions["isa_allowance_schedule_enabled"] = True
        self.assumptions["isa_allowance_schedule"] = {"2028/29": 30000.0}
        result = self.execute_projection()
        year = next(y for y in result.timeline if y.calendar_year == 2028)
        self.assertAlmostEqual(year.isa_growth, year.isa_opening * 0.08, places=2)
        self.assertEqual(year.isa_contribution, year.property_sale_to_isa)
        self.assertAlmostEqual(year.isa_closing, year.isa_opening + year.isa_growth + year.isa_contribution - year.isa_withdrawal, places=2)

    def test_isa_allowance_schedule_is_selected_by_tax_year_then_inflation_link_applies(self):
        self.assumptions["isa_allowance_schedule_enabled"] = True
        self.assumptions["isa_allowance_schedule"] = {
            "2026/27": 20000.0,
            "2028/29": 30000.0,
            "2030/31": 40000.0,
        }
        result = self.execute_projection()
        year = next(y for y in result.timeline if y.calendar_year == 2028)
        self.assertAlmostEqual(year.property_sale_to_isa, 30000.0 * year.inflation_factor, places=2)

    def test_state_pension_schedule_competes_with_cpi_inside_triple_lock(self):
        self.assumptions["state_pension_earnings_growth_schedule_enabled"] = True
        self.assumptions["state_pension_earnings_growth_schedule"] = {"2029": 0.02}
        result = self.execute_projection()
        year = next(y for y in result.timeline if y.calendar_year == 2029)
        self.assertAlmostEqual(year.your_state_pension, 10000.0 * 1.025, places=2)

    def test_annual_spending_schedule_remains_nominal_before_shared_inflation_factor(self):
        self.assumptions["annual_spending_schedule_enabled"] = True
        self.assumptions["annual_spending_schedule"] = {"2028": 25000.0}
        result = self.execute_projection()
        year = next(y for y in result.timeline if y.calendar_year == 2028)
        self.assertAlmostEqual(year.target_spending, 25000.0 * year.inflation_factor, places=2)

    def test_missing_entries_fall_back_independently_to_each_base_assumption(self):
        self.assumptions["annual_spending_schedule_enabled"] = True
        self.assumptions["annual_spending_schedule"] = {"2027": 24000.0}
        self.assumptions["investment_return_schedule_enabled"] = True
        self.assumptions["investment_return_schedule"] = {"2028": 0.10}
        self.assumptions["isa_return_schedule_enabled"] = True
        self.assumptions["isa_return_schedule"] = {"2029": 0.08}
        self.assumptions["state_pension_earnings_growth_schedule_enabled"] = True
        self.assumptions["state_pension_earnings_growth_schedule"] = {"2030": 0.06}
        self.assumptions["isa_allowance_schedule_enabled"] = True
        self.assumptions["isa_allowance_schedule"] = {"2030/31": 40000.0}

        result = self.execute_projection()
        y27 = next(y for y in result.timeline if y.calendar_year == 2027)
        y28 = next(y for y in result.timeline if y.calendar_year == 2028)
        self.assertAlmostEqual(y27.target_spending, 24000.0 * y27.inflation_factor, places=2)
        self.assertAlmostEqual(y28.pension_growth, y28.opening_pension * (0.10 - 0.015), places=2)
        self.assertAlmostEqual(y28.isa_growth_rate, 0.04)

    def test_disabling_one_schedule_does_not_disable_other_schedules(self):
        self.assumptions["annual_spending_schedule_enabled"] = False
        self.assumptions["annual_spending_schedule"] = {"2028": 25000.0}
        self.assumptions["investment_return_schedule_enabled"] = True
        self.assumptions["investment_return_schedule"] = {"2028": 0.10}
        self.assumptions["isa_return_schedule_enabled"] = True
        self.assumptions["isa_return_schedule"] = {"2028": 0.08}
        result = self.execute_projection()
        year = next(y for y in result.timeline if y.calendar_year == 2028)
        self.assertAlmostEqual(year.target_spending, 20000.0 * year.inflation_factor, places=2)
        self.assertAlmostEqual(year.pension_growth, year.opening_pension * 0.085, delta=0.01)
        self.assertAlmostEqual(year.isa_growth_rate, 0.08)

    def test_property_sale_allocation_respects_scheduled_allowance_and_preserves_total_proceeds(self):
        self.assumptions["isa_allowance_schedule_enabled"] = True
        self.assumptions["isa_allowance_schedule"] = {"2028/29": 25000.0}
        result = self.execute_projection()
        year = next(y for y in result.timeline if y.calendar_year == 2028)
        self.assertAlmostEqual(year.property_sale_to_isa + year.property_sale_to_savings, 100000.0, places=2)
        self.assertLessEqual(year.property_sale_to_isa, 25000.0 * year.inflation_factor + 0.01)

    def test_combined_schedules_are_deterministic_across_repeated_runs(self):
        self.assumptions["annual_spending_schedule_enabled"] = True
        self.assumptions["annual_spending_schedule"] = {"2028": 25000.0, "2029": 23000.0}
        self.assumptions["investment_return_schedule_enabled"] = True
        self.assumptions["investment_return_schedule"] = {"2028": 0.10, "2029": 0.02}
        self.assumptions["isa_return_schedule_enabled"] = True
        self.assumptions["isa_return_schedule"] = {"2028": 0.08, "2029": 0.03}
        self.assumptions["state_pension_earnings_growth_schedule_enabled"] = True
        self.assumptions["state_pension_earnings_growth_schedule"] = {"2028": 0.06}
        self.assumptions["isa_allowance_schedule_enabled"] = True
        self.assumptions["isa_allowance_schedule"] = {"2028/29": 30000.0}

        first = self.execute_projection()
        second = self.execute_projection()
        self.assertEqual(first.summary, second.summary)
        self.assertEqual(
            [(y.calendar_year, y.target_spending, y.pension_growth, y.isa_closing) for y in first.timeline],
            [(y.calendar_year, y.target_spending, y.pension_growth, y.isa_closing) for y in second.timeline],
        )

    def test_direct_state_pension_schedule_still_uses_calendar_year(self):
        self.assumptions["state_pension_earnings_growth_schedule_enabled"] = True
        self.assumptions["state_pension_earnings_growth_schedule"] = {"2030": 0.05}
        year = RetirementYear(age=68, calendar_year=2030, spouse_age=65)
        StatePensionEngine(self.assumptions).apply([year])
        self.assertEqual(year.your_state_pension, 10500.0)


if __name__ == "__main__":
    unittest.main()

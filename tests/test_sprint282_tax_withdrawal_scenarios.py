"""Sprint 282: end-to-end tax and withdrawal scenario contracts.

These tests protect the current engine integration; they do not assert that
any withdrawal strategy is universally optimal or model tax advice.
"""
from __future__ import annotations

import math
import unittest

from planner.assumptions import Assumptions
from planner.planner import RetirementPlanner


class Sprint282TaxWithdrawalScenarioTests(unittest.TestCase):
    def make_assumptions(self, **changes):
        assumptions = Assumptions()
        values = {
            "current_age": 65,
            "retirement_age": 65,
            "projection_end_age": 72,
            "spouse_current_age": 62,
            "current_calendar_year": 2026,
            "starting_pension": 240000.0,
            "starting_savings": 30000.0,
            "starting_isa": 60000.0,
            "expected_investment_return": 0.03,
            "platform_charge": 0.0,
            "fund_charge": 0.0,
            "savings_interest_rate": 0.02,
            "isa_growth_rate": 0.03,
            "inflation": 0.025,
            "inflation_link_spending": True,
            "inflation_link_tax": True,
            "inflation_link_isa": False,
            "state_pension_full": 12548.0,
            "state_pension_growth": 0.025,
            "state_pension_earnings_growth": 0.03,
            "state_pension_triple_lock_enabled": True,
            "property_sale": 0.0,
            "property_sale_age": 67,
            "annual_isa_allowance": 20000.0,
            "withdrawal_strategy": "PENSION_FIRST",
            "max_pension_income": 30000.0,
            "spending_phase_1": 38000.0,
            "spending_phase_2": 34000.0,
            "spending_phase_3": 30000.0,
            "phase_1_end_age": 67,
            "phase_2_end_age": 69,
        }
        values.update(changes)
        for key, value in values.items():
            assumptions.set(key, value)
        return assumptions

    def run_scenario(self, **changes):
        return RetirementPlanner(self.make_assumptions(**changes), audit_context="sprint282").run()

    def test_gross_pension_withdrawal_covers_net_pension_need_and_tax(self):
        result = self.run_scenario()
        for row in result.timeline:
            self.assertAlmostEqual(
                row.gross_pension_income - row.income_tax,
                row.net_pension_income,
                delta=0.03,
                msg=f"year {row.calendar_year}",
            )

    def test_final_pension_withdrawal_matches_tax_engine_gross_amount(self):
        result = self.run_scenario()
        for row in result.timeline:
            self.assertAlmostEqual(row.pension_withdrawal, row.gross_pension_income, places=2)

    def test_isa_first_and_pension_first_are_distinct_when_isa_is_available(self):
        pension_first = self.run_scenario(withdrawal_strategy="PENSION_FIRST")
        isa_first = self.run_scenario(withdrawal_strategy="ISA_FIRST")
        self.assertEqual(len(pension_first.timeline), len(isa_first.timeline))
        self.assertTrue(any(
            abs(a.isa_used - b.isa_used) > 0.01
            or abs(a.pension_needed - b.pension_needed) > 0.01
            for a, b in zip(pension_first.timeline, isa_first.timeline)
        ))

    def test_annual_pension_income_cap_is_respected_by_strategy_layer(self):
        cap = 18000.0
        result = self.run_scenario(max_pension_income=cap)
        for row in result.timeline:
            self.assertLessEqual(row.pension_needed, cap + 0.01)

    def test_disabling_tax_free_cash_removes_tax_free_withdrawals(self):
        result = self.run_scenario(use_tax_free_cash=False)
        for row in result.timeline:
            self.assertAlmostEqual(row.tax_free_cash_used, 0.0, places=2)
            self.assertAlmostEqual(row.taxable_pension_withdrawal, row.pension_withdrawal, places=2)

    def test_tax_free_cash_used_never_exceeds_original_lifetime_allowance(self):
        start = 240000.0
        percentage = 0.25
        result = self.run_scenario(starting_pension=start, tax_free_pension_percentage=percentage)
        used = sum(row.tax_free_cash_used for row in result.timeline)
        self.assertLessEqual(used, start * percentage + 0.02)
        self.assertAlmostEqual(result.timeline[-1].remaining_tax_free_cash, max(0.0, start * percentage - used), places=2)

    def test_exhausted_assets_and_zero_state_pension_surface_shortfall(self):
        result = self.run_scenario(
            starting_pension=0.0,
            starting_savings=0.0,
            starting_isa=0.0,
            state_pension_full=0.0,
            max_pension_income=0.0,
            spending_phase_1=20000.0,
            spending_phase_2=20000.0,
            spending_phase_3=20000.0,
        )
        first = result.timeline[0]
        self.assertGreater(first.income_shortfall, 0.0)
        self.assertEqual(first.gross_pension_income, 0.0)
        self.assertEqual(first.income_tax, 0.0)

    def test_tax_summary_is_aggregated_from_the_final_timeline(self):
        result = self.run_scenario()
        self.assertAlmostEqual(result.summary["total_tax"], sum(row.income_tax for row in result.timeline), places=2)
        self.assertAlmostEqual(result.summary["gross_pension"], sum(row.gross_pension_income for row in result.timeline), places=2)
        self.assertEqual(result.summary["ending_pension"], result.timeline[-1].closing_pension)

    def test_tax_and_withdrawal_outputs_remain_finite(self):
        result = self.run_scenario()
        fields = ("pension_needed", "pension_withdrawal", "gross_pension_income", "tax_free_cash_used", "taxable_pension_withdrawal", "income_tax", "closing_pension", "isa_closing", "savings_closing", "income_shortfall")
        for row in result.timeline:
            for field in fields:
                self.assertTrue(math.isfinite(float(getattr(row, field))), f"{field} at {row.calendar_year}")


if __name__ == "__main__":
    unittest.main()

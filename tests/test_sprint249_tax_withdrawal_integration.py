import unittest

from planner.assumptions import Assumptions
from planner.models import RetirementYear
from planner.planner import RetirementPlanner
from planner.strategy_engine import StrategyEngine
from planner.withdrawal_engine import WithdrawalEngine


class Sprint249TaxWithdrawalIntegrationTests(unittest.TestCase):
    """Protect the strategy -> withdrawal -> tax -> pension integration contract."""

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
            "platform_charge": 0.0,
            "fund_charge": 0.0,
            "savings_interest_rate": 0.03,
            "isa_growth_rate": 0.04,
            "inflation": 0.025,
            "inflation_link_spending": True,
            "inflation_link_tax": True,
            "inflation_link_isa": True,
            "state_pension_full": 12548.0,
            "state_pension_growth": 0.03,
            "state_pension_earnings_growth": 0.03,
            "state_pension_triple_lock_enabled": True,
            "property_sale": 100000.0,
            "property_sale_age": 67,
            "annual_isa_allowance": 20000.0,
            "withdrawal_strategy": "PENSION_FIRST",
            "max_pension_income": 30000.0,
            "spending_phase_1": 35000.0,
            "spending_phase_2": 32000.0,
            "spending_phase_3": 28000.0,
            "phase_1_end_age": 67,
            "phase_2_end_age": 69,
        }
        for key, value in values.items():
            self.assumptions.set(key, value)

    def execute_projection(self):
        return RetirementPlanner(self.assumptions, audit_context="sprint249").run()

    def test_strategy_cap_routes_excess_need_to_isa_before_tax(self):
        timeline = [RetirementYear(age=65, calendar_year=2026, spouse_age=62)]
        year = timeline[0]
        year.target_spending = 40000.0
        year.cash_available = 0.0
        year.maximum_tax_efficient_pension = 50000.0
        year.isa_closing = 20000.0

        StrategyEngine(self.assumptions).apply(timeline)

        self.assertEqual(year.pension_needed, 30000.0)
        self.assertEqual(year.isa_used, 10000.0)
        self.assertEqual(year.income_shortfall, 0.0)

    def test_withdrawal_engine_carries_strategy_pension_need_into_tax_boundary(self):
        timeline = [RetirementYear(age=65, calendar_year=2026, spouse_age=62)]
        year = timeline[0]
        year.pension_needed = 25000.0

        WithdrawalEngine(self.assumptions).apply(timeline)

        self.assertEqual(year.pension_withdrawal, 25000.0)

    def test_tax_grosses_up_net_pension_need_and_preserves_net_target(self):
        result = self.execute_projection()
        year = result.timeline[0]

        self.assertGreater(year.gross_pension_income, year.net_pension_income)
        self.assertAlmostEqual(
            year.gross_pension_income - year.income_tax,
            year.net_pension_income,
            places=2,
        )
        self.assertEqual(year.net_pension_income, year.pension_needed)

    def test_tax_and_pension_engines_agree_on_final_gross_withdrawal(self):
        result = self.execute_projection()

        for year in result.timeline:
            self.assertAlmostEqual(
                year.pension_withdrawal,
                year.gross_pension_income,
                places=2,
            )
            self.assertAlmostEqual(
                year.closing_pension,
                year.opening_pension + year.pension_growth - year.pension_withdrawal,
                places=1,
            )

    def test_tax_free_cash_is_capped_by_lifetime_available_amount(self):
        self.assumptions.set("tax_free_pension_percentage", 0.25)
        result = self.execute_projection()
        available = 200000.0 * 0.25
        total_used = sum(year.tax_free_cash_used for year in result.timeline)

        self.assertLessEqual(total_used, available + 0.01)
        self.assertAlmostEqual(
            result.timeline[-1].remaining_tax_free_cash,
            max(0.0, available - total_used),
            places=2,
        )

    def test_disabling_tax_free_cash_makes_entire_pension_withdrawal_taxable(self):
        self.assumptions.set("use_tax_free_cash", False)
        result = self.execute_projection()

        for year in result.timeline:
            self.assertEqual(year.tax_free_cash_used, 0.0)
            self.assertAlmostEqual(
                year.taxable_pension_withdrawal,
                year.pension_withdrawal,
                places=2,
            )

    def test_state_pension_reduces_pension_need_before_tax_is_applied(self):
        result = self.execute_projection()
        age_67 = next(year for year in result.timeline if year.age == 67)

        self.assertGreater(age_67.your_state_pension, 0.0)
        self.assertLess(age_67.pension_needed, age_67.target_spending)
        self.assertGreater(age_67.gross_pension_income, age_67.pension_needed)

    def test_exhausted_isa_creates_explicit_income_shortfall(self):
        self.assumptions.set("starting_pension", 0.0)
        self.assumptions.set("starting_savings", 0.0)
        self.assumptions.set("starting_isa", 0.0)
        self.assumptions.set("property_sale", 0.0)
        self.assumptions.set("state_pension_full", 0.0)
        self.assumptions.set("max_pension_income", 0.0)
        self.assumptions.set("spending_phase_1", 20000.0)
        self.assumptions.set("spending_phase_2", 20000.0)
        self.assumptions.set("spending_phase_3", 20000.0)

        result = self.execute_projection()
        first = result.timeline[0]

        self.assertEqual(first.pension_needed, 0.0)
        self.assertEqual(first.isa_used, 0.0)
        self.assertEqual(first.income_shortfall, first.target_spending)
        self.assertEqual(first.gross_pension_income, 0.0)
        self.assertEqual(first.income_tax, 0.0)

    def test_max_pension_income_remains_strategy_constraint_after_tax_gross_up(self):
        result = self.execute_projection()

        for year in result.timeline:
            self.assertLessEqual(
                year.pension_needed,
                self.assumptions.get("max_pension_income") + 0.01,
            )
            self.assertGreaterEqual(year.gross_pension_income, year.pension_needed)

    def test_summary_tax_and_gross_income_are_derived_from_final_timeline(self):
        result = self.execute_projection()

        self.assertAlmostEqual(
            result.summary["gross_pension"],
            sum(year.gross_pension_income for year in result.timeline),
            places=2,
        )
        self.assertAlmostEqual(
            result.summary["total_tax"],
            sum(year.income_tax for year in result.timeline),
            places=2,
        )
        self.assertEqual(result.summary["ending_pension"], result.timeline[-1].closing_pension)

    def test_tax_withdrawal_pipeline_is_deterministic(self):
        first = self.execute_projection()
        second = self.execute_projection()

        self.assertEqual(first.summary, second.summary)
        self.assertEqual(
            [
                (y.age, y.pension_needed, y.gross_pension_income, y.income_tax, y.closing_pension)
                for y in first.timeline
            ],
            [
                (y.age, y.pension_needed, y.gross_pension_income, y.income_tax, y.closing_pension)
                for y in second.timeline
            ],
        )


if __name__ == "__main__":
    unittest.main()

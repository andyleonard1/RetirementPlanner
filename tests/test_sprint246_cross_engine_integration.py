import unittest

from planner.assumptions import Assumptions
from planner.planner import RetirementPlanner


class Sprint246CrossEngineIntegrationTests(unittest.TestCase):
    """End-to-end regression coverage for the shared projection timeline."""

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
                "spending_phase_1": 20000.0,
                "spending_phase_2": 20000.0,
                "spending_phase_3": 20000.0,
                "phase_1_end_age": 69,
                "phase_2_end_age": 79,
            }
        for key, value in values.items():
            self.assumptions[key] = value

    def execute_projection(self):
        return RetirementPlanner(self.assumptions).run()

    def test_complete_projection_populates_shared_timeline_across_engine_boundaries(self):
        result = self.execute_projection()

        self.assertEqual(len(result.timeline), 6)
        for year in result.timeline:
            self.assertIsNotNone(year.inflation_rate)
            self.assertGreaterEqual(year.inflation_factor, 1.0)
            self.assertGreaterEqual(year.savings_closing, 0.0)
            self.assertGreaterEqual(year.isa_closing, 0.0)
            self.assertGreaterEqual(year.closing_pension, 0.0)
            self.assertGreaterEqual(year.target_spending, 0.0)

    def test_inflation_flows_from_inflation_engine_into_spending_and_tax_boundaries(self):
        result = self.execute_projection()

        first, second = result.timeline[:2]
        self.assertAlmostEqual(first.inflation_factor, 1.0)
        self.assertAlmostEqual(second.inflation_factor, 1.025)
        self.assertAlmostEqual(first.target_spending, 20000.0)
        self.assertAlmostEqual(second.target_spending, 20500.0)

        # With tax inflation-linking enabled, the second year's allowance is
        # scaled by the same shared inflation factor used by the projection.
        expected_allowance = self.assumptions["personal_allowance"] * second.inflation_factor
        self.assertLessEqual(second.taxable_pension_income, max(0.0, second.gross_pension_income + second.your_state_pension - expected_allowance) + 0.01)

    def test_state_pension_flows_into_cash_available_and_changes_strategy_need(self):
        result = self.execute_projection()

        age_67 = next(year for year in result.timeline if year.age == 67)
        self.assertGreater(age_67.your_state_pension, 0.0)
        self.assertAlmostEqual(
            age_67.cash_available,
            age_67.savings_interest + age_67.your_state_pension + age_67.spouse_state_pension,
            places=2,
        )
        self.assertLessEqual(age_67.pension_needed, age_67.target_spending)

    def test_property_sale_flows_into_both_asset_engines_on_sale_year(self):
        result = self.execute_projection()

        sale_year = next(year for year in result.timeline if year.age == 67)
        self.assertEqual(sale_year.property_sale_proceeds, 100000.0)
        self.assertEqual(
            sale_year.property_sale_to_isa + sale_year.property_sale_to_savings,
            sale_year.property_sale_proceeds,
        )
        self.assertGreater(sale_year.property_sale_to_isa, 0.0)
        self.assertGreater(sale_year.property_sale_to_savings, 0.0)
        self.assertGreater(sale_year.isa_contribution, 0.0)
        self.assertGreater(sale_year.savings_money_in, 0.0)

    def test_scheduled_investment_and_isa_returns_reach_pension_and_isa_roll_forwards(self):
        self.assumptions["investment_return_schedule_enabled"] = True
        self.assumptions["investment_return_schedule"] = {"2027": 0.10}
        self.assumptions["isa_return_schedule_enabled"] = True
        self.assumptions["isa_return_schedule"] = {"2027": 0.08}

        result = self.execute_projection()
        year_2027 = next(year for year in result.timeline if year.calendar_year == 2027)

        self.assertAlmostEqual(
            year_2027.pension_growth,
            year_2027.opening_pension * 0.10,
            places=2,
        )
        self.assertAlmostEqual(year_2027.isa_growth_rate, 0.08)
        self.assertAlmostEqual(
            year_2027.isa_growth,
            year_2027.isa_opening * 0.08,
            places=2,
        )

    def test_strategy_withdrawal_tax_and_pension_engines_preserve_cross_engine_flow(self):
        result = self.execute_projection()

        for year in result.timeline:
            self.assertLessEqual(year.pension_needed, self.assumptions["max_pension_income"] + 0.01)
            self.assertAlmostEqual(year.pension_withdrawal, year.gross_pension_income, places=2)
            self.assertAlmostEqual(
                year.closing_pension,
                year.opening_pension + year.pension_growth - year.pension_withdrawal,
                places=1,
            )
            self.assertLessEqual(year.tax_free_cash_used, year.gross_pension_income * self.assumptions["tax_free_pension_percentage"] + 0.01)

    def test_summary_is_derived_from_final_timeline_state_and_aggregates(self):
        result = self.execute_projection()
        final = result.timeline[-1]

        self.assertEqual(result.summary["ending_pension"], final.closing_pension)
        self.assertEqual(result.summary["ending_savings"], final.savings_closing)
        self.assertEqual(result.summary["ending_isa"], final.isa_closing)
        self.assertEqual(result.summary["ending_assets"], final.closing_pension + final.savings_closing + final.isa_closing)
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
        self.assertEqual(result.success, result.summary["success"])

    def test_repeated_complete_runs_are_deterministic(self):
        first = self.execute_projection()
        second = self.execute_projection()

        self.assertEqual(first.summary, second.summary)
        self.assertEqual(
            [(y.age, y.closing_pension, y.savings_closing, y.isa_closing) for y in first.timeline],
            [(y.age, y.closing_pension, y.savings_closing, y.isa_closing) for y in second.timeline],
        )


if __name__ == "__main__":
    unittest.main()

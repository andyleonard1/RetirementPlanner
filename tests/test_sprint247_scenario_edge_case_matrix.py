import unittest

from planner.assumptions import Assumptions
from planner.planner import RetirementPlanner


class Sprint247ScenarioEdgeCaseMatrixTests(unittest.TestCase):
    """Boundary scenario coverage for projection and schedule edge cases."""

    def make_assumptions(self):
        assumptions = Assumptions()
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
            "spending_phase_2": 18000.0,
            "spending_phase_3": 16000.0,
            "phase_1_end_age": 67,
            "phase_2_end_age": 69,
        }
        for key, value in values.items():
            assumptions[key] = value
        return assumptions

    def execute_projection(self, assumptions=None):
        return RetirementPlanner(assumptions or self.make_assumptions()).run()

    def test_projection_horizon_equal_to_current_age_produces_single_boundary_row(self):
        assumptions = self.make_assumptions()
        assumptions.set("projection_end_age", assumptions.get("current_age"))

        result = self.execute_projection(assumptions)

        self.assertEqual(len(result.timeline), 1)
        self.assertEqual(result.timeline[0].age, 65)
        self.assertEqual(result.timeline[0].calendar_year, 2026)
        self.assertEqual(result.summary["ending_pension"], result.timeline[0].closing_pension)

    def test_property_sale_on_first_projected_age_is_applied_once(self):
        assumptions = self.make_assumptions()
        assumptions.set("property_sale_age", assumptions.get("current_age"))

        result = self.execute_projection(assumptions)

        proceeds = [year.property_sale_proceeds for year in result.timeline]
        self.assertEqual(proceeds[0], 100000.0)
        self.assertEqual(sum(proceeds), 100000.0)

    def test_property_sale_after_projection_horizon_is_not_injected(self):
        assumptions = self.make_assumptions()
        assumptions.set("property_sale_age", 99)

        result = self.execute_projection(assumptions)

        self.assertTrue(all(year.property_sale_proceeds == 0.0 for year in result.timeline))
        self.assertEqual(sum(year.property_sale_proceeds for year in result.timeline), 0.0)

    def test_spending_phase_boundary_switches_to_phase_two_at_next_age(self):
        result = self.execute_projection()

        age_67 = next(year for year in result.timeline if year.age == 67)
        age_68 = next(year for year in result.timeline if year.age == 68)

        self.assertAlmostEqual(age_67.target_spending, 20000.0 * age_67.inflation_factor, places=2)
        self.assertAlmostEqual(age_68.target_spending, 18000.0 * age_68.inflation_factor, places=2)
        self.assertLess(age_68.target_spending, age_67.target_spending)

    def test_second_spending_phase_boundary_switches_to_phase_three(self):
        result = self.execute_projection()

        age_69 = next(year for year in result.timeline if year.age == 69)
        age_70 = next(year for year in result.timeline if year.age == 70)

        self.assertAlmostEqual(age_69.target_spending, 18000.0 * age_69.inflation_factor, places=2)
        self.assertAlmostEqual(age_70.target_spending, 16000.0 * age_70.inflation_factor, places=2)
        self.assertLess(age_70.target_spending, age_69.target_spending)

    def test_schedule_year_before_horizon_does_not_affect_projection(self):
        assumptions = self.make_assumptions()
        assumptions.set("investment_return_schedule_enabled", True)
        assumptions.set("investment_return_schedule", {"2020": 0.20})

        baseline = self.execute_projection()
        scheduled = self.execute_projection(assumptions)

        self.assertEqual(
            [(y.age, y.closing_pension) for y in baseline.timeline],
            [(y.age, y.closing_pension) for y in scheduled.timeline],
        )

    def test_schedule_at_last_projected_year_applies_only_to_that_year(self):
        assumptions = self.make_assumptions()
        assumptions.set("investment_return_schedule_enabled", True)
        assumptions.set("investment_return_schedule", {"2031": 0.10})

        result = self.execute_projection(assumptions)

        last = result.timeline[-1]
        previous = result.timeline[-2]
        self.assertEqual(last.calendar_year, 2031)
        self.assertAlmostEqual(last.pension_growth, last.opening_pension * 0.10, places=2)
        self.assertNotAlmostEqual(previous.pension_growth, previous.opening_pension * 0.10, places=2)

    def test_isa_return_schedule_at_horizon_end_updates_only_final_isa_growth(self):
        assumptions = self.make_assumptions()
        assumptions.set("isa_return_schedule_enabled", True)
        assumptions.set("isa_return_schedule", {"2031": 0.12})

        result = self.execute_projection(assumptions)

        last = result.timeline[-1]
        previous = result.timeline[-2]
        self.assertEqual(last.calendar_year, 2031)
        self.assertAlmostEqual(last.isa_growth_rate, 0.12)
        self.assertAlmostEqual(last.isa_growth, last.isa_opening * 0.12, places=2)
        self.assertNotAlmostEqual(previous.isa_growth_rate, 0.12)


if __name__ == "__main__":
    unittest.main()

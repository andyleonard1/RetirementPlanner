import unittest

from planner.assumptions import Assumptions
from planner.assumptions_schema import AssumptionsSchema
from planner.cashflow_engine import CashFlowEngine
from planner.models import RetirementYear


class TestSprint218AnnualSpendingSchedule(unittest.TestCase):
    def setUp(self):
        self.assumptions = Assumptions()
        self.assumptions.set("spending_phase_1", 35000.0)
        self.assumptions.set("spending_phase_2", 32000.0)
        self.assumptions.set("spending_phase_3", 28000.0)
        self.assumptions.set("phase_1_end_age", 69)
        self.assumptions.set("phase_2_end_age", 79)
        self.assumptions.set("inflation_link_spending", False)
        self.assumptions.set("annual_spending_schedule_enabled", True)
        self.assumptions.set(
            "annual_spending_schedule",
            {"2028": 39000.0, "2030": 36000.0},
        )

    def make_year(self, age, year):
        return RetirementYear(age=age, calendar_year=year, spouse_age=age - 2)

    def test_matching_calendar_year_overrides_age_phase(self):
        year = self.make_year(63, 2028)
        CashFlowEngine(self.assumptions).apply([year])
        self.assertEqual(year.target_spending, 39000.0)

    def test_schedule_applies_year_by_year(self):
        years = [self.make_year(63, 2028), self.make_year(65, 2030)]
        CashFlowEngine(self.assumptions).apply(years)
        self.assertEqual(years[0].target_spending, 39000.0)
        self.assertEqual(years[1].target_spending, 36000.0)

    def test_missing_schedule_year_falls_back_to_existing_age_phase(self):
        year = self.make_year(64, 2029)
        CashFlowEngine(self.assumptions).apply([year])
        self.assertEqual(year.target_spending, 35000.0)

    def test_disabled_schedule_preserves_existing_age_phase(self):
        self.assumptions.set("annual_spending_schedule_enabled", False)
        year = self.make_year(63, 2028)
        CashFlowEngine(self.assumptions).apply([year])
        self.assertEqual(year.target_spending, 35000.0)

    def test_schedule_remains_a_nominal_layer_before_inflation_link(self):
        self.assumptions.set("inflation_link_spending", True)
        year = self.make_year(63, 2028)
        year.inflation_factor = 1.10
        CashFlowEngine(self.assumptions).apply([year])
        self.assertEqual(year.target_spending, 42900.0)

    def test_invalid_schedule_value_and_key_are_rejected(self):
        data = dict(self.assumptions.data)
        data["annual_spending_schedule"] = {"2028": 0.0}
        with self.assertRaises(ValueError):
            AssumptionsSchema.validate(data)

        data["annual_spending_schedule"] = {"28": 39000.0}
        with self.assertRaises(ValueError):
            AssumptionsSchema.validate(data)


if __name__ == "__main__":
    unittest.main()

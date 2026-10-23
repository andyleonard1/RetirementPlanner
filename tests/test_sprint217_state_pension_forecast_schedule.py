import unittest

from planner.assumptions import Assumptions
from planner.models import RetirementYear
from planner.state_pension import StatePensionEngine


class TestSprint217StatePensionForecastSchedule(unittest.TestCase):

    def setUp(self):
        self.assumptions = Assumptions()
        self.assumptions.set("state_pension_full", 10000.0)
        self.assumptions.set("state_pension_earnings_growth", 0.03)
        self.assumptions.set("inflation_rate", 0.02)
        self.assumptions.set("state_pension_triple_lock_enabled", True)
        self.assumptions.set("state_pension_earnings_growth_schedule_enabled", True)
        self.assumptions.set(
            "state_pension_earnings_growth_schedule",
            {"2030": 0.04, "2031": 0.05},
        )

    def make_year(self, age, year):
        return RetirementYear(age=age, calendar_year=year, spouse_age=age - 2)

    def test_schedule_overrides_base_earnings_forecast_for_matching_year(self):
        years = [self.make_year(68, 2030)]
        StatePensionEngine(self.assumptions).apply(years)
        self.assertEqual(years[0].your_state_pension, 10400.00)

    def test_schedule_applies_year_by_year(self):
        years = [self.make_year(68, 2030), self.make_year(69, 2031)]
        StatePensionEngine(self.assumptions).apply(years)
        self.assertEqual(years[0].your_state_pension, 10400.00)
        self.assertEqual(years[1].your_state_pension, 10920.00)

    def test_cpi_still_wins_when_above_scheduled_earnings_growth(self):
        self.assumptions.set("inflation_rate", 0.06)
        years = [self.make_year(68, 2030)]
        StatePensionEngine(self.assumptions).apply(years)
        self.assertEqual(years[0].your_state_pension, 10600.00)

    def test_missing_schedule_year_falls_back_to_base_earnings_growth(self):
        years = [self.make_year(68, 2029)]
        StatePensionEngine(self.assumptions).apply(years)
        self.assertEqual(years[0].your_state_pension, 10300.00)

    def test_disabled_schedule_preserves_base_earnings_forecast(self):
        self.assumptions.set("state_pension_earnings_growth_schedule_enabled", False)
        years = [self.make_year(68, 2030)]
        StatePensionEngine(self.assumptions).apply(years)
        self.assertEqual(years[0].your_state_pension, 10300.00)

    def test_schedule_affects_spouse_from_spouse_start_age(self):
        years = [self.make_year(69, 2030)]
        StatePensionEngine(self.assumptions).apply(years)
        self.assertEqual(years[0].spouse_state_pension, 10712.00)


if __name__ == "__main__":
    unittest.main()

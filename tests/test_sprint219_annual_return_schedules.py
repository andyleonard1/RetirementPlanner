import unittest

from planner.assumptions import Assumptions
from planner.planner import RetirementPlanner


class Sprint219AnnualReturnScheduleTests(unittest.TestCase):
    def _run(self, mutate):
        assumptions = Assumptions()
        mutate(assumptions)
        return RetirementPlanner(assumptions).run()

    def test_investment_schedule_overrides_base_by_calendar_year(self):
        result = self._run(lambda a: (
            a.set("investment_return_schedule_enabled", True),
            a.set("investment_return_schedule", {"2027": 0.08}),
        ))
        year = next(y for y in result.timeline if y.calendar_year == 2027)
        self.assertAlmostEqual(year.pension_growth, 660000 * (0.08 - 0.005), places=2)

    def test_investment_schedule_missing_year_falls_back_to_base(self):
        result = self._run(lambda a: (
            a.set("investment_return_schedule_enabled", True),
            a.set("investment_return_schedule", {"2099": 0.08}),
        ))
        year = next(y for y in result.timeline if y.calendar_year == 2027)
        self.assertAlmostEqual(year.pension_growth, 660000 * (0.0475 - 0.005), places=2)

    def test_investment_schedule_disabled_preserves_base(self):
        result = self._run(lambda a: a.set("investment_return_schedule", {"2027": 0.08}))
        year = next(y for y in result.timeline if y.calendar_year == 2027)
        self.assertAlmostEqual(year.pension_growth, 660000 * (0.0475 - 0.005), places=2)

    def test_isa_schedule_overrides_base_by_calendar_year(self):
        result = self._run(lambda a: (
            a.set("isa_return_schedule_enabled", True),
            a.set("isa_return_schedule", {"2027": 0.07}),
        ))
        year = next(y for y in result.timeline if y.calendar_year == 2027)
        self.assertAlmostEqual(year.isa_growth_rate, 0.07)

    def test_isa_schedule_missing_year_falls_back_to_base(self):
        result = self._run(lambda a: (
            a.set("isa_return_schedule_enabled", True),
            a.set("isa_return_schedule", {"2099": 0.07}),
        ))
        year = next(y for y in result.timeline if y.calendar_year == 2027)
        self.assertAlmostEqual(year.isa_growth_rate, 0.04)

    def test_isa_schedule_applies_year_by_year(self):
        result = self._run(lambda a: (
            a.set("isa_return_schedule_enabled", True),
            a.set("isa_return_schedule", {"2027": 0.07, "2028": 0.02}),
        ))
        y27 = next(y for y in result.timeline if y.calendar_year == 2027)
        y28 = next(y for y in result.timeline if y.calendar_year == 2028)
        self.assertAlmostEqual(y27.isa_growth_rate, 0.07)
        self.assertAlmostEqual(y28.isa_growth_rate, 0.02)

    def test_invalid_return_schedule_is_rejected(self):
        assumptions = Assumptions()
        assumptions.set("investment_return_schedule", {"2027": -1.1})
        with self.assertRaises(ValueError):
            assumptions.validate()

    def test_isa_schedule_disabled_preserves_base(self):
        result = self._run(lambda a: a.set("isa_return_schedule", {"2027": 0.07}))
        year = next(y for y in result.timeline if y.calendar_year == 2027)
        self.assertAlmostEqual(year.isa_growth_rate, 0.04)


if __name__ == "__main__":
    unittest.main()

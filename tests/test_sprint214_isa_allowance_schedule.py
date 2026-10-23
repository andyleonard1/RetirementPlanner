import unittest

from planner.assumptions import Assumptions
from planner.assumptions_schema import AssumptionsSchema
from planner.property_sale_engine import PropertySaleEngine
from planner.models import RetirementYear


class TestSprint214ISAllowanceSchedule(unittest.TestCase):
    def _year(self, calendar_year):
        return RetirementYear(age=67, calendar_year=calendar_year, spouse_age=64)

    def test_empty_schedule_preserves_existing_annual_allowance(self):
        assumptions = Assumptions()
        assumptions.set("annual_isa_allowance", 40000.0)
        year = self._year(2031)
        PropertySaleEngine(assumptions).apply([year])
        self.assertEqual(year.property_sale_to_isa, 40000.0)

    def test_schedule_uses_latest_prior_tax_year(self):
        assumptions = Assumptions()
        assumptions.set("annual_isa_allowance", 40000.0)
        assumptions.set("isa_allowance_schedule", {
            "2026/27": 40000.0,
            "2030/31": 42000.0,
        })
        assumptions.set("isa_allowance_schedule_enabled", True)
        year = self._year(2031)
        PropertySaleEngine(assumptions).apply([year])
        self.assertEqual(year.property_sale_to_isa, 42000.0)

    def test_schedule_future_entry_does_not_apply_early(self):
        assumptions = Assumptions()
        assumptions.set("annual_isa_allowance", 40000.0)
        assumptions.set("isa_allowance_schedule", {"2032/33": 45000.0})
        year = self._year(2031)
        PropertySaleEngine(assumptions).apply([year])
        self.assertEqual(year.property_sale_to_isa, 40000.0)

    def test_schedule_works_with_inflation_link_as_separate_layer(self):
        assumptions = Assumptions()
        assumptions.set("annual_isa_allowance", 40000.0)
        assumptions.set("isa_allowance_schedule", {"2030/31": 42000.0})
        assumptions.set("isa_allowance_schedule_enabled", True)
        assumptions.set("inflation_link_isa", True)
        year = self._year(2031)
        year.inflation_factor = 1.10
        PropertySaleEngine(assumptions).apply([year])
        self.assertEqual(year.property_sale_to_isa, 46200.0)

    def test_schedule_can_be_disabled_without_removing_configuration(self):
        assumptions = Assumptions()
        assumptions.set("annual_isa_allowance", 40000.0)
        assumptions.set("isa_allowance_schedule", {"2030/31": 42000.0})
        assumptions.set("isa_allowance_schedule_enabled", False)
        year = self._year(2031)
        PropertySaleEngine(assumptions).apply([year])
        self.assertEqual(year.property_sale_to_isa, 40000.0)

    def test_enabled_schedule_selects_scheduled_allowance(self):
        assumptions = Assumptions()
        assumptions.set("annual_isa_allowance", 40000.0)
        assumptions.set("isa_allowance_schedule", {"2030/31": 42000.0})
        assumptions.set("isa_allowance_schedule_enabled", True)
        year = self._year(2031)
        PropertySaleEngine(assumptions).apply([year])
        self.assertEqual(year.property_sale_to_isa, 42000.0)

    def test_invalid_schedule_tax_year_is_rejected(self):
        assumptions = Assumptions()
        assumptions.set("isa_allowance_schedule", {"2030/32": 42000.0})
        with self.assertRaises(ValueError):
            assumptions.validate()

    def test_invalid_schedule_allowance_is_rejected(self):
        assumptions = Assumptions()
        assumptions.set("isa_allowance_schedule", {"2030/31": -1.0})
        with self.assertRaises(ValueError):
            assumptions.validate()

    def test_schema_accepts_schedule_contract(self):
        assumptions = Assumptions()
        data = dict(assumptions.data)
        data["isa_allowance_schedule"] = {"2026/27": 40000.0}
        data["isa_allowance_schedule_enabled"] = True
        AssumptionsSchema.validate(data)


if __name__ == "__main__":
    unittest.main()

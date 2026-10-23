"""Sprint 279: ISA inflation-link opt-in and tax-year schedule boundaries."""
from __future__ import annotations

import json
from pathlib import Path
import unittest

from planner.assumptions import Assumptions
from planner.models import RetirementYear
from planner.property_sale_engine import PropertySaleEngine

ROOT = Path(__file__).resolve().parents[1]


class TestSprint279InflationAdjustedISAAllowance(unittest.TestCase):
    def _assumptions(self) -> Assumptions:
        assumptions = Assumptions()
        assumptions.set("property_sale", 100_000.0)
        assumptions.set("property_sale_age", 67)
        assumptions.set("annual_isa_allowance", 40_000.0)
        assumptions.set("isa_allowance_schedule_enabled", False)
        assumptions.set("isa_allowance_schedule", {})
        return assumptions

    def _year(self, calendar_year: int, inflation_factor: float = 1.0) -> RetirementYear:
        year = RetirementYear(age=67, calendar_year=calendar_year, spouse_age=64)
        year.inflation_factor = inflation_factor
        return year

    def test_shipped_default_is_opt_in_off(self):
        shipped = json.loads((ROOT / "data" / "assumptions.json").read_text(encoding="utf-8"))
        self.assertIs(shipped["inflation_link_isa"], False)
        self.assertEqual(self._assumptions().get("inflation_link_isa"), False)

    def test_default_off_keeps_nominal_allowance_even_with_inflation_factor(self):
        assumptions = self._assumptions()
        year = self._year(2031, 1.25)
        PropertySaleEngine(assumptions).apply([year])
        self.assertEqual(year.property_sale_to_isa, 40_000.0)
        self.assertEqual(year.property_sale_to_savings, 60_000.0)

    def test_explicit_opt_in_applies_compounded_inflation_factor(self):
        assumptions = self._assumptions()
        assumptions.set("inflation_link_isa", True)
        year = self._year(2031, 1.25)
        PropertySaleEngine(assumptions).apply([year])
        self.assertEqual(year.property_sale_to_isa, 50_000.0)
        self.assertEqual(year.property_sale_to_savings, 50_000.0)

    def test_schedule_transitions_at_configured_start_year_boundary(self):
        assumptions = self._assumptions()
        assumptions.set("isa_allowance_schedule_enabled", True)
        assumptions.set("isa_allowance_schedule", {
            "2026/27": 40_000.0,
            "2030/31": 42_000.0,
            "2032/33": 45_000.0,
        })
        years = [self._year(y) for y in (2029, 2030, 2031, 2032, 2033)]
        PropertySaleEngine(assumptions).apply(years)
        self.assertEqual(
            [y.property_sale_to_isa for y in years],
            [40_000.0, 42_000.0, 42_000.0, 45_000.0, 45_000.0],
        )

    def test_schedule_is_not_inflated_when_link_is_off(self):
        assumptions = self._assumptions()
        assumptions.set("isa_allowance_schedule_enabled", True)
        assumptions.set("isa_allowance_schedule", {"2030/31": 42_000.0})
        year = self._year(2031, 1.25)
        PropertySaleEngine(assumptions).apply([year])
        self.assertEqual(year.property_sale_to_isa, 42_000.0)

    def test_schedule_and_inflation_link_compose_only_when_both_enabled(self):
        assumptions = self._assumptions()
        assumptions.set("isa_allowance_schedule_enabled", True)
        assumptions.set("isa_allowance_schedule", {"2030/31": 42_000.0})
        assumptions.set("inflation_link_isa", True)
        year = self._year(2031, 1.10)
        PropertySaleEngine(assumptions).apply([year])
        self.assertEqual(year.property_sale_to_isa, 46_200.0)

    def test_inflated_allowance_remains_capped_at_sale_proceeds(self):
        assumptions = self._assumptions()
        assumptions.set("property_sale", 30_000.0)
        assumptions.set("inflation_link_isa", True)
        year = self._year(2031, 2.0)
        PropertySaleEngine(assumptions).apply([year])
        self.assertEqual(year.property_sale_to_isa, 30_000.0)
        self.assertEqual(year.property_sale_to_savings, 0.0)


if __name__ == "__main__":
    unittest.main()

import unittest

from planner.assumptions import Assumptions
from planner.planner import RetirementPlanner
from planner.property_sale_engine import PropertySaleEngine
from planner.models import RetirementYear


class TestSprint213InflationLinkedISACalculationWiring(unittest.TestCase):
    def _year(self, age=67, factor=1.0):
        year = RetirementYear(age=age, calendar_year=2031, spouse_age=64)
        year.inflation_factor = factor
        return year

    def test_enabled_isa_link_scales_allowance_by_year_inflation_factor(self):
        assumptions = Assumptions()
        assumptions.set("annual_isa_allowance", 40000.0)
        assumptions.set("inflation_link_isa", True)
        year = self._year(factor=1.25)

        PropertySaleEngine(assumptions).apply([year])

        self.assertEqual(year.property_sale_to_isa, 50000.0)
        self.assertEqual(year.property_sale_to_savings, 300000.0)

    def test_disabled_isa_link_keeps_nominal_allowance(self):
        assumptions = Assumptions()
        assumptions.set("annual_isa_allowance", 40000.0)
        assumptions.set("inflation_link_isa", False)
        year = self._year(factor=1.25)

        PropertySaleEngine(assumptions).apply([year])

        self.assertEqual(year.property_sale_to_isa, 40000.0)
        self.assertEqual(year.property_sale_to_savings, 310000.0)

    def test_first_projection_year_uses_nominal_allowance_when_linked(self):
        assumptions = Assumptions()
        assumptions.set("annual_isa_allowance", 40000.0)
        assumptions.set("inflation_link_isa", True)
        year = self._year(factor=1.0)

        PropertySaleEngine(assumptions).apply([year])

        self.assertEqual(year.property_sale_to_isa, 40000.0)

    def test_sale_proceeds_remain_capped_by_available_proceeds(self):
        assumptions = Assumptions()
        assumptions.set("property_sale", 30000.0)
        assumptions.set("annual_isa_allowance", 40000.0)
        assumptions.set("inflation_link_isa", True)
        year = self._year(factor=2.0)

        PropertySaleEngine(assumptions).apply([year])

        self.assertEqual(year.property_sale_to_isa, 30000.0)
        self.assertEqual(year.property_sale_to_savings, 0.0)

    def test_live_projection_changes_when_isa_link_is_disabled(self):
        linked = Assumptions()
        linked.set("inflation_link_isa", True)
        unlinked = Assumptions()
        unlinked.set("inflation_link_isa", False)

        linked_result = RetirementPlanner(linked).run()
        unlinked_result = RetirementPlanner(unlinked).run()

        sale_year_linked = next(y for y in linked_result.timeline if y.age == 67)
        sale_year_unlinked = next(y for y in unlinked_result.timeline if y.age == 67)

        self.assertGreater(
            sale_year_linked.property_sale_to_isa,
            sale_year_unlinked.property_sale_to_isa,
        )
        self.assertLess(
            sale_year_linked.property_sale_to_savings,
            sale_year_unlinked.property_sale_to_savings,
        )
        self.assertNotEqual(
            linked_result.timeline[-1].isa_closing,
            unlinked_result.timeline[-1].isa_closing,
        )

    def test_live_projection_uses_compounded_inflation_factor(self):
        assumptions = Assumptions()
        assumptions.set("inflation_link_isa", True)
        result = RetirementPlanner(assumptions).run()

        sale_year = next(y for y in result.timeline if y.age == 67)
        expected_allowance = 40000.0 * sale_year.inflation_factor

        self.assertAlmostEqual(
            sale_year.property_sale_to_isa,
            expected_allowance,
            places=2,
        )


if __name__ == "__main__":
    unittest.main()

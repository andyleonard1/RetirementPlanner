import unittest

from planner.assumptions import Assumptions
from planner.planner import RetirementPlanner
from planner.property_sale_engine import PropertySaleEngine
from planner.models import RetirementYear


class TestSprint210PropertySaleAndISAAllowance(unittest.TestCase):
    def make_year(self, age=67):
        return RetirementYear(age=age, calendar_year=2031, spouse_age=64)

    def test_property_sale_is_split_between_isa_allowance_and_savings(self):
        assumptions = Assumptions()
        assumptions.set("property_sale", 350000.0)
        assumptions.set("property_sale_age", 67)
        assumptions.set("annual_isa_allowance", 40000.0)

        year = self.make_year()
        PropertySaleEngine(assumptions).apply([year])

        self.assertEqual(year.property_sale_proceeds, 350000.0)
        self.assertEqual(year.property_sale_to_isa, 40000.0)
        self.assertEqual(year.property_sale_to_savings, 310000.0)
        self.assertEqual(year.isa_contribution, 40000.0)
        self.assertEqual(year.savings_money_in, 310000.0)

    def test_annual_isa_allowance_changes_end_to_end_projection_result(self):
        sheltered = Assumptions()
        sheltered.set("annual_isa_allowance", 40000.0)
        sheltered.set("property_sale", 350000.0)
        sheltered.set("property_sale_age", 67)

        unsheltered = Assumptions()
        unsheltered.set("annual_isa_allowance", 0.0)
        unsheltered.set("property_sale", 350000.0)
        unsheltered.set("property_sale_age", 67)

        sheltered_result = RetirementPlanner(sheltered).run()
        unsheltered_result = RetirementPlanner(unsheltered).run()

        self.assertGreater(
            sheltered_result.summary["ending_assets"],
            unsheltered_result.summary["ending_assets"],
        )

    def test_property_sale_changes_end_to_end_projection_result(self):
        with_sale = Assumptions()
        with_sale.set("property_sale", 350000.0)
        with_sale.set("property_sale_age", 67)

        without_sale = Assumptions()
        without_sale.set("property_sale", 0.0)
        without_sale.set("property_sale_age", 67)

        with_sale_result = RetirementPlanner(with_sale).run()
        without_sale_result = RetirementPlanner(without_sale).run()

        self.assertGreater(
            with_sale_result.summary["ending_assets"],
            without_sale_result.summary["ending_assets"],
        )

    def test_property_sale_age_must_be_inside_projection_period(self):
        assumptions = Assumptions()
        assumptions.set(
            "property_sale_age",
            assumptions.get("projection_end_age") + 1,
        )

        with self.assertRaisesRegex(
            ValueError,
            "property_sale_age must be within the projection period",
        ):
            assumptions.validate()


if __name__ == "__main__":
    unittest.main()

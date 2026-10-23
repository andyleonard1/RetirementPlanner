import unittest

from planner.assumptions import Assumptions
from planner.models import RetirementYear
from planner.pension_engine import PensionEngine
from planner.planner import RetirementPlanner
from planner.tax_engine import TaxEngine


class TestSprint207AssumptionCalculationCoverage(unittest.TestCase):
    def test_tax_free_pension_percentage_controls_initial_allowance(self):
        assumptions = Assumptions()
        assumptions.set("tax_free_pension_percentage", 0.10)

        engine = PensionEngine(assumptions)
        self.assertAlmostEqual(engine.remaining_tax_free_cash, 66000.0)

    def test_tax_free_pension_percentage_drives_tax_engine(self):
        assumptions = Assumptions()
        assumptions.set("tax_free_pension_percentage", 0.10)

        engine = TaxEngine(assumptions)
        year = RetirementYear(age=63, calendar_year=2027, spouse_age=60)
        year.pension_needed = 20000.0
        year.your_state_pension = 0.0

        engine.apply([year])

        self.assertGreater(year.tax_free_cash_used, 0.0)
        self.assertAlmostEqual(
            year.tax_free_cash_used,
            year.gross_pension_income * 0.10,
            places=2,
        )
        self.assertAlmostEqual(
            year.remaining_tax_free_cash,
            66000.0 - year.tax_free_cash_used,
            places=2,
        )

    def test_tax_free_pension_percentage_changes_projection_result(self):
        ten_percent = Assumptions()
        ten_percent.set("tax_free_pension_percentage", 0.10)
        twenty_five_percent = Assumptions()
        twenty_five_percent.set("tax_free_pension_percentage", 0.25)

        ten_result = RetirementPlanner(ten_percent).run()
        twenty_five_result = RetirementPlanner(twenty_five_percent).run()

        ten_tax_free = sum(
            year.tax_free_cash_used for year in ten_result.timeline
        )
        twenty_five_tax_free = sum(
            year.tax_free_cash_used for year in twenty_five_result.timeline
        )

        self.assertGreater(ten_tax_free, 0.0)
        self.assertGreater(twenty_five_tax_free, ten_tax_free)
        self.assertNotEqual(
            ten_result.summary["ending_assets"],
            twenty_five_result.summary["ending_assets"],
        )

    def test_tax_free_pension_percentage_validation_rejects_out_of_range(self):
        assumptions = Assumptions()
        assumptions.set("tax_free_pension_percentage", 1.1)
        with self.assertRaisesRegex(
            ValueError,
            "tax_free_pension_percentage must be between 0 and 1",
        ):
            assumptions.validate()


if __name__ == "__main__":
    unittest.main()

import unittest

from planner.assumptions import Assumptions
from planner.isa_engine import ISAEngine
from planner.models import RetirementYear


class TestISAEngine(unittest.TestCase):

    def setUp(self):

        self.assumptions = Assumptions()

        self.assumptions.set("starting_isa", 50000)
        self.assumptions.set("isa_growth_rate", 0.04)

        self.engine = ISAEngine(self.assumptions)

    def make_year(self):

        year = RetirementYear(
            age=65,
            calendar_year=2030,
            spouse_age=63,
        )

        year.isa_contribution = 0.0
        year.isa_used = 0.0

        return year

    def test_engine_can_be_created(self):
        self.assertIsNotNone(self.engine)

    def test_growth_without_transactions(self):

        year = self.make_year()

        self.engine.apply([year])

        self.assertEqual(year.isa_opening, 50000.00)
        self.assertEqual(year.isa_growth, 2000.00)
        self.assertEqual(year.isa_closing, 52000.00)

    def test_growth_with_contribution(self):

        year = self.make_year()

        year.isa_contribution = 10000

        self.engine.apply([year])

        self.assertEqual(year.isa_closing, 62000.00)

    def test_growth_with_withdrawal(self):

        year = self.make_year()

        year.isa_used = 5000

        self.engine.apply([year])

        self.assertEqual(year.isa_withdrawal, 5000.00)
        self.assertEqual(year.isa_closing, 47000.00)

    def test_contribution_and_withdrawal(self):

        year = self.make_year()

        year.isa_contribution = 8000
        year.isa_used = 3000

        self.engine.apply([year])

        self.assertEqual(year.isa_closing, 57000.00)

    def test_second_year_rolls_forward(self):

        year1 = self.make_year()
        year2 = self.make_year()

        self.engine.apply([year1, year2])

        self.assertEqual(year2.isa_opening, 52000.00)
        self.assertEqual(year2.isa_growth, 2080.00)
        self.assertEqual(year2.isa_closing, 54080.00)


if __name__ == "__main__":
    unittest.main()
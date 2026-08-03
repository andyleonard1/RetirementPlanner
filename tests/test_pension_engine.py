import unittest

from planner.assumptions import Assumptions
from planner.models import RetirementYear
from planner.pension_engine import PensionEngine


class TestPensionEngine(unittest.TestCase):

    def setUp(self):
        self.assumptions = Assumptions()

        # Override values for a predictable test
        self.assumptions["starting_pension"] = 100000
        self.assumptions["pension_growth"] = 0.05

        self.engine = PensionEngine(self.assumptions)

    def test_engine_can_be_created(self):
        self.assertIsNotNone(self.engine)

    def test_pension_growth_without_withdrawal(self):

        year = RetirementYear(
            age=65,
            calendar_year=2030,
            spouse_age=63
        )

        year.pension_withdrawal = 0

        timeline = [year]

        self.engine.apply(timeline)

        self.assertEqual(year.opening_pension, 100000.00)
        self.assertEqual(year.pension_growth, 5000.00)
        self.assertEqual(year.closing_pension, 105000.00)

    def test_pension_growth_with_withdrawal(self):

        year = RetirementYear(
            age=65,
            calendar_year=2030,
            spouse_age=63
        )

        year.pension_withdrawal = 10000

        timeline = [year]

        self.engine.apply(timeline)

        self.assertEqual(year.opening_pension, 100000.00)
        self.assertEqual(year.pension_growth, 5000.00)
        self.assertEqual(year.closing_pension, 95000.00)


if __name__ == "__main__":
    unittest.main()
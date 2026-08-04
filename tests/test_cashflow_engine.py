import unittest

from planner.assumptions import Assumptions
from planner.cashflow_engine import CashFlowEngine
from planner.models import RetirementYear


class TestCashFlowEngine(unittest.TestCase):

    def setUp(self):

        self.assumptions = Assumptions()

        self.assumptions.set("phase_1_end_age", 70)
        self.assumptions.set("phase_2_end_age", 80)

        self.assumptions.set("spending_phase_1", 35000)
        self.assumptions.set("spending_phase_2", 30000)
        self.assumptions.set("spending_phase_3", 25000)

        self.assumptions.set("inflation_link_spending", False)

        self.engine = CashFlowEngine(self.assumptions)

    def make_year(self, age):

        year = RetirementYear(
            age=age,
            calendar_year=2030,
            spouse_age=age - 2,
        )

        year.inflation_factor = 1.00
        year.savings_interest = 0.0
        year.your_state_pension = 0.0
        year.spouse_state_pension = 0.0

        return year

    def test_engine_can_be_created(self):
        self.assertIsNotNone(self.engine)

    def test_phase_1_spending(self):

        year = self.make_year(65)

        self.engine.apply([year])

        self.assertEqual(year.target_spending, 35000.00)

    def test_phase_2_spending(self):

        year = self.make_year(75)

        self.engine.apply([year])

        self.assertEqual(year.target_spending, 30000.00)

    def test_phase_3_spending(self):

        year = self.make_year(85)

        self.engine.apply([year])

        self.assertEqual(year.target_spending, 25000.00)

    def test_cash_available(self):

        year = self.make_year(70)

        year.savings_interest = 500
        year.your_state_pension = 12000
        year.spouse_state_pension = 8000

        self.engine.apply([year])

        self.assertEqual(year.cash_available, 20500.00)

    def test_required_pension_income(self):

        year = self.make_year(70)

        year.savings_interest = 500
        year.your_state_pension = 12000
        year.spouse_state_pension = 8000

        self.engine.apply([year])

        self.assertEqual(
            year.required_pension_income,
            14500.00,
        )

    def test_cash_remaining_initially_equals_cash_available(self):

        year = self.make_year(70)

        year.savings_interest = 400
        year.your_state_pension = 10000
        year.spouse_state_pension = 7000

        self.engine.apply([year])

        self.assertEqual(
            year.cash_remaining,
            year.cash_available,
        )

    def test_cash_to_isa_initially_zero(self):

        year = self.make_year(70)

        self.engine.apply([year])

        self.assertEqual(year.cash_to_isa, 0.0)

    def test_cash_spent_initially_zero(self):

        year = self.make_year(70)

        self.engine.apply([year])

        self.assertEqual(year.cash_spent, 0.0)


if __name__ == "__main__":
    unittest.main()
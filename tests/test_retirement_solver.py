import unittest

from planner.assumptions import Assumptions
from planner.services.retirement_solver import RetirementSolver


class TestRetirementSolver(unittest.TestCase):

    def test_can_create_solver(self):

        assumptions = Assumptions()

        solver = RetirementSolver(
            assumptions
        )

        self.assertIsNotNone(
            solver
        )
    def test_solver_returns_an_age(self):

        assumptions = Assumptions()

        solver = RetirementSolver(
            assumptions
        )

        age = solver.find_earliest_age()

        self.assertIsNotNone(age)

        self.assertGreaterEqual(age, 55)

if __name__ == "__main__":
    unittest.main()
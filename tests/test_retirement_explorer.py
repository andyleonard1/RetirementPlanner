import unittest

from planner.assumptions import Assumptions
from planner.services.retirement_solver import RetirementSolver


class TestRetirementExplorer(unittest.TestCase):

    def test_explore_returns_results(self):

        assumptions = Assumptions()

        solver = RetirementSolver(
            assumptions
        )

        results = solver.explore(60, 62)

        self.assertEqual(
            len(results),
            3,
        )

    def test_first_result_exists(self):

        assumptions = Assumptions()

        solver = RetirementSolver(
            assumptions
        )

        results = solver.explore(60, 62)

        self.assertIsNotNone(
            results[0]
        )


if __name__ == "__main__":
    unittest.main()
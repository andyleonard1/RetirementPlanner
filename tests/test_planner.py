import unittest

from planner.assumptions import Assumptions
from planner.planner import RetirementPlanner


class TestPlanner(unittest.TestCase):

    def setUp(self):
        self.assumptions = Assumptions()
        self.planner = RetirementPlanner(self.assumptions)

    def test_planner_runs(self):

        result = self.planner.run()

        self.assertIsNotNone(result)

    def test_timeline_exists(self):

        result = self.planner.run()

        self.assertGreater(len(result.timeline), 0)

    def test_first_year_exists(self):

        result = self.planner.run()

        self.assertIsNotNone(result.timeline[0])

    def test_last_year_exists(self):

        result = self.planner.run()

        self.assertIsNotNone(result.timeline[-1])

    def test_pension_rolls_forward(self):

        result = self.planner.run()

        timeline = result.timeline

        for previous, current in zip(timeline, timeline[1:]):

            self.assertAlmostEqual(
                previous.closing_pension,
                current.opening_pension,
                places=2,
            )

    def test_isa_rolls_forward(self):

        result = self.planner.run()

        timeline = result.timeline

        for previous, current in zip(timeline, timeline[1:]):

            self.assertAlmostEqual(
                previous.isa_closing,
                current.isa_opening,
                places=2,
            )

    def test_savings_rolls_forward(self):

        result = self.planner.run()

        timeline = result.timeline

        for previous, current in zip(timeline, timeline[1:]):

            self.assertAlmostEqual(
                previous.savings_closing,
                current.savings_opening,
                places=2,
            )


if __name__ == "__main__":
    unittest.main()
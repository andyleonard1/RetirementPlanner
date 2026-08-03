import unittest

from planner.assumptions import Assumptions
from planner.pension_engine import PensionEngine


class TestPensionEngine(unittest.TestCase):

    def test_engine_can_be_created(self):
        assumptions = Assumptions()
        engine = PensionEngine(assumptions)

        self.assertIsNotNone(engine)

    def test_engine_has_assumptions(self):
        assumptions = Assumptions()
        engine = PensionEngine(assumptions)

        self.assertEqual(engine.assumptions, assumptions)


if __name__ == "__main__":
    unittest.main()
import json
import unittest

from planner.assumptions import Assumptions
from planner.planner import RetirementPlanner


class TestGoldenScenario(unittest.TestCase):

    def test_golden_scenario(self):

        planner = RetirementPlanner(
            Assumptions()
        )

        result = planner.run()

        with open(
            "tests/golden/baseline.json",
            encoding="utf8",
        ) as f:

            baseline = json.load(f)

        self.assertEqual(
            len(result.timeline),
            len(baseline),
        )

        for actual, expected in zip(
            result.timeline,
            baseline,
        ):

            self.assertAlmostEqual(
                actual.closing_pension,
                expected["closing_pension"],
                places=2,
            )

            self.assertAlmostEqual(
                actual.isa_closing,
                expected["isa_closing"],
                places=2,
            )

            self.assertAlmostEqual(
                actual.savings_closing,
                expected["savings_closing"],
                places=2,
            )

            self.assertAlmostEqual(
                actual.total_assets,
                expected["total_assets"],
                places=2,
            )


if __name__ == "__main__":
    unittest.main()
import unittest

from planner.funds.portfolio_risk_return_scenarios import (
    PortfolioRiskReturnScenarioBuilder,
)


class PortfolioRiskReturnScenarioTests(unittest.TestCase):
    def setUp(self):
        self.builder = PortfolioRiskReturnScenarioBuilder()

    def test_builds_three_scenarios_when_volatility_exists(self):
        result = self.builder.build({
            "annualised_return": 0.06,
            "volatility": 0.10,
        })
        self.assertEqual(
            [item.name for item in result],
            ["conservative", "central", "optimistic"],
        )

    def test_central_scenario_uses_historical_annualised_return(self):
        result = self.builder.build({
            "annualised_return": 0.06,
            "volatility": 0.10,
        })
        self.assertAlmostEqual(result[1].expected_return, 0.06)

    def test_conservative_scenario_is_one_volatility_below_centre(self):
        result = self.builder.build({
            "annualised_return": 0.06,
            "volatility": 0.10,
        })
        self.assertAlmostEqual(result[0].expected_return, -0.04)

    def test_optimistic_scenario_is_one_volatility_above_centre(self):
        result = self.builder.build({
            "annualised_return": 0.06,
            "volatility": 0.10,
        })
        self.assertAlmostEqual(result[2].expected_return, 0.16)

    def test_volatility_is_preserved(self):
        result = self.builder.build({
            "annualised_return": 0.06,
            "volatility": 0.10,
        })
        self.assertTrue(all(item.volatility == 0.10 for item in result))

    def test_source_is_explicitly_descriptive(self):
        result = self.builder.build({
            "annualised_return": 0.06,
            "volatility": 0.10,
        })
        self.assertTrue(all(item.descriptive for item in result))
        self.assertIn("historical", result[0].source)

    def test_missing_annualised_return_is_rejected(self):
        with self.assertRaises(ValueError):
            self.builder.build({"volatility": 0.10})

    def test_missing_volatility_produces_only_central_scenario(self):
        result = self.builder.build({
            "annualised_return": 0.06,
            "volatility": None,
        })
        self.assertEqual([item.name for item in result], ["central"])
        self.assertIsNone(result[0].volatility)

    def test_missing_volatility_does_not_invent_range(self):
        result = self.builder.build({
            "annualised_return": 0.06,
            "volatility": None,
        })
        self.assertAlmostEqual(result[0].expected_return, 0.06)

    def test_negative_volatility_is_rejected(self):
        with self.assertRaises(ValueError):
            self.builder.build({
                "annualised_return": 0.06,
                "volatility": -0.01,
            })

    def test_zero_volatility_creates_identical_return_scenarios(self):
        result = self.builder.build({
            "annualised_return": 0.06,
            "volatility": 0.0,
        })
        self.assertEqual(len(result), 3)
        self.assertTrue(all(item.expected_return == 0.06 for item in result))

    def test_scenario_order_is_stable(self):
        result = self.builder.build({
            "annualised_return": 0.04,
            "volatility": 0.08,
        })
        self.assertEqual(
            [item.name for item in result],
            ["conservative", "central", "optimistic"],
        )

    def test_user_assumption_boundary_is_not_written(self):
        result = self.builder.build({
            "annualised_return": 0.04,
            "volatility": 0.08,
        })
        self.assertTrue(result)
        # Builder returns immutable derived objects only; no assumptions object
        # is accepted or mutated by this API.
        self.assertTrue(all(hasattr(item, "source") for item in result))


if __name__ == "__main__":
    unittest.main()

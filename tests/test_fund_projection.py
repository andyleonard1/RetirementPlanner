import unittest

from planner.funds.fund_projection import FundProjectionBuilder


class FundProjectionBuilderTests(unittest.TestCase):
    def setUp(self):
        self.builder = FundProjectionBuilder()

    def test_uses_portfolio_return_as_expected_return(self):
        result = self.builder.build({
            "weighted_average_return": 0.055,
            "portfolio_volatility": 0.12,
        })
        self.assertAlmostEqual(result.expected_return, 0.055)

    def test_preserves_portfolio_volatility(self):
        result = self.builder.build({
            "weighted_average_return": 0.055,
            "portfolio_volatility": 0.12,
        })
        self.assertAlmostEqual(result.volatility, 0.12)

    def test_builds_descriptive_lower_bound(self):
        result = self.builder.build({
            "weighted_average_return": 0.05,
            "portfolio_volatility": 0.10,
        })
        self.assertAlmostEqual(result.minimum_return, -0.05)

    def test_builds_descriptive_upper_bound(self):
        result = self.builder.build({
            "weighted_average_return": 0.05,
            "portfolio_volatility": 0.10,
        })
        self.assertAlmostEqual(result.maximum_return, 0.15)

    def test_custom_scenario_name_is_preserved(self):
        result = self.builder.build(
            {
                "weighted_average_return": 0.04,
                "portfolio_volatility": 0.08,
            },
            name="actual_fund",
        )
        self.assertEqual(result.name, "actual_fund")

    def test_missing_metrics_are_rejected(self):
        with self.assertRaises(ValueError):
            self.builder.build({
                "weighted_average_return": 0.04,
            })

    def test_negative_volatility_is_rejected(self):
        with self.assertRaises(ValueError):
            self.builder.build({
                "weighted_average_return": 0.04,
                "portfolio_volatility": -0.01,
            })


if __name__ == "__main__":
    unittest.main()

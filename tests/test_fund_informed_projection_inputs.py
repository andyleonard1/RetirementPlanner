import unittest
from planner.funds.fund_informed_projection_inputs import FundInformedProjectionInputBuilder
from planner.funds.portfolio_risk_return_scenarios import PortfolioRiskReturnScenario

class FundInformedProjectionInputTests(unittest.TestCase):
    def setUp(self):
        self.b = FundInformedProjectionInputBuilder()
        self.s = PortfolioRiskReturnScenario("central", 0.06, 0.10, "historical")
        self.a = (("GB00BRDCMN86:GBP", 0.75), ("SKY_NEW_DRAWDOWN_LIFESTYLE", 0.25))

    def test_starting_pension_preserved(self):
        self.assertEqual(self.b.build(665000, self.s, self.a).starting_pension, 665000)

    def test_scenario_preserved(self):
        r = self.b.build(665000, self.s, self.a)
        self.assertEqual(r.scenario_name, "central")
        self.assertAlmostEqual(r.expected_return, .06)
        self.assertAlmostEqual(r.volatility, .10)

    def test_allocation_preserved(self):
        self.assertEqual(self.b.build(665000, self.s, self.a).fund_allocation, self.a)

    def test_allocation_must_total_one(self):
        with self.assertRaises(ValueError):
            self.b.build(665000, self.s, (("A", .7), ("B", .25)))

    def test_empty_allocation_rejected(self):
        with self.assertRaises(ValueError):
            self.b.build(665000, self.s, ())

    def test_negative_allocation_rejected(self):
        with self.assertRaises(ValueError):
            self.b.build(665000, self.s, (("A", 1.1), ("B", -.1)))

    def test_negative_pension_rejected(self):
        with self.assertRaises(ValueError):
            self.b.build(-1, self.s, self.a)

    def test_negative_volatility_rejected(self):
        bad = PortfolioRiskReturnScenario("bad", .06, -.01, "test")
        with self.assertRaises(ValueError):
            self.b.build(665000, bad, self.a)

    def test_source_preserved(self):
        self.assertEqual(self.b.build(665000, self.s, self.a).source, "historical")

    def test_result_immutable(self):
        r = self.b.build(665000, self.s, self.a)
        with self.assertRaises(AttributeError):
            r.expected_return = .99

    def test_disabled(self):
        r = self.b.build_disabled(665000)
        self.assertFalse(r.enabled)
        self.assertEqual(r.scenario_name, "disabled")
        self.assertEqual(r.expected_return, 0.0)
        self.assertIsNone(r.volatility)
        self.assertEqual(r.fund_allocation, ())

    def test_fractional_pension(self):
        self.assertAlmostEqual(self.b.build(665000.5, self.s, self.a).starting_pension, 665000.5)

    def test_identifier_preserved(self):
        self.assertEqual(self.b.build(665000, self.s, self.a).fund_allocation[0][0], "GB00BRDCMN86:GBP")

    def test_negative_scenario_return_allowed(self):
        s = PortfolioRiskReturnScenario("conservative", -.04, .10, "historical")
        self.assertAlmostEqual(self.b.build(665000, s, self.a).expected_return, -.04)

    def test_disabled_preserves_pension(self):
        self.assertEqual(self.b.build_disabled(665000).starting_pension, 665000)

if __name__ == "__main__":
    unittest.main()

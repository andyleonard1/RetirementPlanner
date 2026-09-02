import unittest
from planner.funds.portfolio_risk_metrics import PortfolioRiskMetricsCalculator

class PortfolioRiskMetricsTests(unittest.TestCase):
    def setUp(self): self.calculator=PortfolioRiskMetricsCalculator()
    def test_weighted_average_return(self):
        r=self.calculator.calculate({"A":.75,"B":.25},{"A":[.10]*5,"B":[.20]*5}); self.assertTrue(r.calculation_available); self.assertAlmostEqual(r.weighted_average_return,.125)
    def test_portfolio_volatility(self):
        r=self.calculator.calculate({"A":.75,"B":.25},{"A":[.10,.12,.08,.10,.11],"B":[.20,.18,.22,.20,.19]}); self.assertTrue(r.calculation_available); self.assertGreaterEqual(r.portfolio_volatility,0)
    def test_excluded_fund_blocks_calculation(self):
        r=self.calculator.calculate({"A":.75,"B":.25},{"A":[.10]*5,"B":[.20]*3}); self.assertFalse(r.calculation_available); self.assertEqual(r.excluded_funds,("B",)); self.assertEqual(r.included_funds,("A",)); self.assertEqual(len(r.exclusion_reasons),1)
    def test_empty_input_raises(self):
        with self.assertRaises(ValueError): self.calculator.calculate({}, {})
    def test_all_funds_reported(self):
        r=self.calculator.calculate({"A":.75,"B":.25},{"A":[.10]*5,"B":[.20]*5}); self.assertEqual(r.included_funds,("A","B")); self.assertEqual(r.excluded_funds,())
    def test_custom_threshold(self):
        c=PortfolioRiskMetricsCalculator(risk_minimum_years=3,projection_minimum_years=6); r=c.calculate({"A":1.0},{"A":[.10,.10,.10]}); self.assertTrue(r.calculation_available)

if __name__=="__main__": unittest.main()

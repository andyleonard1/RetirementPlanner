import unittest
from planner.funds.investment_growth_calculation import InvestmentGrowthCalculator
from planner.funds.projection_engine_integration import ProjectionReturnDecision

class InvestmentGrowthCalculationTests(unittest.TestCase):
    def setUp(self): self.c=InvestmentGrowthCalculator()
    def d(self,r,fi=False): return ProjectionReturnDecision(r,"fund" if fi else "legacy",fi)
    def test_legacy_return_applied(self): self.assertAlmostEqual(self.c.calculate(100000,self.d(.04)).ending_balance,104000)
    def test_fund_return_applied(self): self.assertAlmostEqual(self.c.calculate(100000,self.d(.06,True)).ending_balance,106000)
    def test_zero_return(self): self.assertEqual(self.c.calculate(100000,self.d(0)).ending_balance,100000)
    def test_negative_return(self): self.assertAlmostEqual(self.c.calculate(100000,self.d(-.1,True)).ending_balance,90000)
    def test_return_preserved(self): self.assertAlmostEqual(self.c.calculate(100000,self.d(.075)).expected_return,.075)
    def test_balance_preserved(self): self.assertEqual(self.c.calculate(665000,self.d(.05)).starting_balance,665000)
    def test_source_preserved(self): self.assertEqual(self.c.calculate(100000,self.d(.06,True)).source,"fund")
    def test_flag_preserved(self): self.assertTrue(self.c.calculate(100000,self.d(.06,True)).fund_informed)
    def test_legacy_flag(self): self.assertFalse(self.c.calculate(100000,self.d(.04)).fund_informed)
    def test_negative_balance_rejected(self):
        with self.assertRaises(ValueError): self.c.calculate(-1,self.d(.04))
    def test_fractional_balance(self): self.assertAlmostEqual(self.c.calculate(100000.5,self.d(.04)).ending_balance,104000.52)
    def test_not_compounded_twice(self): self.assertAlmostEqual(self.c.calculate(100000,self.d(.1)).ending_balance,110000)
    def test_large_balance(self): self.assertAlmostEqual(self.c.calculate(1000000,self.d(.04)).ending_balance,1040000)
    def test_negative_fund_return(self): self.assertAlmostEqual(self.c.calculate(100000,self.d(-.4,True)).ending_balance,60000)
    def test_result_immutable(self):
        with self.assertRaises(AttributeError): self.c.calculate(100000,self.d(.04)).ending_balance=1
    def test_fund_and_legacy_same_return_same_balance(self):
        self.assertEqual(self.c.calculate(100000,self.d(.06)).ending_balance,self.c.calculate(100000,self.d(.06,True)).ending_balance)
    def test_different_returns_change_balance(self): self.assertNotEqual(self.c.calculate(100000,self.d(.04)).ending_balance,self.c.calculate(100000,self.d(.06,True)).ending_balance)
    def test_custom_source_does_not_change_math(self):
        r=self.c.calculate(250000,ProjectionReturnDecision(.08,"arbitrary",True))
        self.assertAlmostEqual(r.ending_balance,270000)
if __name__=="__main__": unittest.main()

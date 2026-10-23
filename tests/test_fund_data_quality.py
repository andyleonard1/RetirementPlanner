import unittest
from planner.funds.fund_data_quality import FundDataQualityAnalyzer
from planner.funds.fund_import import ImportedFundReturn

class FundDataQualityAnalyzerTests(unittest.TestCase):
    def test_contiguous_history_has_full_coverage(self):
        r=FundDataQualityAnalyzer().analyze([ImportedFundReturn("A",y,v) for y,v in [(2020,.05),(2021,.06),(2022,-.02),(2023,.08),(2024,.07)]])[0]
        self.assertEqual((r.first_year,r.last_year,r.expected_years,r.missing_years,r.coverage_rate),(2020,2024,5,(),1.0)); self.assertTrue(r.sufficient_history)
    def test_missing_year_is_reported(self):
        r=FundDataQualityAnalyzer().analyze([ImportedFundReturn("A",y,v) for y,v in [(2020,.05),(2021,.06),(2023,.08),(2024,.07)]])[0]
        self.assertEqual(r.missing_years,(2022,)); self.assertAlmostEqual(r.coverage_rate,.8); self.assertFalse(r.sufficient_history)
    def test_short_history_is_not_sufficient(self):
        r=FundDataQualityAnalyzer().analyze([ImportedFundReturn("A",y,.05) for y in (2022,2023,2024)])[0]; self.assertFalse(r.sufficient_history)
    def test_custom_minimum_history_can_be_used(self):
        r=FundDataQualityAnalyzer(3).analyze([ImportedFundReturn("A",y,.05) for y in (2022,2023,2024)])[0]; self.assertTrue(r.sufficient_history)
    def test_multiple_funds_are_independent(self):
        r=FundDataQualityAnalyzer(2).analyze([ImportedFundReturn("B",2022,.05),ImportedFundReturn("B",2023,.06),ImportedFundReturn("A",2020,.04),ImportedFundReturn("A",2021,.05)])
        self.assertEqual([x.fund_identifier for x in r],["A","B"])
    def test_empty_input(self): self.assertEqual(FundDataQualityAnalyzer().analyze([]),())
if __name__=="__main__": unittest.main()

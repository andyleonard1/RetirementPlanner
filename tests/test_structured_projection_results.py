import unittest

from planner.projection.structured_projection_results import (
    ProjectionYearResult,
    StructuredProjectionResultBuilder,
)


class StructuredProjectionResultTests(unittest.TestCase):
    def setUp(self):
        self.builder = StructuredProjectionResultBuilder()

    def rows(self):
        return (
            ProjectionYearResult(2030, 100000, 6000, 0, 106000),
            ProjectionYearResult(2031, 106000, 6360, 10000, 102360),
            ProjectionYearResult(2032, 102360, 6141.6, 10000, 98501.6),
        )

    def test_scenario_is_preserved(self):
        r = self.builder.build(
            scenario_name="central", source="fund-informed",
            starting_pension=100000, annual_return=.06, rows=self.rows())
        self.assertEqual(r.scenario_name, "central")

    def test_source_is_preserved(self):
        r = self.builder.build(
            scenario_name="central", source="fund-informed",
            starting_pension=100000, annual_return=.06, rows=self.rows())
        self.assertEqual(r.source, "fund-informed")

    def test_starting_pension_is_preserved(self):
        r = self.builder.build(
            scenario_name="central", source="fund-informed",
            starting_pension=100000, annual_return=.06, rows=self.rows())
        self.assertEqual(r.starting_pension, 100000)

    def test_annual_return_is_preserved(self):
        r = self.builder.build(
            scenario_name="central", source="fund-informed",
            starting_pension=100000, annual_return=.06, rows=self.rows())
        self.assertAlmostEqual(r.annual_return, .06)

    def test_years_are_preserved_in_order(self):
        r = self.builder.build(
            scenario_name="central", source="fund-informed",
            starting_pension=100000, annual_return=.06, rows=self.rows())
        self.assertEqual(tuple(x.year for x in r.years), (2030, 2031, 2032))

    def test_ending_balance(self):
        r = self.builder.build(
            scenario_name="central", source="fund-informed",
            starting_pension=100000, annual_return=.06, rows=self.rows())
        self.assertAlmostEqual(r.ending_balance, 98501.6)

    def test_total_investment_growth(self):
        r = self.builder.build(
            scenario_name="central", source="fund-informed",
            starting_pension=100000, annual_return=.06, rows=self.rows())
        self.assertAlmostEqual(r.total_investment_growth, 18501.6)

    def test_total_withdrawals(self):
        r = self.builder.build(
            scenario_name="central", source="fund-informed",
            starting_pension=100000, annual_return=.06, rows=self.rows())
        self.assertAlmostEqual(r.total_withdrawals, 20000)

    def test_empty_projection_uses_starting_balance_as_ending_balance(self):
        r = self.builder.build(
            scenario_name="central", source="fund-informed",
            starting_pension=100000, annual_return=.06, rows=())
        self.assertEqual(r.ending_balance, 100000)

    def test_rows_are_immutable(self):
        r = self.builder.build(
            scenario_name="central", source="fund-informed",
            starting_pension=100000, annual_return=.06, rows=self.rows())
        with self.assertRaises(AttributeError):
            r.years = ()

    def test_year_row_is_immutable(self):
        row = self.rows()[0]
        with self.assertRaises(AttributeError):
            row.ending_balance = 1

    def test_negative_starting_pension_is_rejected(self):
        with self.assertRaises(ValueError):
            self.builder.build(
                scenario_name="central", source="fund-informed",
                starting_pension=-1, annual_return=.06, rows=())

    def test_non_contiguous_balances_are_rejected(self):
        rows = (
            ProjectionYearResult(2030, 100000, 6000, 0, 106000),
            ProjectionYearResult(2031, 105000, 6300, 0, 111300),
        )
        with self.assertRaises(ValueError):
            self.builder.build(
                scenario_name="central", source="fund-informed",
                starting_pension=100000, annual_return=.06, rows=rows)

    def test_negative_growth_is_allowed_with_negative_return(self):
        rows = (ProjectionYearResult(2030, 100000, -4000, 0, 96000),)
        r = self.builder.build(
            scenario_name="conservative", source="fund-informed",
            starting_pension=100000, annual_return=-.04, rows=rows)
        self.assertAlmostEqual(r.ending_balance, 96000)

    def test_year_result_contains_required_components(self):
        row = self.rows()[1]
        self.assertEqual(row.year, 2031)
        self.assertEqual(row.starting_balance, 106000)
        self.assertEqual(row.withdrawals, 10000)

    def test_result_can_be_consumed_without_financial_recalculation(self):
        r = self.builder.build(
            scenario_name="central", source="fund-informed",
            starting_pension=100000, annual_return=.06, rows=self.rows())
        self.assertEqual(r.years[-1].ending_balance, r.ending_balance)

    def test_builder_materialises_iterables(self):
        r = self.builder.build(
            scenario_name="central", source="fund-informed",
            starting_pension=100000, annual_return=.06,
            rows=(x for x in self.rows()))
        self.assertEqual(len(r.years), 3)

    def test_result_has_no_mutable_year_list(self):
        r = self.builder.build(
            scenario_name="central", source="fund-informed",
            starting_pension=100000, annual_return=.06, rows=self.rows())
        self.assertIsInstance(r.years, tuple)

    def test_multiple_scenarios_remain_distinguishable(self):
        central = self.builder.build(
            scenario_name="central", source="fund-informed",
            starting_pension=100000, annual_return=.06, rows=self.rows())
        conservative = self.builder.build(
            scenario_name="conservative", source="fund-informed",
            starting_pension=100000, annual_return=-.04,
            rows=(ProjectionYearResult(2030,100000,-4000,0,96000),))
        self.assertNotEqual(central.scenario_name, conservative.scenario_name)

    def test_projection_result_is_a_presentation_model(self):
        r = self.builder.build(
            scenario_name="central", source="fund-informed",
            starting_pension=100000, annual_return=.06, rows=self.rows())
        self.assertTrue(hasattr(r, "years"))
        self.assertTrue(hasattr(r, "ending_balance"))
        self.assertTrue(hasattr(r, "total_withdrawals"))


if __name__ == "__main__":
    unittest.main()

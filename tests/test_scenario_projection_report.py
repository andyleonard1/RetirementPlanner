import unittest

from planner.assumptions import Assumptions
from planner.funds.portfolio_historical_statistics import PortfolioHistoricalStatisticsCalculator
from planner.projection.scenario_projection_comparison import ScenarioProjectionComparisonRunner
from planner.projection.scenario_projection_report import ScenarioProjectionReport


class ScenarioProjectionReportTests(unittest.TestCase):
    def setUp(self):
        statistics = PortfolioHistoricalStatisticsCalculator().calculate(
            {"Aviva": 0.75, "Sky": 0.25},
            {"Aviva": [0.10, 0.02, 0.08], "Sky": [0.20, 0.04, 0.16]},
        )
        self.comparison = ScenarioProjectionComparisonRunner().run(
            assumptions=Assumptions(), statistics=statistics
        )
        self.report = ScenarioProjectionReport()

    def test_build_returns_dict(self):
        self.assertIsInstance(self.report.build(self.comparison), dict)

    def test_all_three_scenarios_are_present(self):
        result = self.report.build(self.comparison)
        self.assertEqual(result["scenario_names"], ["conservative", "central", "optimistic"])

    def test_summary_contains_three_rows(self):
        self.assertEqual(len(self.report.build(self.comparison)["summary"]), 3)

    def test_summary_preserves_scenario_names(self):
        names = [x["name"] for x in self.report.build(self.comparison)["summary"]]
        self.assertEqual(names, ["conservative", "central", "optimistic"])

    def test_summary_preserves_returns(self):
        result = self.report.build(self.comparison)
        for item in result["summary"]:
            self.assertAlmostEqual(item["annual_return"], self.comparison.get(item["name"]).annual_return)

    def test_summary_preserves_ending_balances(self):
        result = self.report.build(self.comparison)
        for item in result["summary"]:
            self.assertEqual(item["ending_balance"], self.comparison.get(item["name"]).ending_balance)

    def test_spread_is_preserved(self):
        result = self.report.build(self.comparison)
        self.assertEqual(result["ending_balance_spread"], self.comparison.ending_balance_spread)

    def test_text_report_has_title(self):
        self.assertIn("RETIREMENT SCENARIO COMPARISON", self.report.render_text(self.comparison))

    def test_text_report_has_each_scenario(self):
        text = self.report.render_text(self.comparison)
        for name in ("conservative", "central", "optimistic"):
            self.assertIn(name, text)

    def test_text_report_contains_currency_values(self):
        text = self.report.render_text(self.comparison)
        self.assertIn("£", text)

    def test_text_report_does_not_recalculate_finances(self):
        before = self.comparison
        self.report.render_text(self.comparison)
        self.assertEqual(before, self.comparison)

    def test_year_rows_are_flattened(self):
        rows = self.report.year_rows(self.comparison)
        expected = sum(len(p.years) for p in self.comparison.projections)
        self.assertEqual(len(rows), expected)

    def test_year_rows_preserve_scenario(self):
        rows = self.report.year_rows(self.comparison)
        self.assertEqual({r["scenario"] for r in rows}, {"conservative", "central", "optimistic"})

    def test_year_rows_have_required_fields(self):
        row = self.report.year_rows(self.comparison)[0]
        self.assertEqual(
            set(row),
            {"scenario", "year", "starting_balance", "investment_growth", "withdrawals", "ending_balance"},
        )

    def test_year_rows_preserve_balance_values(self):
        rows = self.report.year_rows(self.comparison)
        source = self.comparison.get(rows[0]["scenario"]).years[0]
        self.assertEqual(rows[0]["starting_balance"], source.starting_balance)
        self.assertEqual(rows[0]["ending_balance"], source.ending_balance)

    def test_year_rows_preserve_order(self):
        rows = self.report.year_rows(self.comparison)
        names = [r["scenario"] for r in rows]
        self.assertEqual(names[: len(self.comparison.get("conservative").years)], ["conservative"] * len(self.comparison.get("conservative").years))

    def test_report_is_deterministic(self):
        self.assertEqual(self.report.build(self.comparison), self.report.build(self.comparison))
        self.assertEqual(self.report.render_text(self.comparison), self.report.render_text(self.comparison))

    def test_report_contains_existing_adapter_payload(self):
        result = self.report.build(self.comparison)
        for key in ("scenarios", "ending_balances", "highest_ending_balance", "lowest_ending_balance"):
            self.assertIn(key, result)

    def test_starting_pension_is_consistent(self):
        result = self.report.build(self.comparison)
        self.assertEqual({x["starting_pension"] for x in result["summary"]}, {self.comparison.get("central").starting_pension})


if __name__ == "__main__":
    unittest.main()

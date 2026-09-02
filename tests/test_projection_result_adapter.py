import unittest

from planner.assumptions import Assumptions
from planner.funds.portfolio_historical_statistics import PortfolioHistoricalStatisticsCalculator
from planner.projection.projection_result_adapter import ProjectionResultReportAdapter
from planner.projection.scenario_projection_comparison import ScenarioProjectionComparisonRunner


class ProjectionResultReportAdapterTests(unittest.TestCase):
    def setUp(self):
        assumptions = Assumptions()
        statistics = PortfolioHistoricalStatisticsCalculator().calculate(
            {"Aviva": 0.75, "Sky": 0.25},
            {"Aviva": [0.10, 0.02, 0.08], "Sky": [0.20, 0.04, 0.16]},
        )
        self.comparison = ScenarioProjectionComparisonRunner().run(
            assumptions=assumptions,
            statistics=statistics,
        )
        self.adapter = ProjectionResultReportAdapter()

    def test_rejects_wrong_input_type(self):
        with self.assertRaises(TypeError):
            self.adapter.build({})

    def test_scenario_names_are_exposed(self):
        report = self.adapter.build(self.comparison)
        self.assertEqual(
            report["scenario_names"],
            ["conservative", "central", "optimistic"],
        )

    def test_scenarios_are_exposed(self):
        report = self.adapter.build(self.comparison)
        self.assertEqual(len(report["scenarios"]), 3)

    def test_scenario_name_is_preserved(self):
        report = self.adapter.build(self.comparison)
        self.assertEqual(report["scenarios"][1]["name"], "central")

    def test_provenance_is_preserved(self):
        report = self.adapter.build(self.comparison)
        for scenario in report["scenarios"]:
            self.assertIn("fund-informed scenario:", scenario["source"])

    def test_starting_pension_is_preserved(self):
        report = self.adapter.build(self.comparison)
        values = {s["starting_pension"] for s in report["scenarios"]}
        self.assertEqual(values, {self.comparison.get("central").starting_pension})

    def test_annual_return_is_preserved(self):
        report = self.adapter.build(self.comparison)
        self.assertAlmostEqual(
            report["scenarios"][1]["annual_return"],
            self.comparison.get("central").annual_return,
        )

    def test_year_rows_are_exposed(self):
        report = self.adapter.build(self.comparison)
        central = report["scenarios"][1]
        self.assertEqual(len(central["years"]), len(self.comparison.get("central").years))

    def test_year_row_fields_are_exposed(self):
        report = self.adapter.build(self.comparison)
        row = report["scenarios"][1]["years"][0]
        self.assertEqual(
            set(row),
            {"year", "starting_balance", "investment_growth", "withdrawals", "ending_balance"},
        )

    def test_ending_balances_are_preserved(self):
        report = self.adapter.build(self.comparison)
        self.assertEqual(report["ending_balances"], dict(self.comparison.ending_balances))

    def test_highest_ending_balance_is_preserved(self):
        report = self.adapter.build(self.comparison)
        self.assertEqual(report["highest_ending_balance"], self.comparison.highest_ending_balance)

    def test_lowest_ending_balance_is_preserved(self):
        report = self.adapter.build(self.comparison)
        self.assertEqual(report["lowest_ending_balance"], self.comparison.lowest_ending_balance)

    def test_spread_is_preserved(self):
        report = self.adapter.build(self.comparison)
        self.assertEqual(report["ending_balance_spread"], self.comparison.ending_balance_spread)

    def test_total_growth_is_preserved(self):
        report = self.adapter.build(self.comparison)
        for scenario in report["scenarios"]:
            source = self.comparison.get(scenario["name"])
            self.assertEqual(scenario["total_investment_growth"], source.total_investment_growth)

    def test_total_withdrawals_are_preserved(self):
        report = self.adapter.build(self.comparison)
        for scenario in report["scenarios"]:
            source = self.comparison.get(scenario["name"])
            self.assertEqual(scenario["total_withdrawals"], source.total_withdrawals)

    def test_adapter_does_not_recalculate_finances(self):
        report = self.adapter.build(self.comparison)
        central = self.comparison.get("central")
        self.assertEqual(
            report["scenarios"][1]["ending_balance"],
            central.ending_balance,
        )

    def test_report_payload_is_independent_of_domain_mutation(self):
        report = self.adapter.build(self.comparison)
        report["scenario_names"].append("fake")
        report["scenarios"][0]["name"] = "fake"
        self.assertEqual(self.comparison.scenario_names, ("conservative", "central", "optimistic"))

    def test_payload_is_legacy_report_friendly(self):
        report = self.adapter.build(self.comparison)
        self.assertIsInstance(report, dict)
        self.assertIsInstance(report["scenarios"], list)
        self.assertIsInstance(report["ending_balances"], dict)


if __name__ == "__main__":
    unittest.main()

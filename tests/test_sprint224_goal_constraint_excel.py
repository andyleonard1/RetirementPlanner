import os
import tempfile
import unittest
from pathlib import Path

from openpyxl import load_workbook

from reports.excel_report import ExcelReport


class Sprint224GoalConstraintExcelTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.cwd = os.getcwd()
        os.chdir(self.tmp.name)

    def tearDown(self):
        os.chdir(self.cwd)
        self.tmp.cleanup()

    def _timeline(self):
        class Year:
            age = 63
            calendar_year = 2026
            opening_pension = 660000
            pension_growth = 0.04
            closing_pension = 650000
            gross_pension_income = 10000
            income_tax = 1000
            net_pension_income = 9000
            your_state_pension = 0
            spouse_state_pension = 0
            cash_available = 9000
            savings_closing = 70000
            isa_closing = 130000
            total_assets = 860000
        return [Year()]

    def _assumptions(self):
        class Assumptions:
            data = {"starting_pension": 660000}

            def get(self, key):
                return self.data[key]
        return Assumptions()

    def test_goal_constraints_sheet_presents_effective_operator(self):
        goals = [{"name": "Estate", "passed": True, "target": 500000, "actual": 860000, "operator": ">="}]
        ExcelReport().generate(self._timeline(), self._assumptions(), goals=goals)

        workbook = load_workbook("RetirementPlanner.xlsx", data_only=True)
        ws = workbook["Goals"]
        self.assertEqual([ws.cell(1, c).value for c in range(1, 6)],
                         ["Status", "Goal", "Constraint", "Target", "Actual"])
        self.assertEqual(ws.cell(2, 1).value, "[OK]")
        self.assertEqual(ws.cell(2, 3).value, ">= 500000")
        self.assertEqual(ws.cell(2, 4).value, 500000)
        self.assertEqual(ws.cell(2, 5).value, 860000)

    def test_all_custom_operators_are_rendered(self):
        operators = [">", "<", "<=", "==", "!="]
        goals = [
            {"name": op, "passed": False, "target": 10, "actual": 9, "operator": op}
            for op in operators
        ]
        ExcelReport().generate(self._timeline(), self._assumptions(), goals=goals)
        ws = load_workbook("RetirementPlanner.xlsx", data_only=True)["Goals"]
        values = [ws.cell(row, 3).value for row in range(2, 7)]
        self.assertEqual(values[:3], [f"{op} 10" for op in operators[:3]])
        self.assertEqual(values[3], "'== 10")
        self.assertEqual(values[4], "!= 10")

    def test_legacy_goal_result_without_operator_remains_compatible(self):
        goals = [{"name": "Legacy", "passed": True, "target": 10, "actual": 10}]
        ExcelReport().generate(self._timeline(), self._assumptions(), goals=goals)
        ws = load_workbook("RetirementPlanner.xlsx", data_only=True)["Goals"]
        self.assertEqual(ws.cell(2, 3).value, "10")

    def test_no_goals_preserves_existing_workbook_shape(self):
        ExcelReport().generate(self._timeline(), self._assumptions())
        workbook = load_workbook("RetirementPlanner.xlsx", data_only=True)
        self.assertNotIn("Goals", workbook.sheetnames)
        self.assertEqual(workbook.sheetnames, ["Summary", "Assumptions", "Cash Flow", "Tax", "Assets", "Charts"])

    def test_goal_export_does_not_mutate_source_results(self):
        goals = [{"name": "Estate", "passed": True, "target": 500000, "actual": 860000, "operator": ">="}]
        original = [dict(goals[0])]
        ExcelReport().generate(self._timeline(), self._assumptions(), goals=goals)
        self.assertEqual(goals, original)


if __name__ == "__main__":
    unittest.main()

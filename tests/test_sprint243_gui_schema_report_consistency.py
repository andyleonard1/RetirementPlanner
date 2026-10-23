import json
import shutil
import tempfile
import unittest
import os
from pathlib import Path

from openpyxl import load_workbook

from planner.assumptions import Assumptions
from planner.assumptions_schema import AssumptionsSchema
from planner.audit_catalog import description
from planner.gui.scenario_projection_application import ScenarioProjectionApplication
from planner.gui.scenario_projection_controller import ScenarioProjectionGuiController
from reports.excel_report import ExcelReport


class Sprint243GuiSchemaReportConsistencyTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        source = Path(__file__).resolve().parents[1] / "data" / "assumptions.json"
        target = Path(self.tempdir.name) / "assumptions.json"
        shutil.copy2(source, target)
        self.assumptions = Assumptions(str(target))
        self.application = ScenarioProjectionApplication(self.assumptions)
        self.controller = ScenarioProjectionGuiController(
            self.application,
            {"Aviva": 0.75, "Sky": 0.25},
            {"Aviva": (0.10, 0.02, 0.08), "Sky": (0.20, 0.04, 0.16)},
        )

    def tearDown(self):
        self.tempdir.cleanup()

    def test_gui_editor_accepts_every_schema_defined_top_level_key(self):
        document = json.loads(self.controller.assumptions_json())
        expected = (
            AssumptionsSchema.REQUIRED_KEYS
            | AssumptionsSchema.OPTIONAL_BOOLS
            | AssumptionsSchema.OPTIONAL_OBJECTS
        )
        self.assertTrue(expected <= set(document))
        self.controller.validate_assumptions_json(json.dumps(document))
        formatted = self.controller.format_assumptions_json(json.dumps(document))
        self.assertEqual(set(json.loads(formatted)), set(document))

    def test_gui_round_trip_preserves_nested_schema_values(self):
        document = json.loads(self.controller.assumptions_json())
        document["goals"][0]["target"] = 63
        document["annual_spending_schedule"] = {"2030": 41000, "2040": 33000}
        document["investment_return_schedule"] = {"2031": 0.05}
        document["isa_return_schedule"] = {"2032": 0.045}
        document["isa_allowance_schedule"] = {"2033/34": 45000}
        self.controller.apply_assumptions_json(json.dumps(document))
        self.assertEqual(self.application.assumptions.data, document)

    def test_excel_assumptions_report_contains_every_schema_key_and_description(self):
        timeline = self.application.build_view_model(
            allocations={"Aviva": 0.75, "Sky": 0.25},
            fund_returns={"Aviva": [0.10, 0.02, 0.08], "Sky": [0.20, 0.04, 0.16]},
        )
        # ExcelReport's established API expects timeline rows; use a minimal
        # deterministic projection timeline from the application's planner.
        result = self.application.run_report_workflow(
            allocations={"Aviva": 0.75, "Sky": 0.25},
            fund_returns={"Aviva": [0.10, 0.02, 0.08], "Sky": [0.20, 0.04, 0.16]},
            scenarios=("central",),
        )
        self.assertIsNotNone(timeline)
        # The workflow result exposes the underlying comparison timeline only
        # indirectly, so use a one-row shape compatible with ExcelReport.
        row = type("Row", (), {
            "age": 63, "calendar_year": 2027, "opening_pension": 100000.0,
            "pension_growth": 0.04, "closing_pension": 95000.0, "gross_pension_income": 35000.0,
            "income_tax": 5000.0, "net_pension_income": 30000.0,
            "your_state_pension": 0.0, "spouse_state_pension": 0.0,
            "cash_available": 30000.0, "savings_closing": 72500.0,
            "isa_closing": 126000.0, "total_assets": 298500.0,
        })()
        path = Path(self.tempdir.name) / "RetirementPlanner.xlsx"
        previous = os.getcwd()
        try:
            os.chdir(self.tempdir.name)
            ExcelReport().generate([row], self.assumptions)
        finally:
            os.chdir(previous)
        loaded = load_workbook(path, read_only=True, data_only=True)
        sheet = loaded["Assumptions"]
        rows = list(sheet.iter_rows(values_only=True))
        self.assertEqual(rows[0], ("Assumption", "Value", "Description"))
        actual = {r[0]: (r[1], r[2]) for r in rows[1:] if r[0] is not None}
        expected = set(AssumptionsSchema.REQUIRED_KEYS | AssumptionsSchema.OPTIONAL_BOOLS | AssumptionsSchema.OPTIONAL_OBJECTS)
        self.assertEqual(expected, set(actual))
        for key in expected:
            self.assertEqual(actual[key][1], description(key))
        self.assertIsInstance(actual["goals"][0], str)
        self.assertIsInstance(actual["annual_spending_schedule"][0], str)
        loaded.close()

    def test_excel_nested_assumptions_are_lossless_json(self):
        document = self.assumptions.data
        document["goals"][0]["target"] = 64
        document["annual_spending_schedule"] = {"2030": 41000}
        self.assumptions.validate()
        row = type("Row", (), {
            "age": 63, "calendar_year": 2027, "opening_pension": 100000.0,
            "pension_growth": 0.04, "closing_pension": 95000.0, "gross_pension_income": 35000.0,
            "income_tax": 5000.0, "net_pension_income": 30000.0,
            "your_state_pension": 0.0, "spouse_state_pension": 0.0,
            "cash_available": 30000.0, "savings_closing": 72500.0,
            "isa_closing": 126000.0, "total_assets": 298500.0,
        })()
        previous = os.getcwd()
        try:
            os.chdir(self.tempdir.name)
            ExcelReport().generate([row], self.assumptions)
        finally:
            os.chdir(previous)
        workbook = load_workbook(Path(self.tempdir.name) / "RetirementPlanner.xlsx", data_only=True)
        sheet = workbook["Assumptions"]
        values = {sheet.cell(r, 1).value: sheet.cell(r, 2).value for r in range(2, sheet.max_row + 1)}
        self.assertEqual(json.loads(values["goals"])[0]["target"], 64)
        self.assertEqual(json.loads(values["annual_spending_schedule"]), {"2030": 41000})


if __name__ == "__main__":
    unittest.main()

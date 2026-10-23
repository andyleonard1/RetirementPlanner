"""Sprint 251: executable GUI -> calculation -> report traceability guards."""
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from planner.assumptions import Assumptions
from planner.gui.scenario_projection_application import ScenarioProjectionApplication
from planner.gui.scenario_projection_controller import ScenarioProjectionGuiController
from planner.projection.scenario_projection_report import ScenarioProjectionReport


class Sprint251GuiEngineReportTraceabilityTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        source = Path(__file__).resolve().parents[1] / "data" / "assumptions.json"
        target = Path(self.tempdir.name) / "assumptions.json"
        shutil.copy2(source, target)
        self.assumptions = Assumptions(str(target))
        # Keep the integration run small and deterministic.
        self.assumptions.set("current_age", 65)
        self.assumptions.set("retirement_age", 65)
        self.assumptions.set("projection_end_age", 67)
        self.assumptions.set("starting_pension", 200000)
        self.application = ScenarioProjectionApplication(self.assumptions)
        self.controller = ScenarioProjectionGuiController(
            self.application,
            {"Fund A": 1.0},
            {"Fund A": (0.05, 0.04, 0.06)},
        )

    def tearDown(self):
        self.tempdir.cleanup()

    def run_workflow(self):
        return self.application.run_report_workflow(
            allocations={"Fund A": 1.0},
            fund_returns={"Fund A": (0.05, 0.04, 0.06)},
            scenarios=("central",),
        )

    def test_gui_json_edit_reaches_application_inputs(self):
        document = json.loads(self.controller.assumptions_json())
        document.update({"starting_pension": 234567, "retirement_age": 66, "projection_end_age": 67})
        self.controller.apply_assumptions_json(json.dumps(document))
        inputs = self.application.inputs()
        self.assertEqual(inputs.starting_pension, 234567.0)
        self.assertEqual(inputs.retirement_age, 66)
        self.assertEqual(inputs.projection_end_age, 67)

    def test_workflow_inputs_match_active_gui_assumptions(self):
        document = json.loads(self.controller.assumptions_json())
        document["starting_pension"] = 234567
        self.controller.apply_assumptions_json(json.dumps(document))
        result = self.run_workflow()
        self.assertEqual(result.inputs.starting_pension, 234567.0)
        self.assertEqual(result.inputs.retirement_age, self.assumptions.get("retirement_age"))
        self.assertEqual(result.inputs.projection_end_age, self.assumptions.get("projection_end_age"))

    def test_workflow_snapshot_is_report_source(self):
        result = self.run_workflow()
        report = ScenarioProjectionReport()
        self.assertEqual(result.report_payload, report.build_from_snapshot(result.snapshot))
        self.assertEqual(result.report_text, report.render_text_from_snapshot(result.snapshot))

    def test_report_text_and_payload_share_scenario_identity(self):
        result = self.run_workflow()
        self.assertIn("central", result.report_text.lower())
        self.assertTrue(result.report_payload)
        self.assertEqual([item["name"] for item in result.snapshot["payload"]["scenarios"]], [item["name"] for item in result.report_payload["scenarios"]])

    def test_nested_schedule_survives_gui_edit_and_is_active_in_engine_config(self):
        document = json.loads(self.controller.assumptions_json())
        document["annual_spending_schedule_enabled"] = True
        document["annual_spending_schedule"] = {"2030": 12345}
        self.controller.apply_assumptions_json(json.dumps(document))
        round_trip = json.loads(self.controller.assumptions_json())
        self.assertEqual(round_trip["annual_spending_schedule"], {"2030": 12345})
        self.assertTrue(round_trip["annual_spending_schedule_enabled"])

    def test_invalid_gui_edit_does_not_mutate_engine_assumptions(self):
        before = dict(self.assumptions.data)
        document = json.loads(self.controller.assumptions_json())
        document["starting_pension"] = float("nan")
        with self.assertRaises((ValueError, TypeError)):
            self.controller.apply_assumptions_json(json.dumps(document))
        self.assertEqual(self.assumptions.data, before)

    def test_report_snapshot_is_immutable_after_publication(self):
        result = self.run_workflow()
        with self.assertRaises((TypeError, AttributeError)):
            result.report_payload["traceability_probe"] = True

    def test_repeat_workflow_has_identical_published_report(self):
        first = self.run_workflow()
        second = self.run_workflow()
        self.assertEqual(first.snapshot, second.snapshot)
        self.assertEqual(first.report_payload, second.report_payload)
        self.assertEqual(first.report_text, second.report_text)


if __name__ == "__main__":
    unittest.main()

import tempfile
import unittest
from pathlib import Path

from planner.assumptions import Assumptions
from planner.gui.scenario_projection_application import (
    ScenarioProjectionApplication,
    ScenarioProjectionWorkflowResult,
)
from planner.projection.scenario_projection_report import ScenarioProjectionReport


ALLOCATIONS = {"Aviva": 0.75, "Sky": 0.25}
FUND_RETURNS = {
    "Aviva": (0.10, 0.02, 0.08),
    "Sky": (0.20, 0.04, 0.16),
}


class Sprint193WorkflowResultIntegrityTests(unittest.TestCase):
    def setUp(self):
        self._tempdir = tempfile.TemporaryDirectory()
        source = Path(__file__).resolve().parents[1] / "data" / "assumptions.json"
        target = Path(self._tempdir.name) / "assumptions.json"
        target.write_bytes(source.read_bytes())
        self.application = ScenarioProjectionApplication(Assumptions(str(target)))
        self.result = self.application.run_report_workflow(
            allocations=ALLOCATIONS,
            fund_returns=FUND_RETURNS,
            scenarios=("central", "optimistic"),
        )

    def tearDown(self):
        self._tempdir.cleanup()

    def test_report_payload_is_recursively_immutable(self):
        with self.assertRaises(TypeError):
            self.result.report_payload["lowest_ending_balance"] = 1
        with self.assertRaises(TypeError):
            self.result.report_payload["scenarios"][0]["name"] = "changed"
        with self.assertRaises(TypeError):
            self.result.report_payload["scenarios"].append({"name": "changed"})

    def test_workflow_result_rejects_payload_or_text_drift(self):
        report = ScenarioProjectionReport()
        with self.assertRaises(ValueError):
            ScenarioProjectionWorkflowResult(
                self.result.inputs,
                self.result.view_model,
                self.result.snapshot,
                {**report.build_from_snapshot(self.result.snapshot), "ending_balance_spread": -1},
                self.result.report_text,
            )
        with self.assertRaises(ValueError):
            ScenarioProjectionWorkflowResult(
                self.result.inputs,
                self.result.view_model,
                self.result.snapshot,
                report.build_from_snapshot(self.result.snapshot),
                self.result.report_text + "\nchanged",
            )

    def test_frozen_workflow_payload_matches_snapshot_on_repeated_access(self):
        report = ScenarioProjectionReport()
        first = report.build_from_snapshot(self.result.snapshot)
        second = report.build_from_snapshot(self.result.snapshot)
        self.assertEqual(self.result.report_payload, first)
        self.assertEqual(first, second)
        self.assertEqual(self.result.report_text, report.render_text_from_snapshot(self.result.snapshot))


if __name__ == "__main__":
    unittest.main()

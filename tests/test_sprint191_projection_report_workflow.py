import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from planner.assumptions import Assumptions
from planner.gui.scenario_projection_application import ScenarioProjectionApplication
from planner.projection.scenario_projection_report import ScenarioProjectionReport


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ALLOCATIONS = {"Aviva": 0.75, "Sky": 0.25}
DEFAULT_FUND_RETURNS = {
    "Aviva": [0.10, 0.02, 0.08],
    "Sky": [0.20, 0.04, 0.16],
}


class Sprint191ProjectionReportWorkflowTests(unittest.TestCase):
    def test_application_workflow_publishes_one_report_ready_result(self):
        application = ScenarioProjectionApplication(Assumptions())
        before = application.assumptions.changes()

        result = application.run_report_workflow(
            allocations=DEFAULT_ALLOCATIONS,
            fund_returns=DEFAULT_FUND_RETURNS,
            scenarios=("central", "optimistic"),
        )

        report = ScenarioProjectionReport()
        self.assertEqual(result.inputs.scenarios, ("central", "optimistic"))
        self.assertEqual(result.report_payload, report.build_from_snapshot(result.snapshot))
        self.assertEqual(result.report_text, report.render_text_from_snapshot(result.snapshot))
        self.assertEqual([item["name"] for item in result.report_payload["scenarios"]], ["central", "optimistic"])
        self.assertEqual(application.assumptions.changes(), before)

    def test_public_scenario_report_cli_exports_json_and_text_from_one_run(self):
        with tempfile.TemporaryDirectory() as directory:
            worktree = Path(directory) / "RetirementPlanner"
            shutil.copytree(PROJECT_ROOT, worktree)
            export_dir = worktree / "exports"

            completed = subprocess.run(
                [sys.executable, "scenario_report.py", "--export-dir", str(export_dir)],
                cwd=worktree,
                capture_output=True,
                text=True,
                timeout=60,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertIn("RETIREMENT SCENARIO COMPARISON", completed.stdout)
            json_path = export_dir / "retirement_projection.json"
            text_path = export_dir / "retirement_projection.txt"
            self.assertTrue(json_path.exists())
            self.assertTrue(text_path.exists())
            payload = json.loads(json_path.read_text(encoding="utf-8"))
            text = text_path.read_text(encoding="utf-8").rstrip("\n")
            self.assertEqual([item["name"] for item in payload["scenarios"]], ["conservative", "central", "optimistic"])
            self.assertEqual(text, completed.stdout.split("\n\nJSON report exported:", 1)[0])

    def test_public_scenario_report_cli_preserves_bundle_conflict_and_allows_explicit_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            worktree = Path(directory) / "RetirementPlanner"
            shutil.copytree(PROJECT_ROOT, worktree)
            export_dir = worktree / "exports"

            first = subprocess.run(
                [sys.executable, "scenario_report.py", "--export-dir", str(export_dir)],
                cwd=worktree,
                capture_output=True,
                text=True,
                timeout=60,
            )
            self.assertEqual(first.returncode, 0, first.stderr)

            blocked = subprocess.run(
                [sys.executable, "scenario_report.py", "--export-dir", str(export_dir)],
                cwd=worktree,
                capture_output=True,
                text=True,
                timeout=60,
            )
            self.assertNotEqual(blocked.returncode, 0)
            self.assertIn("export destination already exists", blocked.stderr)

            overwritten = subprocess.run(
                [
                    sys.executable,
                    "scenario_report.py",
                    "--export-dir",
                    str(export_dir),
                    "--overwrite",
                    "--export-stem",
                    "scenario_latest",
                ],
                cwd=worktree,
                capture_output=True,
                text=True,
                timeout=60,
            )
            self.assertEqual(overwritten.returncode, 0, overwritten.stderr)
            self.assertTrue((export_dir / "scenario_latest.json").exists())
            self.assertTrue((export_dir / "scenario_latest.txt").exists())


if __name__ == "__main__":
    unittest.main()

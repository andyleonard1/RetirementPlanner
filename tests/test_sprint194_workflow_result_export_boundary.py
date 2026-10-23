import json
import tempfile
import unittest
from pathlib import Path

from planner.assumptions import Assumptions
from planner.gui.scenario_projection_application import ScenarioProjectionApplication, ScenarioProjectionWorkflowResult


ALLOCATIONS = {"Aviva": 0.75, "Sky": 0.25}
FUND_RETURNS = {
    "Aviva": (0.10, 0.02, 0.08),
    "Sky": (0.20, 0.04, 0.16),
}


class Sprint194WorkflowResultExportBoundaryTests(unittest.TestCase):
    def setUp(self):
        source = Path(__file__).resolve().parents[1] / "data" / "assumptions.json"
        self._tempdir = tempfile.TemporaryDirectory()
        assumptions_path = Path(self._tempdir.name) / "assumptions.json"
        assumptions_path.write_bytes(source.read_bytes())
        application = ScenarioProjectionApplication(Assumptions(str(assumptions_path)))
        self.result = application.run_report_workflow(
            allocations=ALLOCATIONS,
            fund_returns=FUND_RETURNS,
            scenarios=("central", "optimistic"),
        )

    def tearDown(self):
        self._tempdir.cleanup()

    def test_workflow_result_exports_its_published_snapshot_directly(self):
        export_dir = Path(self._tempdir.name) / "exports"
        paths = self.result.export_bundle(export_dir, "published")
        payload = json.loads(paths["json"].read_text(encoding="utf-8"))
        self.assertEqual(payload, self.result.report_payload)
        self.assertEqual(paths["text"].read_text(encoding="utf-8").rstrip("\n"), self.result.report_text)

    def test_application_compatibility_export_delegates_to_result_boundary(self):
        application = object.__new__(ScenarioProjectionApplication)
        export_dir = Path(self._tempdir.name) / "delegated"
        paths = application.export_workflow_result(self.result, export_dir, "delegated")
        self.assertTrue(paths["json"].exists())
        self.assertTrue(paths["text"].exists())

    def test_result_export_preserves_conflict_and_explicit_overwrite_contract(self):
        export_dir = Path(self._tempdir.name) / "conflict"
        self.result.export_bundle(export_dir, "latest")
        with self.assertRaises(FileExistsError):
            self.result.export_bundle(export_dir, "latest")
        overwritten = self.result.export_bundle(export_dir, "latest", overwrite=True)
        self.assertEqual(overwritten["json"].read_text(encoding="utf-8").rstrip("\n"), json.dumps(self.result.report_payload, indent=2, ensure_ascii=False, allow_nan=False))


if __name__ == "__main__":
    unittest.main()

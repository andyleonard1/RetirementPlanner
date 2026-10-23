import tempfile
import unittest
from pathlib import Path
from unittest import mock

from planner.assumptions import Assumptions
from planner.projection.scenario_projection_workflow import ScenarioProjectionApplication
from planner.reporting.report_suite import (
    _publish_pdf_bundle,
    export_report_suite,
)


class Sprint204ReportSuitePublicationSafetyTests(unittest.TestCase):
    def _workflow_result(self):
        app = ScenarioProjectionApplication(Assumptions())
        return app.run_report_workflow(allocations={"Aviva": 1.0}, fund_returns={"Aviva": [0.05, 0.05, 0.05]})

    def test_default_export_rejects_any_existing_output_before_report_work(self):
        result = self._workflow_result()
        with tempfile.TemporaryDirectory() as directory:
            existing = Path(directory) / "retirement_health_check.pdf"
            existing.write_bytes(b"existing")
            with mock.patch("planner.reporting.report_suite.ScenarioProjectionPDFReport.create") as create:
                with self.assertRaises(FileExistsError):
                    export_report_suite(
                        assumptions=Assumptions(),
                        scenario_result=result,
                        allocations={"Aviva": 1.0},
                        fund_returns={"Aviva": [0.05, 0.05, 0.05]},
                        directory=directory,
                        monte_carlo_iterations=2,
                    )
            create.assert_not_called()
            self.assertEqual(existing.read_bytes(), b"existing")

    def test_overwrite_public_api_publishes_all_outputs(self):
        result = self._workflow_result()
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            for name in (
                "retirement_scenario_projection.pdf",
                "retirement_strategy_comparison.pdf",
                "retirement_recommendation.pdf",
                "retirement_health_check.pdf",
                "retirement_goals.pdf",
            ):
                (target / name).write_bytes(b"old")

            exported = export_report_suite(
                assumptions=Assumptions(),
                scenario_result=result,
                allocations={"Aviva": 1.0},
                fund_returns={"Aviva": [0.05, 0.05, 0.05]},
                directory=directory,
                monte_carlo_iterations=2,
                monte_carlo_seed=1,
                overwrite=True,
            )

            self.assertEqual(tuple(exported.paths), (
                "scenario_projection",
                "strategy_comparison",
                "recommendation",
                "health_check",
                "retirement_goals",
            ))
            for path in exported.paths.values():
                self.assertTrue(path.exists())
                self.assertGreater(path.stat().st_size, 1000)
            self.assertEqual(list(target.glob(".retirement-planner-report-suite-*")), [])

    def test_overwrite_rolls_back_when_second_publication_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            staging = Path(directory) / "staging"
            staging.mkdir()
            keys = ("scenario_projection", "strategy_comparison", "recommendation")
            staged = {key: staging / f"{key}.pdf" for key in keys}
            final = {key: Path(directory) / f"{key}.pdf" for key in keys}
            for path in staged.values():
                path.write_bytes((path.name + " new").encode())
            for key, path in final.items():
                path.write_bytes(f"old {key}".encode())

            original_replace = Path.replace
            calls = {"count": 0}

            def failing_replace(self, target):
                if self in staged.values():
                    calls["count"] += 1
                    if calls["count"] == 2:
                        raise OSError("simulated publish failure")
                return original_replace(self, target)

            with mock.patch.object(Path, "replace", new=failing_replace):
                with self.assertRaises(OSError):
                    _publish_pdf_bundle(staged, final, overwrite=True)

            for key, path in final.items():
                self.assertEqual(path.read_bytes(), f"old {key}".encode())
            self.assertTrue(all(not path.exists() for path in staged.values()))
            self.assertEqual(list(Path(directory).glob(".*.pdf.backup*")), [])


if __name__ == "__main__":
    unittest.main()

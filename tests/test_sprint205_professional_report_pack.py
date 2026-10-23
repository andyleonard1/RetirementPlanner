import tempfile
import unittest
from pathlib import Path

from pypdf import PdfReader

from planner.assumptions import Assumptions
from planner.projection.scenario_projection_workflow import ScenarioProjectionApplication
from planner.reporting.report_pack import export_report_pack
from planner.reporting.report_suite import ReportSuiteExportResult
from planner.reporting.report_suite import export_report_suite


class Sprint205ProfessionalReportPackTests(unittest.TestCase):
    def _suite(self, directory):
        workflow = ScenarioProjectionApplication(Assumptions()).run_report_workflow(
            allocations={"Aviva": 1.0},
            fund_returns={"Aviva": [0.05, 0.05, 0.05]},
        )
        return export_report_suite(
            assumptions=Assumptions(),
            scenario_result=workflow,
            allocations={"Aviva": 1.0},
            fund_returns={"Aviva": [0.05, 0.05, 0.05]},
            directory=directory,
            monte_carlo_iterations=2,
            monte_carlo_seed=1,
        )

    def test_pack_contains_cover_all_five_reports_and_bookmarks(self):
        with tempfile.TemporaryDirectory() as directory:
            suite = self._suite(directory)
            output = Path(directory) / "RetirementPlanner_Report_Pack.pdf"
            result = export_report_pack(suite, output)

            reader = PdfReader(result.path)
            expected_pages = 1 + sum(len(PdfReader(str(path)).pages) for path in suite.paths.values())
            self.assertEqual(len(reader.pages), expected_pages)
            outline = reader.outline
            titles = [item.title for item in outline if hasattr(item, "title")]
            self.assertEqual(
                titles,
                [
                    "Scenario Projection",
                    "Strategy Comparison",
                    "Recommendation",
                    "Health Check",
                    "Retirement Goals",
                ],
            )

    def test_pack_does_not_mutate_source_reports(self):
        with tempfile.TemporaryDirectory() as directory:
            suite = self._suite(directory)
            before = {key: path.read_bytes() for key, path in suite.paths.items()}
            output = Path(directory) / "RetirementPlanner_Report_Pack.pdf"
            export_report_pack(suite, output)
            after = {key: path.read_bytes() for key, path in suite.paths.items()}
            self.assertEqual(before, after)

    def test_pack_protects_existing_output_and_supports_explicit_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            suite = self._suite(directory)
            output = Path(directory) / "RetirementPlanner_Report_Pack.pdf"
            output.write_bytes(b"existing")
            with self.assertRaises(FileExistsError):
                export_report_pack(suite, output)
            self.assertEqual(output.read_bytes(), b"existing")

            result = export_report_pack(suite, output, overwrite=True)
            self.assertEqual(result.path, output)
            self.assertGreater(output.stat().st_size, 1000)
            self.assertFalse(output.with_name(f".{output.name}.tmp").exists())


if __name__ == "__main__":
    unittest.main()

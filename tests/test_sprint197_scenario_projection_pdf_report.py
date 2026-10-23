import tempfile
import unittest
from pathlib import Path

from pypdf import PdfReader

from planner.assumptions import Assumptions
from planner.projection import ScenarioProjectionApplication
from reports.scenario_projection_pdf_report import ScenarioProjectionPDFReport


ALLOCATIONS = {"Aviva": 0.75, "Sky": 0.25}
FUND_RETURNS = {
    "Aviva": [0.10, 0.02, 0.08],
    "Sky": [0.20, 0.04, 0.16],
}


class ScenarioProjectionPDFReportTests(unittest.TestCase):
    def setUp(self):
        self.result = ScenarioProjectionApplication(Assumptions()).run_report_workflow(
            allocations=ALLOCATIONS,
            fund_returns=FUND_RETURNS,
        )
        self.renderer = ScenarioProjectionPDFReport()

    def test_pdf_is_created_from_published_workflow_result(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "projection.pdf"
            returned = self.renderer.create(self.result, target)
            self.assertEqual(returned, target)
            self.assertGreater(target.stat().st_size, 1000)

    def test_pdf_contains_published_report_content(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "projection.pdf"
            self.renderer.create(self.result, target)
            text = "\n".join(page.extract_text() or "" for page in PdfReader(str(target)).pages)
            self.assertIn("RETIREMENT PLANNER", text)
            self.assertIn("Scenario Projection Report", text)
            self.assertIn("conservative", text)
            self.assertIn("central", text)
            self.assertIn("optimistic", text)
            self.assertIn("Scenario spread", text)
            self.assertIn(self.result.report_text.splitlines()[0], text)

    def test_pdf_renderer_rejects_non_workflow_result(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(TypeError):
                self.renderer.create(object(), Path(directory) / "projection.pdf")


if __name__ == "__main__":
    unittest.main()

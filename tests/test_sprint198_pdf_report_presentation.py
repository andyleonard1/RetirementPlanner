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


class ScenarioProjectionPDFReportPresentationTests(unittest.TestCase):
    def setUp(self):
        self.result = ScenarioProjectionApplication(Assumptions()).run_report_workflow(
            allocations=ALLOCATIONS,
            fund_returns=FUND_RETURNS,
        )
        self.renderer = ScenarioProjectionPDFReport()

    def _create(self):
        directory = tempfile.TemporaryDirectory()
        target = Path(directory.name) / "presentation.pdf"
        self.renderer.create(self.result, target)
        return directory, target, PdfReader(str(target))

    def test_pdf_adds_vector_trajectory_section_from_published_rows(self):
        directory, _, reader = self._create()
        try:
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
            self.assertIn("Projected Balance Trajectory", text)
            self.assertIn("Published ending balance by year", text)
            self.assertIn("conservative", text)
            self.assertIn("central", text)
            self.assertIn("optimistic", text)
            self.assertIn("Report provenance", text)
        finally:
            directory.cleanup()

    def test_pdf_has_page_chrome_on_every_page(self):
        directory, _, reader = self._create()
        try:
            self.assertGreaterEqual(len(reader.pages), 4)
            for number, page in enumerate(reader.pages, 1):
                text = page.extract_text() or ""
                self.assertIn("Retirement Planner — Scenario Projection Report", text)
                self.assertIn(f"Page {number}", text)
        finally:
            directory.cleanup()

    def test_year_table_header_repeats_when_projection_spans_pages(self):
        directory, _, reader = self._create()
        try:
            matching_pages = []
            for page in reader.pages:
                text = page.extract_text() or ""
                if all(column in text for column in ("Scenario", "Year", "Starting", "Growth", "Withdrawals", "Ending")):
                    matching_pages.append(page)
            self.assertGreaterEqual(len(matching_pages), 2)
            for page in matching_pages:
                text = page.extract_text() or ""
                self.assertIn("Scenario", text)
                self.assertIn("Year", text)
                self.assertIn("Ending", text)
        finally:
            directory.cleanup()


if __name__ == "__main__":
    unittest.main()

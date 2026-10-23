import unittest
from pathlib import Path


class Sprint245AssumptionBoundaryDocumentationTests(unittest.TestCase):
    ROOT = Path(__file__).resolve().parents[1]
    DOC = ROOT / "planner" / "docs" / "ASSUMPTION_BOUNDARY.md"
    ROADMAP = ROOT / "RC4_ROADMAP.md"
    STATUS = ROOT / "PROJECT_STATUS.md"

    def test_boundary_document_exists_and_covers_frozen_contract(self):
        text = self.DOC.read_text(encoding="utf-8")
        for phrase in (
            "Canonical boundary",
            "inflation_rate",
            "savings_interest_rate",
            "expected_investment_return",
            "expected_return",
            "expected_return`\n2. `expected_investment_return`\n3. `pension_growth",
            "canonical value wins",
        ):
            self.assertIn(phrase, text)

    def test_boundary_document_records_validation_and_change_protocol(self):
        text = self.DOC.read_text(encoding="utf-8")
        self.assertIn("reject booleans, non-numeric values and non-finite values", text)
        self.assertIn("Run the complete discovered suite", text)
        self.assertIn("Create a named ZIP checkpoint", text)

    def test_roadmap_records_sprint_245(self):
        text = self.ROADMAP.read_text(encoding="utf-8")
        self.assertIn("## Sprint 245 — Assumption Boundary Documentation and Release Traceability", text)
        self.assertIn("Current checkpoint: Sprint 245", text)

    def test_project_status_records_sprint_245(self):
        text = self.STATUS.read_text(encoding="utf-8")
        self.assertIn("Sprint 245 — Assumption Boundary Documentation and Release Traceability", text)
        self.assertIn("Current Sprint", text)
        self.assertIn("1224 tests", text)


if __name__ == "__main__":
    unittest.main()

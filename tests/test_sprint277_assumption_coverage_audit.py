import json
import tempfile
import unittest
from pathlib import Path

from scripts.audit_assumption_coverage import ROOT, build_report
from planner.assumptions_schema import AssumptionsSchema
from planner.assumption_usage_catalog import ROLES, schema_paths
from planner.audit_catalog import DESCRIPTIONS


class Sprint277AssumptionCoverageAuditTests(unittest.TestCase):
    def test_repository_assumptions_contract_has_no_static_coverage_gaps(self):
        report = build_report(ROOT)
        self.assertEqual("PASS", report["status"], report["issues"])
        self.assertEqual(0, len(report["issues"]))
        self.assertEqual(len(schema_paths()), report["counts"]["schema_paths"])
        self.assertTrue(report["gui_complete_json_editor_boundary"])

    def test_schema_paths_are_role_and_description_classified(self):
        schema = set(schema_paths())
        self.assertEqual(set(AssumptionsSchema.REQUIRED_KEYS | AssumptionsSchema.OPTIONAL_BOOLS | AssumptionsSchema.OPTIONAL_OBJECTS), schema)
        self.assertFalse(schema - set(ROLES))
        self.assertFalse(schema - set(DESCRIPTIONS))

    def test_report_scope_does_not_claim_financial_correctness(self):
        report = build_report(ROOT)
        self.assertIn("not financial correctness", report["scope"])


if __name__ == "__main__":
    unittest.main()

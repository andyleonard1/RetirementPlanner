"""Release-readiness documentation and repository-contract regressions."""
import json
from pathlib import Path
import tomllib
import unittest

ROOT = Path(__file__).resolve().parents[1]


class TestSprint253ReleaseReadiness(unittest.TestCase):
    def test_release_readiness_checklist_covers_required_release_gates(self):
        text = (ROOT / "planner" / "docs" / "RELEASE_READINESS.md").read_text(
            encoding="utf-8"
        )
        for required in (
            "Regression suite",
            "Compile check",
            "Golden scenario",
            "Financial boundary",
            "Configuration",
            "Entry points and reports",
            "Package integrity",
            "Traceability",
        ):
            with self.subTest(gate=required):
                self.assertIn(required, text)

    def test_release_checklist_explicitly_prohibits_unreviewed_calculation_changes(self):
        text = (ROOT / "planner" / "docs" / "RELEASE_READINESS.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("must not silently alter assumptions", text)
        self.assertIn("Do not modify the golden baseline", text)
        self.assertIn("does not perform a speculative source rewrite", text)

    def test_pyproject_has_supported_python_and_test_configuration(self):
        config = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        self.assertEqual(config["project"]["requires-python"], ">=3.13")
        self.assertEqual(config["tool"]["pytest"]["ini_options"]["testpaths"], ["tests"])
        self.assertEqual(config["tool"]["pytest"]["ini_options"]["python_files"], ["test_*.py"])

    def test_shipped_assumptions_file_remains_valid_json_object(self):
        assumptions = json.loads(
            (ROOT / "data" / "assumptions.json").read_text(encoding="utf-8")
        )
        self.assertIsInstance(assumptions, dict)
        self.assertTrue(assumptions)

    def test_readme_points_to_release_readiness_checklist(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("planner/docs/RELEASE_READINESS.md", readme)

    def test_sprint253_is_traceable_in_roadmap_and_project_status(self):
        roadmap = (ROOT / "RC4_ROADMAP.md").read_text(encoding="utf-8")
        status = (ROOT / "PROJECT_STATUS.md").read_text(encoding="utf-8")
        self.assertIn("Sprint 253", roadmap)
        self.assertIn("Sprint 253", status)

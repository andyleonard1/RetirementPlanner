import json
import shutil
import tempfile
import unittest
from pathlib import Path

from planner.assumptions import Assumptions
from planner.audit_catalog import description, has_description, schema_paths
from planner.gui.scenario_projection_application import ScenarioProjectionApplication
from planner.gui.scenario_projection_controller import ScenarioProjectionGuiController
from planner.assumptions_schema import AssumptionsSchema


class Sprint230AssumptionCatalogGuiCoverageTests(unittest.TestCase):
    """Prove the complete schema is represented by audit metadata and GUI JSON editing."""

    def setUp(self):
        self._tempdir = tempfile.TemporaryDirectory()
        source = Path(__file__).resolve().parents[1] / "data" / "assumptions.json"
        target = Path(self._tempdir.name) / "assumptions.json"
        shutil.copy2(source, target)
        self.path = target
        self.application = ScenarioProjectionApplication(Assumptions(str(target)))
        self.controller = ScenarioProjectionGuiController(
            self.application,
            {"Aviva": 0.75, "Sky": 0.25},
            {"Aviva": (0.10, 0.02, 0.08), "Sky": (0.20, 0.04, 0.16)},
        )

    def tearDown(self):
        self._tempdir.cleanup()

    def test_schema_paths_include_optional_assumption_fields(self):
        paths = set(schema_paths())
        expected = (
            AssumptionsSchema.REQUIRED_KEYS
            | AssumptionsSchema.OPTIONAL_BOOLS
            | AssumptionsSchema.OPTIONAL_OBJECTS
        )
        self.assertEqual(paths, expected)
        for path in expected:
            self.assertTrue(has_description(path), path)
            self.assertTrue(description(path), path)

    def test_actual_assumptions_document_has_catalog_description_for_every_top_level_key(self):
        document = json.loads(self.path.read_text(encoding="utf-8"))
        for key in document:
            self.assertTrue(has_description(key), key)

    def test_gui_complete_document_round_trip_preserves_every_assumption_key(self):
        document = json.loads(self.controller.assumptions_json())
        document["annual_spending_schedule_enabled"] = True
        document["annual_spending_schedule"] = {"2030": 41000, "2040": 33000}
        document["investment_return_schedule_enabled"] = True
        document["investment_return_schedule"] = {"2031": 0.05}
        document["isa_return_schedule_enabled"] = True
        document["isa_return_schedule"] = {"2032": 0.045}
        document["isa_allowance_schedule_enabled"] = True
        document["isa_allowance_schedule"] = {"2033/34": 45000}

        self.controller.apply_assumptions_json(json.dumps(document))
        self.controller.save()
        self.controller.reload_saved()

        persisted = json.loads(self.path.read_text(encoding="utf-8"))
        self.assertEqual(persisted, document)
        self.assertEqual(set(persisted), set(document))


if __name__ == "__main__":
    unittest.main()

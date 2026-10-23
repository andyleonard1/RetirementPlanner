import json
import math
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from planner.assumptions import Assumptions
from planner.assumptions_schema import AssumptionsSchema


class TestAssumptionsSchema(unittest.TestCase):

    def setUp(self):
        self.data = json.loads(Path("data/assumptions.json").read_text())

    def test_current_configuration_matches_schema(self):
        AssumptionsSchema.validate(self.data)

    def test_missing_required_key_is_rejected(self):
        self.data.pop("starting_pension")
        with self.assertRaisesRegex(ValueError, "Missing required assumptions: starting_pension"):
            AssumptionsSchema.validate(self.data)

    def test_numeric_type_is_rejected(self):
        self.data["starting_pension"] = "660000"
        with self.assertRaisesRegex(ValueError, "starting_pension must be a finite number"):
            AssumptionsSchema.validate(self.data)

    def test_non_finite_number_is_rejected(self):
        self.data["starting_pension"] = math.nan
        with self.assertRaisesRegex(ValueError, "starting_pension must be a finite number"):
            AssumptionsSchema.validate(self.data)

    def test_boolean_type_is_rejected(self):
        self.data["inflation_link_spending"] = 1
        with self.assertRaisesRegex(ValueError, "inflation_link_spending must be a boolean"):
            AssumptionsSchema.validate(self.data)

    def test_goals_structure_is_rejected(self):
        self.data["goals"] = [{"name": "Bad goal"}]
        with self.assertRaisesRegex(ValueError, r"goals\[0\]\.type must be a non-empty string"):
            AssumptionsSchema.validate(self.data)

    def test_unknown_keys_are_retained_with_warning(self):
        self.data["future_setting"] = 123
        with patch("planner.assumptions_schema.logger.warning") as warning:
            AssumptionsSchema.validate(self.data)
        warning.assert_called_once()

    def test_assumptions_load_uses_schema_before_domain_validation(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "assumptions.json"
            data = dict(self.data)
            data.pop("current_age")
            path.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError, "Missing required assumptions: current_age"):
                Assumptions(str(path))


if __name__ == "__main__":
    unittest.main()

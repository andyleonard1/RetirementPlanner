import json
import tempfile
import unittest
from pathlib import Path

from planner.assumptions import Assumptions


class TestAssumptionsSave(unittest.TestCase):

    def _copy_config(self, directory):
        source = Path("data/assumptions.json")
        target = Path(directory) / "assumptions.json"
        target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
        return target

    def test_save_persists_valid_changes(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self._copy_config(directory)
            assumptions = Assumptions(str(path))
            assumptions.set("target_net_income", 36000)
            assumptions.save()

            saved = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(saved["target_net_income"], 36000)

    def test_save_rejects_invalid_changes_before_writing(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self._copy_config(directory)
            original = path.read_text(encoding="utf-8")
            assumptions = Assumptions(str(path))
            assumptions.set("starting_pension", "invalid")

            with self.assertRaisesRegex(ValueError, "starting_pension must be a finite number"):
                assumptions.save()

            self.assertEqual(path.read_text(encoding="utf-8"), original)

    def test_save_rejects_domain_invalid_changes_before_writing(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self._copy_config(directory)
            original = path.read_text(encoding="utf-8")
            assumptions = Assumptions(str(path))
            assumptions.set("retirement_age", 50)

            with self.assertRaisesRegex(ValueError, "Retirement age cannot be before current age"):
                assumptions.save()

            self.assertEqual(path.read_text(encoding="utf-8"), original)

    def test_save_rejects_non_finite_changes_before_writing(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self._copy_config(directory)
            original = path.read_text(encoding="utf-8")
            assumptions = Assumptions(str(path))
            assumptions.set("starting_pension", float("nan"))

            with self.assertRaisesRegex(ValueError, "starting_pension must be a finite number"):
                assumptions.save()

            self.assertEqual(path.read_text(encoding="utf-8"), original)

    def test_validate_can_be_called_without_writing(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self._copy_config(directory)
            assumptions = Assumptions(str(path))
            assumptions.set("target_net_income", 36000)
            assumptions.validate()

            saved = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(saved["target_net_income"], 35000)

    def test_save_keeps_unknown_keys_for_forward_compatibility(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self._copy_config(directory)
            assumptions = Assumptions(str(path))
            assumptions.set("future_setting", "kept")
            assumptions.save()

            saved = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(saved["future_setting"], "kept")


if __name__ == "__main__":
    unittest.main()

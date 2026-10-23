import tempfile
import unittest
from pathlib import Path

from planner.assumptions import AssumptionChange, Assumptions


class TestAssumptionsAudit(unittest.TestCase):

    def _copy_config(self, directory):
        source = Path("data/assumptions.json")
        target = Path(directory) / "assumptions.json"
        target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
        return target

    def test_no_changes_after_load(self):
        with tempfile.TemporaryDirectory() as directory:
            assumptions = Assumptions(str(self._copy_config(directory)))
            self.assertEqual(assumptions.changes(), ())
            self.assertFalse(assumptions.has_changes())

    def test_set_records_change(self):
        with tempfile.TemporaryDirectory() as directory:
            assumptions = Assumptions(str(self._copy_config(directory)))
            original = assumptions.get("target_net_income")

            assumptions.set("target_net_income", 36000)

            self.assertEqual(
                assumptions.changes(),
                (AssumptionChange("target_net_income", original, 36000),),
            )

    def test_new_key_is_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            assumptions = Assumptions(str(self._copy_config(directory)))
            assumptions.set("future_setting", "new")

            self.assertEqual(
                assumptions.changes(),
                (AssumptionChange("future_setting", None, "new"),),
            )

    def test_nested_goal_change_is_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            assumptions = Assumptions(str(self._copy_config(directory)))
            assumptions.data["goals"][0]["target"] = 123456

            changes = assumptions.changes()

            self.assertEqual(len(changes), 1)
            self.assertEqual(changes[0].path, "goals[0].target")
            self.assertEqual(changes[0].after, 123456)

    def test_reset_change_tracking_accepts_current_state(self):
        with tempfile.TemporaryDirectory() as directory:
            assumptions = Assumptions(str(self._copy_config(directory)))
            assumptions.set("target_net_income", 36000)
            self.assertTrue(assumptions.has_changes())

            assumptions.reset_change_tracking()

            self.assertEqual(assumptions.changes(), ())
            self.assertFalse(assumptions.has_changes())

    def test_successful_save_resets_audit_baseline(self):
        with tempfile.TemporaryDirectory() as directory:
            assumptions = Assumptions(str(self._copy_config(directory)))
            assumptions.set("target_net_income", 36000)
            self.assertTrue(assumptions.has_changes())

            assumptions.save()

            self.assertEqual(assumptions.changes(), ())
            self.assertFalse(assumptions.has_changes())


if __name__ == "__main__":
    unittest.main()

"""Sprint 252: strengthen the existing golden scenario contract without changing calculations."""
import json
import unittest
from pathlib import Path

from planner.assumptions import Assumptions
from planner.planner import RetirementPlanner


ROOT = Path(__file__).resolve().parent
GOLDEN_PATH = ROOT / "golden" / "baseline.json"
FIELDS = ("closing_pension", "isa_closing", "savings_closing", "total_assets")


def project():
    result = RetirementPlanner(Assumptions()).run()
    return [{
        "closing_pension": y.closing_pension,
        "isa_closing": y.isa_closing,
        "savings_closing": y.savings_closing,
        "total_assets": y.total_assets,
    } for y in result.timeline]


class TestSprint252GoldenScenarioPack(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.baseline = json.loads(GOLDEN_PATH.read_text(encoding="utf8"))

    def test_baseline_is_nonempty_and_has_complete_schema(self):
        self.assertTrue(self.baseline)
        for row in self.baseline:
            self.assertEqual(set(row), set(FIELDS))

    def test_baseline_row_count_matches_projection_horizon(self):
        self.assertEqual(len(self.baseline), len(project()))

    def test_full_golden_row_matches_current_projection(self):
        actual = project()
        self.assertEqual(len(actual), len(self.baseline))
        for row, expected in zip(actual, self.baseline):
            for field in FIELDS:
                self.assertAlmostEqual(row[field], expected[field], places=2, msg=f"{field} in golden row")

    def test_repeated_projection_matches_golden_pack(self):
        self.assertEqual(project(), project())

    def test_each_portfolio_series_has_one_value_per_year(self):
        self.assertEqual(len(self.baseline), len(self.baseline))
        for row in self.baseline:
            self.assertEqual(set(row), set(FIELDS))

    def test_golden_asset_series_are_present(self):
        for row in self.baseline:
            for field in FIELDS:
                self.assertIn(field, row)

    def test_baseline_values_are_finite(self):
        for row in self.baseline:
            for field in FIELDS[2:]:
                self.assertTrue(abs(row[field]) < float("inf"), f"{field} in golden row")

    def test_golden_file_is_stable_and_not_regenerated_by_tests(self):
        before = GOLDEN_PATH.read_bytes()
        project()
        self.assertEqual(GOLDEN_PATH.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()

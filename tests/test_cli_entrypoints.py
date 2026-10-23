import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class TestCliEntrypoints(unittest.TestCase):
    """Exercise the public command-line entry points end to end."""

    def _run_in_clean_copy(self, script, check=None, timeout=60):
        with tempfile.TemporaryDirectory() as directory:
            worktree = Path(directory) / "RetirementPlanner"
            shutil.copytree(PROJECT_ROOT, worktree)

            completed = subprocess.run(
                [sys.executable, script],
                cwd=worktree,
                capture_output=True,
                text=True,
                timeout=timeout,
            )

            if check is not None:
                check(completed, worktree)

            return completed

    def test_main_cli_completes_successfully(self):
        completed = self._run_in_clean_copy("main.py")

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("Recommended retirement age", completed.stdout)

    def test_recommend_cli_completes_successfully(self):
        completed = self._run_in_clean_copy("recommend.py")

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("Recommended Strategy", completed.stdout)
        self.assertIn("Retirement Risk", completed.stdout)

    def test_health_check_cli_completes_successfully(self):
        completed = self._run_in_clean_copy("health_check.py", timeout=180)

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("Recommendation confidence", completed.stdout)
        self.assertIn("Key strengths", completed.stdout)

    def test_create_report_cli_creates_pdf(self):
        def check(completed, worktree):
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertIn("PDF created", completed.stdout)

            pdf = worktree / "RetirementReport.pdf"
            self.assertTrue(pdf.exists())
            self.assertGreater(pdf.stat().st_size, 1000)

        self._run_in_clean_copy("create_report.py", check=check)

    def test_compare_cli_completes_successfully_and_reports_both_strategies(self):
        completed = self._run_in_clean_copy("compare.py")

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("RETIREMENT STRATEGY COMPARISON", completed.stdout)
        self.assertIn("PENSION_FIRST", completed.stdout)
        self.assertIn("ISA_FIRST", completed.stdout)

    def test_compare_cli_emits_expected_report_columns(self):
        completed = self._run_in_clean_copy("compare.py")

        self.assertEqual(completed.returncode, 0, completed.stderr)
        header = next(
            line
            for line in completed.stdout.splitlines()
            if line.strip().startswith("Strategy")
        )
        for column in ("Assets", "Pension", "ISA", "Tax"):
            self.assertIn(column, header)

    def test_main_cli_accepts_custom_assumptions_file(self):
        with tempfile.TemporaryDirectory() as directory:
            worktree = Path(directory) / "RetirementPlanner"
            shutil.copytree(PROJECT_ROOT, worktree)
            custom = worktree / "custom-assumptions.json"
            data = (worktree / "data" / "assumptions.json").read_text(encoding="utf-8")
            custom.write_text(data, encoding="utf-8")

            completed = subprocess.run(
                [sys.executable, "main.py", "--assumptions", str(custom)],
                cwd=worktree,
                capture_output=True,
                text=True,
                timeout=60,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertIn("Recommended retirement age", completed.stdout)

    def test_compare_cli_uses_custom_assumptions_file(self):
        with tempfile.TemporaryDirectory() as directory:
            worktree = Path(directory) / "RetirementPlanner"
            shutil.copytree(PROJECT_ROOT, worktree)
            custom = worktree / "custom-assumptions.json"
            data = (worktree / "data" / "assumptions.json").read_text(encoding="utf-8")
            custom.write_text(data, encoding="utf-8")

            completed = subprocess.run(
                [sys.executable, "compare.py", "--assumptions", str(custom)],
                cwd=worktree,
                capture_output=True,
                text=True,
                timeout=60,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertIn("PENSION_FIRST", completed.stdout)
            self.assertIn("ISA_FIRST", completed.stdout)

    def test_scenario_engine_preserves_supplied_assumptions_before_changes(self):
        from planner.assumptions import Assumptions
        from planner.scenario_engine import ScenarioEngine

        assumptions = Assumptions()
        original_age = assumptions.get("retirement_age")
        assumptions.set("retirement_age", original_age + 1)

        result = ScenarioEngine(assumptions=assumptions).run("custom")

        retirement_rows = [row for row in result.timeline if row.age == original_age + 1]
        self.assertTrue(retirement_rows)


if __name__ == "__main__":
    unittest.main()

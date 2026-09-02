import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class TestCliEntrypoints(unittest.TestCase):
    """Exercise the public command-line entry points end to end."""

    def _run_in_clean_copy(self, script, check=None):
        with tempfile.TemporaryDirectory() as directory:
            worktree = Path(directory) / "RetirementPlanner"
            shutil.copytree(PROJECT_ROOT, worktree)

            completed = subprocess.run(
                [sys.executable, script],
                cwd=worktree,
                capture_output=True,
                text=True,
                timeout=60,
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
        completed = self._run_in_clean_copy("health_check.py")

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


if __name__ == "__main__":
    unittest.main()

"""Run the repeatable, non-destructive RC4 release acceptance gates.

Run from the repository root with:
    python scripts/release_acceptance.py

The command deliberately does not rewrite assumptions or regenerate golden data.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Sequence

ROOT = Path(__file__).resolve().parents[1]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="skip pytest (useful when only running static/configuration gates)",
    )
    parser.add_argument(
        "--skip-compile",
        action="store_true",
        help="skip compileall",
    )
    parser.add_argument(
        "--partition",
        type=int,
        help="run one 1-based partition of collected pytest items (requires --partitions)",
    )
    parser.add_argument(
        "--partitions",
        type=int,
        help="number of balanced pytest partitions to divide the suite into",
    )
    parser.add_argument(
        "--pytest-arg",
        action="append",
        default=[],
        metavar="ARG",
        help="pass one additional argument to pytest; repeat as needed",
    )
    return parser


def partition_items(items: Sequence[str], partition: int, partitions: int) -> list[str]:
    """Return a deterministic, round-robin partition of collected pytest node IDs."""
    if partitions < 1:
        raise ValueError("partitions must be at least 1")
    if partition < 1 or partition > partitions:
        raise ValueError("partition must be between 1 and partitions")
    return list(items[partition - 1 :: partitions])


def collect_pytest_items() -> list[str]:
    """Collect node IDs using pytest's own collector, preserving its item order."""
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(result.stdout, end="")
        print(result.stderr, end="", file=sys.stderr)
        raise RuntimeError(f"pytest collection failed with exit code {result.returncode}")
    return [line.strip() for line in result.stdout.splitlines()
            if line.startswith("tests/") and "::" in line]


def run_gate(label: str, command: Sequence[str]) -> bool:
    print(f"\n== {label} ==", flush=True)
    print("$ " + " ".join(command), flush=True)
    result = subprocess.run(command, cwd=ROOT, check=False)
    status = result.returncode == 0
    print(f"{label}: {'PASS' if status else 'FAIL (exit ' + str(result.returncode) + ')'}", flush=True)
    return status


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    failures: list[str] = []
    if (args.partition is None) != (args.partitions is None):
        print("Use --partition and --partitions together", file=sys.stderr)
        return 2
    if args.partitions is not None and args.partitions < 1:
        print("--partitions must be at least 1", file=sys.stderr)
        return 2
    if args.partition is not None and (
        args.partition < 1 or args.partition > args.partitions
    ):
        print("--partition must be between 1 and --partitions", file=sys.stderr)
        return 2

    assumptions = ROOT / "data" / "assumptions.json"
    try:
        with assumptions.open(encoding="utf-8") as stream:
            json.load(stream)
        print("Assumptions JSON: PASS (parse only; file not modified)", flush=True)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Assumptions JSON: FAIL ({exc})", flush=True)
        failures.append("Assumptions JSON")

    if not args.skip_compile:
        if not run_gate("Compile check", [sys.executable, "-m", "compileall", "-q", "."]):
            failures.append("Compile check")

    if not args.skip_tests:
        command = [sys.executable, "-m", "pytest", "-q", *args.pytest_arg]
        if args.partition is not None:
            try:
                items = collect_pytest_items()
                selected = partition_items(items, args.partition, args.partitions)
            except (RuntimeError, ValueError) as exc:
                print(f"Pytest partition setup: FAIL ({exc})", flush=True)
                failures.append("Pytest partition setup")
                selected = []
            if selected:
                print(
                    f"Running partition {args.partition}/{args.partitions}: "
                    f"{len(selected)} of {len(items)} collected tests",
                    flush=True,
                )
                command.extend(selected)
            elif "Pytest partition setup" not in failures:
                print("Pytest partition is empty; check the partition count", flush=True)
                failures.append("Pytest partition setup")
        if "Pytest partition setup" not in failures and not run_gate("Pytest suite", command):
            failures.append("Pytest suite")

    print("\n== Acceptance summary ==", flush=True)
    if failures:
        print("FAILED: " + ", ".join(failures), flush=True)
        return 1
    print("PASS: all requested acceptance gates completed successfully", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

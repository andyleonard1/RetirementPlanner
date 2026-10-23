"""Create and compare reproducible pytest collection fingerprints.

Examples from the repository root:
    python scripts/test_collection_report.py --output collection.json
    python scripts/test_collection_report.py --compare other-machine-collection.json

This diagnostic does not run tests, alter application data, or modify project files
unless --output is explicitly supplied.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import re
import subprocess
import sys
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_node_ids(output: str) -> list[str]:
    """Extract collected test node IDs from pytest's quiet collection output."""
    node_ids = [line.strip() for line in output.splitlines()
                if line.strip().startswith("tests/") and "::" in line]
    # Pytest node IDs should be unique; preserve order while guarding against
    # accidental duplicate lines from wrappers or captured output.
    return list(dict.fromkeys(node_ids))


def collect_node_ids(root: Path = ROOT) -> list[str]:
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q"],
        cwd=root, capture_output=True, text=True, check=False,
    )
    if result.returncode:
        raise RuntimeError(
            "pytest collection failed with exit code " + str(result.returncode)
            + "\n" + result.stdout + "\n" + result.stderr
        )
    node_ids = parse_node_ids(result.stdout)
    if not node_ids:
        raise RuntimeError("pytest collection returned no test node IDs")
    return node_ids


def build_report(root: Path = ROOT, node_ids: Iterable[str] | None = None) -> dict[str, Any]:
    root = root.resolve()
    ids = list(node_ids) if node_ids is not None else collect_node_ids(root)
    test_files = sorted({node_id.split("::", 1)[0] for node_id in ids})
    file_hashes = {
        relative: sha256_file(root / relative)
        for relative in test_files if (root / relative).is_file()
    }
    config_candidates = ["pyproject.toml", "pytest.ini", "setup.cfg", "tox.ini", "conftest.py"]
    config_hashes = {
        relative: sha256_file(root / relative)
        for relative in config_candidates if (root / relative).is_file()
    }
    counts: dict[str, int] = {}
    for node_id in ids:
        test_file = node_id.split("::", 1)[0]
        counts[test_file] = counts.get(test_file, 0) + 1
    try:
        pytest_version = version("pytest")
    except PackageNotFoundError:
        pytest_version = "unknown"
    return {
        "report_format": "retirement-planner-pytest-collection",
        "report_version": 1,
        "python_version": platform.python_version(),
        "python_implementation": platform.python_implementation(),
        "pytest_version": pytest_version,
        "root_name": root.name,
        "total_collected": len(ids),
        "test_file_count": len(counts),
        "config_sha256": config_hashes,
        "test_file_sha256": file_hashes,
        "counts_by_file": dict(sorted(counts.items())),
        "node_ids": ids,
    }



def validate_report(report: dict[str, Any]) -> list[str]:
    """Return structural integrity errors for a collection report."""
    errors: list[str] = []
    if report.get("report_format") != "retirement-planner-pytest-collection":
        errors.append("unsupported or missing report_format")
    if report.get("report_version") != 1:
        errors.append("unsupported or missing report_version")
    node_ids = report.get("node_ids")
    if not isinstance(node_ids, list) or any(
        not isinstance(node_id, str) or not node_id.startswith("tests/") or "::" not in node_id
        for node_id in (node_ids if isinstance(node_ids, list) else [])
    ):
        errors.append("node_ids must be a list of pytest test node-ID strings")
        node_ids = []
    elif len(node_ids) != len(set(node_ids)):
        errors.append("node_ids contains duplicates")
    if report.get("total_collected") != len(node_ids):
        errors.append("total_collected does not match node_ids length")
    expected_counts: dict[str, int] = {}
    for node_id in node_ids:
        file_name = node_id.split("::", 1)[0]
        expected_counts[file_name] = expected_counts.get(file_name, 0) + 1
    if report.get("counts_by_file") != dict(sorted(expected_counts.items())):
        errors.append("counts_by_file does not match node_ids")
    if report.get("test_file_count") != len(expected_counts):
        errors.append("test_file_count does not match node_ids")
    for field in ("test_file_sha256", "config_sha256"):
        hashes = report.get(field)
        if not isinstance(hashes, dict):
            errors.append(f"{field} must be an object")
            continue
        for path, digest in hashes.items():
            if not isinstance(path, str) or not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
                errors.append(f"{field} contains an invalid SHA-256 entry: {path!r}")
                break
    return errors

def compare_reports(current: dict[str, Any], other: dict[str, Any]) -> dict[str, Any]:
    current_ids = set(current.get("node_ids", []))
    other_ids = set(other.get("node_ids", []))
    current_hashes = current.get("test_file_sha256", {})
    other_hashes = other.get("test_file_sha256", {})
    common_files = set(current_hashes) & set(other_hashes)
    return {
        "current_total": len(current_ids),
        "other_total": len(other_ids),
        "only_current_count": len(current_ids - other_ids),
        "only_other_count": len(other_ids - current_ids),
        "only_current": sorted(current_ids - other_ids),
        "only_other": sorted(other_ids - current_ids),
        "files_only_current": sorted(set(current_hashes) - set(other_hashes)),
        "files_only_other": sorted(set(other_hashes) - set(current_hashes)),
        "files_with_different_hashes": sorted(
            path for path in common_files if current_hashes[path] != other_hashes[path]
        ),
        "config_hashes_differ": current.get("config_sha256", {}) != other.get("config_sha256", {}),
        "python_versions": [current.get("python_version"), other.get("python_version")],
        "pytest_versions": [current.get("pytest_version"), other.get("pytest_version")],
    }


def comparison_is_clean(comparison: dict[str, Any]) -> bool:
    """Return True only when node IDs, test files, and source hashes all match."""
    return (
        comparison.get("only_current_count") == 0
        and comparison.get("only_other_count") == 0
        and not comparison.get("files_only_current")
        and not comparison.get("files_only_other")
        and not comparison.get("files_with_different_hashes")
        and comparison.get("config_hashes_differ") is False
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="write the current collection report to this JSON path")
    parser.add_argument("--compare", type=Path, help="compare the current collection with another report JSON")
    args = parser.parse_args(argv)
    try:
        report = build_report()
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        if args.compare:
            other = json.loads(args.compare.read_text(encoding="utf-8"))
            errors = validate_report(report) + [
                "comparison report: " + error for error in validate_report(other)
            ]
            if errors:
                print(json.dumps({"validation_errors": errors}, indent=2), file=sys.stderr)
                return 2
            comparison = compare_reports(report, other)
            print(json.dumps(comparison, indent=2))
            return 0 if comparison_is_clean(comparison) else 1
        print(json.dumps(report, indent=2))
        return 0
    except (OSError, json.JSONDecodeError, RuntimeError) as exc:
        print(f"collection report failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

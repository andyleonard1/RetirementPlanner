"""Sprint 263 validation for cross-environment collection reports."""
from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "test_collection_report.py"
spec = importlib.util.spec_from_file_location("rc4_collection_report_sprint263", SCRIPT)
assert spec is not None and spec.loader is not None
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def valid_report() -> dict:
    return {
        "report_format": "retirement-planner-pytest-collection",
        "report_version": 1,
        "total_collected": 2,
        "test_file_count": 1,
        "node_ids": ["tests/test_a.py::test_one", "tests/test_a.py::test_two"],
        "counts_by_file": {"tests/test_a.py": 2},
        "test_file_sha256": {"tests/test_a.py": "a" * 64},
        "config_sha256": {"pyproject.toml": "b" * 64},
    }


def test_valid_collection_report_passes_validation() -> None:
    assert module.validate_report(valid_report()) == []


def test_wrong_report_format_is_rejected() -> None:
    report = valid_report()
    report["report_format"] = "other"
    assert "unsupported or missing report_format" in module.validate_report(report)


def test_wrong_report_version_is_rejected() -> None:
    report = valid_report()
    report["report_version"] = 2
    assert "unsupported or missing report_version" in module.validate_report(report)


def test_total_must_match_node_ids() -> None:
    report = valid_report()
    report["total_collected"] = 3
    assert "total_collected does not match node_ids length" in module.validate_report(report)


def test_duplicate_node_ids_are_rejected() -> None:
    report = valid_report()
    report["node_ids"].append(report["node_ids"][0])
    assert "node_ids contains duplicates" in module.validate_report(report)


def test_counts_by_file_must_match_node_ids() -> None:
    report = valid_report()
    report["counts_by_file"] = {"tests/test_a.py": 1}
    assert "counts_by_file does not match node_ids" in module.validate_report(report)


def test_test_file_count_must_match_node_ids() -> None:
    report = valid_report()
    report["test_file_count"] = 4
    assert "test_file_count does not match node_ids" in module.validate_report(report)


def test_malformed_node_id_is_rejected() -> None:
    report = valid_report()
    report["node_ids"] = ["not-a-node-id"]
    errors = module.validate_report(report)
    assert "node_ids must be a list of pytest test node-ID strings" in errors


def test_invalid_sha256_digest_is_rejected() -> None:
    report = valid_report()
    report["test_file_sha256"]["tests/test_a.py"] = "not-a-hash"
    assert any("invalid SHA-256" in error for error in module.validate_report(report))


def test_missing_hash_map_is_rejected() -> None:
    report = valid_report()
    report["config_sha256"] = None
    assert "config_sha256 must be an object" in module.validate_report(report)

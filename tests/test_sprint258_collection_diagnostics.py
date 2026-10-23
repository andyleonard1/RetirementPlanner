"""Regression tests for cross-environment pytest collection diagnostics."""
from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "test_collection_report.py"
spec = importlib.util.spec_from_file_location("rc4_collection_report", SCRIPT)
assert spec is not None and spec.loader is not None
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_node_id_parser_extracts_test_items_and_ignores_summary() -> None:
    output = "tests/test_a.py::test_one\nnoise\n2 tests collected in 0.1s\n"
    assert module.parse_node_ids(output) == ["tests/test_a.py::test_one"]


def test_node_id_parser_preserves_order_and_deduplicates() -> None:
    output = "tests/test_a.py::test_one\ntests/test_b.py::test_two\ntests/test_a.py::test_one\n"
    assert module.parse_node_ids(output) == ["tests/test_a.py::test_one", "tests/test_b.py::test_two"]


def test_node_id_parser_handles_empty_output() -> None:
    assert module.parse_node_ids("") == []


def test_file_hash_is_stable_for_unchanged_content(tmp_path: Path) -> None:
    path = tmp_path / "sample.txt"
    path.write_text("stable", encoding="utf-8")
    assert module.sha256_file(path) == module.sha256_file(path)


def test_report_counts_node_ids_by_file(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text("[tool.pytest.ini_options]\n", encoding="utf-8")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests/test_a.py").write_text("def test_one(): pass\n", encoding="utf-8")
    ids = ["tests/test_a.py::test_one", "tests/test_a.py::test_two"]
    report = module.build_report(tmp_path, ids)
    assert report["total_collected"] == 2
    assert report["test_file_count"] == 1
    assert report["counts_by_file"] == {"tests/test_a.py": 2}


def test_report_records_test_and_config_hashes(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text("config", encoding="utf-8")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests/test_a.py").write_text("test", encoding="utf-8")
    report = module.build_report(tmp_path, ["tests/test_a.py::test_one"])
    assert "tests/test_a.py" in report["test_file_sha256"]
    assert "pyproject.toml" in report["config_sha256"]


def test_compare_reports_identifies_only_current_and_only_other() -> None:
    current = {"node_ids": ["a::one", "b::two"], "test_file_sha256": {}, "config_sha256": {}}
    other = {"node_ids": ["a::one", "c::three"], "test_file_sha256": {}, "config_sha256": {}}
    diff = module.compare_reports(current, other)
    assert diff["only_current"] == ["b::two"]
    assert diff["only_other"] == ["c::three"]
    assert diff["only_current_count"] == diff["only_other_count"] == 1


def test_compare_reports_detects_changed_test_file_hashes() -> None:
    current = {"node_ids": ["a::one"], "test_file_sha256": {"tests/test_a.py": "new"}, "config_sha256": {}}
    other = {"node_ids": ["a::one"], "test_file_sha256": {"tests/test_a.py": "old"}, "config_sha256": {}}
    assert module.compare_reports(current, other)["files_with_different_hashes"] == ["tests/test_a.py"]


def test_report_format_is_versioned() -> None:
    report = module.build_report(ROOT, ["tests/test_a.py::test_one"])
    assert report["report_format"] == "retirement-planner-pytest-collection"
    assert report["report_version"] == 1


def test_comparison_is_clean_requires_node_ids_files_and_hashes_to_match() -> None:
    clean = {
        "only_current_count": 0, "only_other_count": 0,
        "files_only_current": [], "files_only_other": [],
        "files_with_different_hashes": [], "config_hashes_differ": False,
    }
    assert module.comparison_is_clean(clean)
    for field, value in (
        ("only_current_count", 1),
        ("only_other_count", 1),
        ("files_only_current", ["tests/new.py"]),
        ("files_only_other", ["tests/old.py"]),
        ("files_with_different_hashes", ["tests/test_a.py"]),
        ("config_hashes_differ", True),
    ):
        changed = dict(clean)
        changed[field] = value
        assert not module.comparison_is_clean(changed), field

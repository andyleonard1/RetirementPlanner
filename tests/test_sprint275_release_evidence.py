"""Sprint 275 regression tests for stale and internally inconsistent release evidence."""
from __future__ import annotations

import importlib.util
import json
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import release_evidence  # noqa: E402
import build_release_manifest  # noqa: E402


def _collection(root: Path) -> dict:
    test = root / "tests" / "test_sample.py"
    test.parent.mkdir(parents=True, exist_ok=True)
    test.write_text("def test_ok():\n    assert True\n", encoding="utf-8")
    import hashlib
    digest = hashlib.sha256(test.read_bytes()).hexdigest()
    return {
        "report_format": "retirement-planner-pytest-collection", "report_version": 1,
        "python_version": "3", "python_implementation": "CPython", "pytest_version": "x",
        "root_name": root.name, "total_collected": 1, "test_file_count": 1,
        "config_sha256": {}, "test_file_sha256": {"tests/test_sample.py": digest},
        "counts_by_file": {"tests/test_sample.py": 1},
        "node_ids": ["tests/test_sample.py::test_ok"],
    }


def test_collection_evidence_rejects_stale_test_file_hash(tmp_path: Path) -> None:
    report = _collection(tmp_path)
    (tmp_path / "tests" / "test_sample.py").write_text("def test_changed(): pass\n", encoding="utf-8")
    errors = release_evidence.validate_collection_against_tree(report, tmp_path)
    assert any("stale for: tests/test_sample.py" in error for error in errors)


def test_collection_evidence_rejects_missing_test_file(tmp_path: Path) -> None:
    report = _collection(tmp_path)
    (tmp_path / "tests" / "test_sample.py").unlink()
    errors = release_evidence.validate_collection_against_tree(report, tmp_path)
    assert any("missing file: tests/test_sample.py" in error for error in errors)


def test_collection_evidence_rejects_inconsistent_counts(tmp_path: Path) -> None:
    report = _collection(tmp_path)
    report["total_collected"] = 2
    errors = release_evidence.validate_collection_against_tree(report, tmp_path)
    assert any("total_collected does not match" in error for error in errors)


def test_manifest_evidence_rejects_stale_hash(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("old", encoding="utf-8")
    manifest = build_release_manifest.build_manifest(tmp_path, sprint=275)
    (tmp_path / "README.md").write_text("new", encoding="utf-8")
    errors = release_evidence.validate_manifest_against_tree(manifest, tmp_path)
    assert any("stale for: README.md" in error for error in errors)


def test_manifest_evidence_rejects_missing_and_extra_paths(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("ok", encoding="utf-8")
    manifest = build_release_manifest.build_manifest(tmp_path, sprint=275)
    manifest["files"].pop("README.md")
    manifest["files"]["gone.txt"] = {"size_bytes": 1, "sha256": "0" * 64}
    manifest["files"]["unexpected.txt"] = {"size_bytes": 1, "sha256": "0" * 64}
    manifest["file_count"] = 2
    errors = release_evidence.validate_manifest_against_tree(manifest, tmp_path)
    assert any("missing source files: README.md" in error for error in errors)
    assert any("stale/extra files: gone.txt" in error for error in errors)


def test_archive_inventory_rejects_unmanifested_file(tmp_path: Path) -> None:
    manifest = {"files": {"README.md": {"size_bytes": 2, "sha256": "x"}}}
    archive = tmp_path / "release.zip"
    with zipfile.ZipFile(archive, "w") as handle:
        handle.writestr("README.md", "ok")
        handle.writestr("extra.txt", "extra")
        handle.writestr("release_manifest.json", json.dumps(manifest))
    errors = release_evidence.validate_archive_inventory(archive, manifest)
    assert any("unmanifested entries: extra.txt" in error for error in errors)


def test_archive_inventory_rejects_embedded_manifest_mismatch(tmp_path: Path) -> None:
    manifest = {"files": {"README.md": {"size_bytes": 2, "sha256": "x"}}}
    archive = tmp_path / "release.zip"
    with zipfile.ZipFile(archive, "w") as handle:
        handle.writestr("README.md", "ok")
        handle.writestr("release_manifest.json", json.dumps({"files": {}}))
    errors = release_evidence.validate_archive_inventory(archive, manifest)
    assert any("embedded release_manifest.json differs" in error for error in errors)


def test_reconciliation_never_claims_test_execution(tmp_path: Path) -> None:
    # The report's test-execution field is explicit and intentionally independent
    # of collection totals; validate it through a deliberately failed report.
    collection = tmp_path / "collection.json"
    collection.write_text("{}", encoding="utf-8")
    (tmp_path / "release_manifest.json").write_text("{}", encoding="utf-8")
    archive = tmp_path / "release.zip"
    with zipfile.ZipFile(archive, "w") as handle:
        pass
    result = release_evidence.reconcile(tmp_path, collection, archive)
    assert result["status"] == "FAIL"
    assert result["test_execution_status"] == "NOT_VERIFIED_BY_THIS_REPORT"

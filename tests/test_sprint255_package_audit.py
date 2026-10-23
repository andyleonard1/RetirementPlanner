from __future__ import annotations

import hashlib
import json
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from package_audit import REQUIRED_ENTRIES, audit_archive  # noqa: E402


def _zip(path: Path, entries: dict[str, str]) -> None:
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, content in entries.items():
            archive.writestr(name, content)


def _valid_entries() -> dict[str, str]:
    entries = {
        name: (json.dumps({"ok": True}) if name == "data/assumptions.json" else "checkpoint")
        for name in REQUIRED_ENTRIES if name != "release_manifest.json"
    }
    manifest_files = {
        name: {"size_bytes": len(content.encode("utf-8")),
               "sha256": hashlib.sha256(content.encode("utf-8")).hexdigest()}
        for name, content in entries.items()
    }
    entries["release_manifest.json"] = json.dumps({
        "manifest_format": "retirement-planner-release-manifest",
        "manifest_version": 1,
        "sprint": 265,
        "file_count": len(manifest_files),
        "files": manifest_files,
    })
    return entries


def test_valid_checkpoint_archive_passes(tmp_path: Path) -> None:
    archive = tmp_path / "valid.zip"
    _zip(archive, _valid_entries())
    assert audit_archive(str(archive)) == []


def test_missing_required_file_is_reported(tmp_path: Path) -> None:
    entries = _valid_entries()
    entries.pop("planner/planner.py")
    archive = tmp_path / "missing.zip"
    _zip(archive, entries)
    assert any("planner/planner.py" in error for error in audit_archive(str(archive)))


def test_invalid_packaged_assumptions_is_reported(tmp_path: Path) -> None:
    entries = _valid_entries()
    entries["data/assumptions.json"] = "{invalid"
    archive = tmp_path / "bad-json.zip"
    _zip(archive, entries)
    assert any("assumptions JSON is invalid" in error for error in audit_archive(str(archive)))


def test_python_cache_is_rejected(tmp_path: Path) -> None:
    entries = _valid_entries()
    entries["tests/__pycache__/junk.pyc"] = "cache"
    archive = tmp_path / "cache.zip"
    _zip(archive, entries)
    errors = audit_archive(str(archive))
    assert any("transient directory" in error for error in errors)
    assert any("compiled Python artifact" in error for error in errors)


def test_pytest_cache_is_rejected(tmp_path: Path) -> None:
    entries = _valid_entries()
    entries[".pytest_cache/CACHEDIR.TAG"] = "cache"
    archive = tmp_path / "pytest-cache.zip"
    _zip(archive, entries)
    assert any("transient directory" in error for error in audit_archive(str(archive)))


def test_unsafe_path_is_rejected(tmp_path: Path) -> None:
    entries = _valid_entries()
    entries["../escape.txt"] = "unsafe"
    archive = tmp_path / "unsafe.zip"
    _zip(archive, entries)
    assert any("unsafe archive path" in error for error in audit_archive(str(archive)))


def test_unreadable_zip_is_reported(tmp_path: Path) -> None:
    archive = tmp_path / "not-a-zip.zip"
    archive.write_text("not a zip", encoding="utf-8")
    assert any("cannot read ZIP archive" in error for error in audit_archive(str(archive)))


def test_sprint255_release_traceability_exists() -> None:
    status = (ROOT / "PROJECT_STATUS.md").read_text(encoding="utf-8")
    roadmap = (ROOT / "RC4_ROADMAP.md").read_text(encoding="utf-8")
    assert "Sprint 255" in status
    assert "Sprint 255" in roadmap


def test_sprint259_historical_replay_traceability_exists() -> None:
    status = (ROOT / "PROJECT_STATUS.md").read_text(encoding="utf-8")
    roadmap = (ROOT / "RC4_ROADMAP.md").read_text(encoding="utf-8")
    assert "Sprint 259" in status
    assert "Sprint 259" in roadmap


def test_sprint261_historical_replay_isolation_traceability_exists() -> None:
    status = (ROOT / "PROJECT_STATUS.md").read_text(encoding="utf-8")
    roadmap = (ROOT / "RC4_ROADMAP.md").read_text(encoding="utf-8")
    assert "Sprint 261" in status
    assert "Sprint 261" in roadmap


def test_sprint263_collection_validation_traceability_exists() -> None:
    status = (ROOT / "PROJECT_STATUS.md").read_text(encoding="utf-8")
    roadmap = (ROOT / "RC4_ROADMAP.md").read_text(encoding="utf-8")
    assert "Sprint 263" in status
    assert "Sprint 263" in roadmap


def test_sprint264_collection_evidence_traceability_exists() -> None:
    assert (ROOT / "tests" / "test_sprint264_collection_evidence_freshness.py").is_file()
    assert (ROOT / "reports" / "sprint263_collection_report.json").is_file()
    assert (ROOT / "reports" / "sprint263_test_count_reconciliation.json").is_file()


def test_sprint264_audit_rejects_stale_local_collection_artifact(tmp_path: Path) -> None:
    archive = tmp_path / "stale-evidence.zip"
    with zipfile.ZipFile(archive, "w") as handle:
        handle.writestr("local-collection.json", "{}")
    errors = audit_archive(str(archive))
    assert any("stale/local test-run artifact included: local-collection.json" in error for error in errors)


def test_sprint265_manifest_traceability_exists() -> None:
    assert (ROOT / "scripts" / "build_release_manifest.py").is_file()
    assert (ROOT / "tests" / "test_sprint265_release_manifest.py").is_file()
    assert (ROOT / "reports" / "sprint265_collection_report.json").is_file()
    assert (ROOT / "reports" / "sprint265_test_count_reconciliation.json").is_file()
    assert "Sprint 265" in (ROOT / "PROJECT_STATUS.md").read_text(encoding="utf-8")
    assert "Sprint 265" in (ROOT / "RC4_ROADMAP.md").read_text(encoding="utf-8")


def test_manifest_hash_mismatch_is_reported(tmp_path: Path) -> None:
    entries = _valid_entries()
    entries["README.md"] = "changed after manifest generation"
    archive = tmp_path / "tampered.zip"
    _zip(archive, entries)
    assert any("SHA-256 mismatch for README.md" in error for error in audit_archive(str(archive)))

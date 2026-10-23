"""Sprint 266 cross-platform ZIP path safety regressions."""
from __future__ import annotations

import hashlib
import json
import sys
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from package_audit import (  # noqa: E402
    REQUIRED_ENTRIES,
    audit_archive,
    is_unsafe_archive_path,
)


def _valid_entries() -> dict[str, bytes]:
    entries = {
        name: (b'{"ok": true}' if name == "data/assumptions.json" else b"checkpoint")
        for name in REQUIRED_ENTRIES
        if name != "release_manifest.json"
    }
    entries["release_manifest.json"] = json.dumps(
        {
            "manifest_format": "retirement-planner-release-manifest",
            "manifest_version": 1,
            "sprint": 266,
            "file_count": len(entries),
            "files": {
                name: {
                    "size_bytes": len(content),
                    "sha256": hashlib.sha256(content).hexdigest(),
                }
                for name, content in entries.items()
            },
        }
    ).encode()
    return entries


def _write_zip(path: Path, entries: dict[str, bytes]) -> None:
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, content in entries.items():
            archive.writestr(name, content)


def test_backslash_parent_traversal_is_unsafe() -> None:
    assert is_unsafe_archive_path(r"..\outside.txt")


def test_nested_backslash_parent_traversal_is_unsafe() -> None:
    assert is_unsafe_archive_path(r"reports\..\outside.txt")


def test_windows_drive_absolute_path_is_unsafe() -> None:
    assert is_unsafe_archive_path("C:/outside.txt")


def test_unc_path_is_unsafe() -> None:
    assert is_unsafe_archive_path(r"\\server\share\outside.txt")


def test_noncanonical_backslash_separator_is_unsafe() -> None:
    assert is_unsafe_archive_path(r"reports\sprint.json")


def test_posix_absolute_path_is_unsafe() -> None:
    assert is_unsafe_archive_path("/tmp/outside.txt")


def test_nested_posix_parent_traversal_is_unsafe() -> None:
    assert is_unsafe_archive_path("reports/../../outside.txt")


def test_canonical_relative_path_is_safe() -> None:
    assert not is_unsafe_archive_path("reports/sprint266_collection_report.json")


def test_archive_audit_rejects_windows_style_member_path(tmp_path: Path) -> None:
    entries = _valid_entries()
    entries[r"reports\..\outside.txt"] = b"unsafe"
    archive = tmp_path / "windows-path.zip"
    _write_zip(archive, entries)
    assert any("unsafe archive path" in error for error in audit_archive(str(archive)))


def test_archive_audit_rejects_manifest_entry_with_unsafe_path(tmp_path: Path) -> None:
    entries = _valid_entries()
    manifest = json.loads(entries["release_manifest.json"])
    manifest["files"][r"..\outside.txt"] = {"size_bytes": 1, "sha256": "0" * 64}
    manifest["file_count"] = len(manifest["files"])
    entries["release_manifest.json"] = json.dumps(manifest).encode()
    archive = tmp_path / "manifest-path.zip"
    _write_zip(archive, entries)
    errors = audit_archive(str(archive))
    assert any("invalid path" in error for error in errors)


def test_archive_audit_reports_duplicate_member_names(tmp_path: Path) -> None:
    entries = _valid_entries()
    archive = tmp_path / "duplicate.zip"
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as handle:
        for name, content in entries.items():
            handle.writestr(name, content)
        with pytest.warns(UserWarning, match="Duplicate name"):
            handle.writestr("README.md", b"second copy")
    assert any("duplicate archive entries" in error for error in audit_archive(str(archive)))


def test_path_safety_documentation_is_present() -> None:
    doc = ROOT / "planner" / "docs" / "PACKAGE_PATH_SAFETY.md"
    assert doc.is_file()
    assert "UNC paths" in doc.read_text(encoding="utf-8")


def test_sprint266_status_and_roadmap_traceability() -> None:
    assert "Sprint 266" in (ROOT / "PROJECT_STATUS.md").read_text(encoding="utf-8")
    assert "Sprint 266" in (ROOT / "RC4_ROADMAP.md").read_text(encoding="utf-8")

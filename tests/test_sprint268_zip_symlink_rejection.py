"""Sprint 268 ZIP special-entry safety regressions."""
from __future__ import annotations

import hashlib
import json
import stat
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from package_audit import REQUIRED_ENTRIES, audit_archive  # noqa: E402


def _entries() -> dict[str, bytes]:
    entries = {
        name: (b'{"ok": true}' if name == "data/assumptions.json" else b"checkpoint")
        for name in REQUIRED_ENTRIES if name != "release_manifest.json"
    }
    entries["release_manifest.json"] = json.dumps({
        "manifest_format": "retirement-planner-release-manifest",
        "manifest_version": 1,
        "sprint": 268,
        "file_count": len(entries),
        "files": {
            name: {"size_bytes": len(content), "sha256": hashlib.sha256(content).hexdigest()}
            for name, content in entries.items()
        },
    }).encode()
    return entries


def _write_zip(path: Path, entries: dict[str, bytes], symlink_name: str | None = None) -> None:
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, content in entries.items():
            info = zipfile.ZipInfo(name)
            info.compress_type = zipfile.ZIP_DEFLATED
            if name == symlink_name:
                info.create_system = 3  # Unix attributes, independent of host OS
                info.external_attr = (stat.S_IFLNK | 0o777) << 16
                content = b"../../outside-target"
            archive.writestr(info, content)


def test_audit_rejects_unix_symlink_even_when_named_as_required_file(tmp_path: Path) -> None:
    entries = _entries()
    path = tmp_path / "symlink-required-entry.zip"
    _write_zip(path, entries, symlink_name="README.md")
    assert any("symbolic link archive entry is not allowed: README.md" in error for error in audit_archive(str(path)))


def test_audit_rejects_symlink_entry_not_listed_in_manifest(tmp_path: Path) -> None:
    entries = _entries()
    entries["payload-link"] = b"target"
    path = tmp_path / "symlink-extra-entry.zip"
    _write_zip(path, entries, symlink_name="payload-link")
    errors = audit_archive(str(path))
    assert any("symbolic link archive entry is not allowed: payload-link" in error for error in errors)
    assert any("manifest file paths do not match archive contents" in error for error in errors)


def test_audit_still_accepts_regular_required_files(tmp_path: Path) -> None:
    path = tmp_path / "regular-files.zip"
    _write_zip(path, _entries())
    assert audit_archive(str(path)) == []


def test_directory_entries_are_checked_for_unsafe_paths(tmp_path: Path) -> None:
    path = tmp_path / "unsafe-directory.zip"
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("../escape/", b"")
    assert any("unsafe archive path: ../escape/" in error for error in audit_archive(str(path)))

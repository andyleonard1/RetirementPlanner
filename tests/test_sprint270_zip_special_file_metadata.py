"""Sprint 270 ZIP Unix file-type metadata hardening regressions."""
from __future__ import annotations

import hashlib
import json
import stat
import sys
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from package_audit import REQUIRED_ENTRIES, _archive_entry_type_errors, audit_archive  # noqa: E402


def _info(name: str, file_type: int = stat.S_IFREG) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(name)
    info.create_system = 3
    info.external_attr = (file_type | 0o644) << 16
    if name.endswith("/"):
        info.external_attr = (stat.S_IFDIR | 0o755) << 16
    return info


def _entries() -> dict[str, bytes]:
    entries = {
        name: (b'{"ok": true}' if name == "data/assumptions.json" else b"checkpoint")
        for name in REQUIRED_ENTRIES if name != "release_manifest.json"
    }
    entries["release_manifest.json"] = json.dumps({
        "manifest_format": "retirement-planner-release-manifest",
        "manifest_version": 1,
        "sprint": 270,
        "file_count": len(entries),
        "files": {
            name: {"size_bytes": len(content), "sha256": hashlib.sha256(content).hexdigest()}
            for name, content in entries.items()
        },
    }).encode()
    return entries


def _write_zip(path: Path, special_name: str | None = None, file_type: int = stat.S_IFREG) -> None:
    entries = _entries()
    if special_name:
        entries[special_name] = b"metadata-payload"
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, content in entries.items():
            info = zipfile.ZipInfo(name)
            info.compress_type = zipfile.ZIP_DEFLATED
            if name == special_name:
                info.create_system = 3
                info.external_attr = (file_type | 0o644) << 16
            archive.writestr(info, content)


@pytest.mark.parametrize("file_type", [stat.S_IFIFO, stat.S_IFCHR, stat.S_IFBLK, stat.S_IFSOCK])
def test_metadata_rejects_unneeded_unix_special_file_types(file_type: int) -> None:
    errors = _archive_entry_type_errors([_info("payload.bin", file_type)])
    assert errors == ["special file archive entry is not allowed: payload.bin"]


def test_metadata_rejects_directory_type_without_directory_suffix() -> None:
    errors = _archive_entry_type_errors([_info("folder", stat.S_IFDIR)])
    assert any("directory metadata but no directory path suffix" in error for error in errors)


def test_metadata_rejects_regular_file_type_with_directory_suffix() -> None:
    info = zipfile.ZipInfo("folder/")
    info.create_system = 3
    info.external_attr = (stat.S_IFREG | 0o644) << 16
    errors = _archive_entry_type_errors([info])
    assert any("regular-file metadata but a directory path suffix" in error for error in errors)


def test_audit_rejects_special_file_before_crc_or_payload_reads(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    path = tmp_path / "fifo-entry.zip"
    _write_zip(path, "README.md", stat.S_IFIFO)

    def forbidden_testzip(self: zipfile.ZipFile):
        raise AssertionError("CRC/payload reading must not run before rejecting special entry metadata")

    monkeypatch.setattr(zipfile.ZipFile, "testzip", forbidden_testzip)
    errors = audit_archive(str(path))
    assert any("special file archive entry is not allowed: README.md" in error for error in errors)


def test_audit_accepts_regular_release_files_and_directory_metadata(tmp_path: Path) -> None:
    errors = _archive_entry_type_errors([
        _info("README.md", stat.S_IFREG),
        _info("planner/docs/", stat.S_IFDIR),
    ])
    assert errors == []


def test_sprint270_docs_status_and_roadmap_are_traceable() -> None:
    assert (ROOT / "planner/docs/ZIP_SPECIAL_FILE_METADATA.md").is_file()
    assert "Sprint 270" in (ROOT / "PROJECT_STATUS.md").read_text(encoding="utf-8")
    assert "Sprint 270" in (ROOT / "RC4_ROADMAP.md").read_text(encoding="utf-8")

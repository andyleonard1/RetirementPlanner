"""Sprint 273: local ZIP headers must agree with central-directory metadata."""
from __future__ import annotations

import copy
import struct
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from package_audit import _local_header_errors  # noqa: E402


def _write_zip(path: Path) -> None:
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("docs/guide.txt", b"guide contents")
        archive.writestr("data.json", b'{"ok": true}')


def _mutate(path: Path, offset: int, replacement: bytes) -> None:
    data = bytearray(path.read_bytes())
    data[offset:offset + len(replacement)] = replacement
    path.write_bytes(data)


def test_accepts_consistent_local_headers(tmp_path: Path) -> None:
    path = tmp_path / "valid.zip"
    _write_zip(path)
    with zipfile.ZipFile(path) as archive:
        assert _local_header_errors(archive, archive.infolist()) == []


def test_rejects_invalid_local_header_signature(tmp_path: Path) -> None:
    path = tmp_path / "signature.zip"
    _write_zip(path)
    _mutate(path, 0, b"NOPE")
    with zipfile.ZipFile(path) as archive:
        errors = _local_header_errors(archive, archive.infolist())
    assert any("invalid ZIP local-header signature" in error for error in errors)


def test_rejects_local_filename_mismatch(tmp_path: Path) -> None:
    path = tmp_path / "name.zip"
    _write_zip(path)
    # Change first local-header filename without changing the central directory.
    _mutate(path, 30, b"X")
    with zipfile.ZipFile(path) as archive:
        errors = _local_header_errors(archive, archive.infolist())
    assert any("filename disagrees" in error for error in errors)


def test_rejects_local_compression_method_mismatch(tmp_path: Path) -> None:
    path = tmp_path / "method.zip"
    _write_zip(path)
    _mutate(path, 8, struct.pack("<H", zipfile.ZIP_STORED))
    with zipfile.ZipFile(path) as archive:
        errors = _local_header_errors(archive, archive.infolist())
    assert any("compression method disagrees" in error for error in errors)


def test_rejects_local_flags_mismatch(tmp_path: Path) -> None:
    path = tmp_path / "flags.zip"
    _write_zip(path)
    _mutate(path, 6, struct.pack("<H", 0x08))
    with zipfile.ZipFile(path) as archive:
        errors = _local_header_errors(archive, archive.infolist())
    assert any("flags disagree" in error for error in errors)


def test_rejects_local_crc_mismatch(tmp_path: Path) -> None:
    path = tmp_path / "crc.zip"
    _write_zip(path)
    _mutate(path, 14, struct.pack("<I", 123))
    with zipfile.ZipFile(path) as archive:
        errors = _local_header_errors(archive, archive.infolist())
    assert any("CRC disagrees" in error for error in errors)


def test_rejects_local_size_mismatch(tmp_path: Path) -> None:
    path = tmp_path / "size.zip"
    _write_zip(path)
    _mutate(path, 18, struct.pack("<I", 999))
    with zipfile.ZipFile(path) as archive:
        errors = _local_header_errors(archive, archive.infolist())
    assert any("sizes disagree" in error for error in errors)


def test_rejects_local_header_extending_into_central_directory(tmp_path: Path) -> None:
    path = tmp_path / "length.zip"
    _write_zip(path)
    _mutate(path, 26, struct.pack("<H", 0xFFFF))
    with zipfile.ZipFile(path) as archive:
        errors = _local_header_errors(archive, archive.infolist())
    assert any("extends into central directory" in error for error in errors)


def test_rejects_overlapping_local_records(tmp_path: Path) -> None:
    path = tmp_path / "overlap.zip"
    _write_zip(path)
    with zipfile.ZipFile(path) as archive:
        infos = archive.infolist()
        overlapping = copy.copy(infos[1])
        overlapping.header_offset = infos[0].header_offset
        errors = _local_header_errors(archive, [infos[0], overlapping])
    assert any("overlapping ZIP local records" in error for error in errors)


def test_sprint273_docs_status_and_roadmap_are_traceable() -> None:
    assert (ROOT / "planner/docs/ZIP_LOCAL_HEADER_INTEGRITY.md").is_file()
    assert "Sprint 273" in (ROOT / "PROJECT_STATUS.md").read_text(encoding="utf-8")
    assert "Sprint 273" in (ROOT / "RC4_ROADMAP.md").read_text(encoding="utf-8")

"""Sprint 269 ZIP metadata and decompression resource-bound regressions."""
from __future__ import annotations

import hashlib
import json
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from package_audit import (  # noqa: E402
    ALLOWED_COMPRESSION_METHODS,
    MAX_ARCHIVE_ENTRIES,
    MAX_COMPRESSION_RATIO,
    MAX_ENTRY_UNCOMPRESSED_BYTES,
    MAX_TOTAL_UNCOMPRESSED_BYTES,
    REQUIRED_ENTRIES,
    _archive_metadata_errors,
    audit_archive,
)


def _info(name: str = "payload.bin", *, size: int = 1, compressed: int = 1,
          method: int = zipfile.ZIP_DEFLATED, flags: int = 0) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(name)
    info.file_size = size
    info.compress_size = compressed
    info.compress_type = method
    info.flag_bits = flags
    return info


def _entries() -> dict[str, bytes]:
    entries = {
        name: (b'{"ok": true}' if name == "data/assumptions.json" else b"checkpoint")
        for name in REQUIRED_ENTRIES if name != "release_manifest.json"
    }
    entries["release_manifest.json"] = json.dumps({
        "manifest_format": "retirement-planner-release-manifest",
        "manifest_version": 1,
        "sprint": 269,
        "file_count": len(entries),
        "files": {
            name: {"size_bytes": len(content), "sha256": hashlib.sha256(content).hexdigest()}
            for name, content in entries.items()
        },
    }).encode()
    return entries


def _write_zip(path: Path, entries: dict[str, bytes]) -> None:
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, content in entries.items():
            archive.writestr(name, content)


def test_metadata_accepts_supported_compression_methods() -> None:
    infos = [_info(method=method) for method in ALLOWED_COMPRESSION_METHODS]
    assert _archive_metadata_errors(infos) == []


def test_metadata_rejects_encrypted_entries() -> None:
    errors = _archive_metadata_errors([_info(flags=0x1)])
    assert any("encrypted archive entry is not allowed" in error for error in errors)


def test_metadata_rejects_unsupported_compression_method() -> None:
    errors = _archive_metadata_errors([_info(method=99)])
    assert any("unsupported ZIP compression method" in error for error in errors)


def test_metadata_rejects_single_entry_over_size_limit() -> None:
    errors = _archive_metadata_errors([_info(size=MAX_ENTRY_UNCOMPRESSED_BYTES + 1, compressed=100)])
    assert any("exceeds uncompressed size limit" in error for error in errors)


def test_metadata_rejects_total_uncompressed_size_over_limit() -> None:
    infos = [
        _info("a.bin", size=MAX_TOTAL_UNCOMPRESSED_BYTES // 2 + 1, compressed=100),
        _info("b.bin", size=MAX_TOTAL_UNCOMPRESSED_BYTES // 2 + 1, compressed=100),
    ]
    errors = _archive_metadata_errors(infos)
    assert any("archive exceeds total uncompressed size limit" in error for error in errors)


def test_metadata_rejects_excessive_compression_ratio() -> None:
    errors = _archive_metadata_errors([_info(size=MAX_COMPRESSION_RATIO * 10 + 1, compressed=10)])
    assert any("compression ratio exceeds limit" in error for error in errors)


def test_metadata_rejects_zero_compressed_size_with_content() -> None:
    errors = _archive_metadata_errors([_info(size=1, compressed=0)])
    assert any("zero compressed size but nonzero content" in error for error in errors)


def test_metadata_rejects_excessive_entry_count() -> None:
    infos = [_info(f"{index}.bin") for index in range(MAX_ARCHIVE_ENTRIES + 1)]
    errors = _archive_metadata_errors(infos)
    assert any("archive contains too many entries" in error for error in errors)


def test_audit_preflights_encrypted_archive_before_decompression(tmp_path: Path) -> None:
    path = tmp_path / "encrypted-metadata.zip"
    _write_zip(path, _entries())
    data = bytearray(path.read_bytes())
    # Mark every local and central-directory record encrypted. The payload bytes
    # remain unchanged; the auditor must reject from metadata before testzip/read.
    local_sig = b"PK\x03\x04"
    central_sig = b"PK\x01\x02"
    offset = 0
    while True:
        offset = data.find(local_sig, offset)
        if offset < 0:
            break
        data[offset + 6] |= 0x01
        offset += 4
    offset = 0
    while True:
        offset = data.find(central_sig, offset)
        if offset < 0:
            break
        data[offset + 8] |= 0x01
        offset += 4
    path.write_bytes(data)
    errors = audit_archive(str(path))
    assert any("encrypted archive entry is not allowed" in error for error in errors)
    assert not any("ZIP integrity check could not safely read entries" in error for error in errors)


def test_sprint269_docs_status_and_roadmap_are_traceable() -> None:
    doc = ROOT / "planner" / "docs" / "ZIP_METADATA_RESOURCE_LIMITS.md"
    assert doc.is_file()
    assert "Sprint 269" in (ROOT / "PROJECT_STATUS.md").read_text(encoding="utf-8")
    assert "Sprint 269" in (ROOT / "RC4_ROADMAP.md").read_text(encoding="utf-8")

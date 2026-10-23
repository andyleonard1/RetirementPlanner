"""Sprint 274 review regressions for ZIP data-descriptor integrity."""
from __future__ import annotations

import io
import struct
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from package_audit import _local_header_errors  # noqa: E402


class _NonSeekableBuffer(io.BytesIO):
    """A ZIP output buffer that forces zipfile to emit a data descriptor."""

    def seekable(self) -> bool:
        return False

    def seek(self, *args: object) -> int:
        raise io.UnsupportedOperation("non-seekable buffer")


def _descriptor_zip(path: Path, *, force_zip64: bool = False) -> tuple[bytes, zipfile.ZipInfo, int]:
    buffer = _NonSeekableBuffer()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        payload = b"data descriptor test payload " * 20
        if force_zip64:
            with archive.open("payload.txt", "w", force_zip64=True) as member:
                member.write(payload)
        else:
            archive.writestr("payload.txt", payload)
    data = buffer.getvalue()
    path.write_bytes(data)
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        info = archive.infolist()[0]
        fixed = data[info.header_offset:info.header_offset + 30]
        values = struct.unpack("<IHHHHHIIIHH", fixed)
        data_offset = info.header_offset + 30 + values[-2] + values[-1]
        descriptor_offset = data_offset + info.compress_size
    assert data[descriptor_offset:descriptor_offset + 4] == b"PK\x07\x08"
    return data, info, descriptor_offset


def _write_mutation(path: Path, data: bytes) -> None:
    path.write_bytes(data)


def test_accepts_consistent_signed_data_descriptor(tmp_path: Path) -> None:
    path = tmp_path / "signed-descriptor.zip"
    _descriptor_zip(path)
    with zipfile.ZipFile(path) as archive:
        assert _local_header_errors(archive, archive.infolist()) == []


def test_accepts_consistent_zip64_data_descriptor(tmp_path: Path) -> None:
    path = tmp_path / "zip64-descriptor.zip"
    _descriptor_zip(path, force_zip64=True)
    with zipfile.ZipFile(path) as archive:
        assert _local_header_errors(archive, archive.infolist()) == []


def test_accepts_consistent_unsigned_data_descriptor(tmp_path: Path) -> None:
    path = tmp_path / "unsigned-descriptor.zip"
    data, _info, descriptor_offset = _descriptor_zip(path)
    mutated = bytearray(data)
    del mutated[descriptor_offset:descriptor_offset + 4]
    # The end-of-central-directory stores the central-directory offset.
    eocd = mutated.rfind(b"PK\x05\x06")
    assert eocd >= 0
    central_offset = struct.unpack_from("<I", mutated, eocd + 16)[0]
    struct.pack_into("<I", mutated, eocd + 16, central_offset - 4)
    _write_mutation(path, bytes(mutated))
    with zipfile.ZipFile(path) as archive:
        assert _local_header_errors(archive, archive.infolist()) == []


def test_rejects_data_descriptor_crc_mismatch(tmp_path: Path) -> None:
    path = tmp_path / "descriptor-crc.zip"
    data, _info, descriptor_offset = _descriptor_zip(path)
    mutated = bytearray(data)
    struct.pack_into("<I", mutated, descriptor_offset + 4, 0x12345678)
    _write_mutation(path, bytes(mutated))
    with zipfile.ZipFile(path) as archive:
        errors = _local_header_errors(archive, archive.infolist())
    assert any("data descriptor CRC/sizes disagree" in error for error in errors)


def test_rejects_data_descriptor_size_mismatch(tmp_path: Path) -> None:
    path = tmp_path / "descriptor-size.zip"
    data, _info, descriptor_offset = _descriptor_zip(path)
    mutated = bytearray(data)
    compressed_size = struct.unpack_from("<I", mutated, descriptor_offset + 8)[0]
    struct.pack_into("<I", mutated, descriptor_offset + 8, compressed_size + 1)
    _write_mutation(path, bytes(mutated))
    with zipfile.ZipFile(path) as archive:
        errors = _local_header_errors(archive, archive.infolist())
    assert any("data descriptor CRC/sizes disagree" in error for error in errors)


def test_sprint274_docs_status_and_roadmap_are_traceable() -> None:
    assert (ROOT / "planner/docs/ZIP_SECURITY_REVIEW.md").is_file()
    assert "Sprint 274" in (ROOT / "PROJECT_STATUS.md").read_text(encoding="utf-8")
    assert "Sprint 274" in (ROOT / "RC4_ROADMAP.md").read_text(encoding="utf-8")

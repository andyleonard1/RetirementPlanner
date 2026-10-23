"""Audit an RC4 checkpoint ZIP without extracting or modifying it.

Usage: python scripts/package_audit.py path/to/checkpoint.zip
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import stat
import struct
import sys
import unicodedata
import zipfile
from pathlib import PurePosixPath
from typing import Iterable

REQUIRED_ENTRIES = {
    "README.md",
    "RC4_ROADMAP.md",
    "PROJECT_STATUS.md",
    "data/assumptions.json",
    "planner/planner.py",
    "planner/docs/RELEASE_READINESS.md",
    "scripts/release_acceptance.py",
    "tests/test_sprint254_release_acceptance.py",
    "scripts/test_collection_report.py",
    "planner/docs/TEST_COLLECTION_DIAGNOSTICS.md",
    "tests/test_sprint258_collection_diagnostics.py",
    "planner/market/historical_replay.py",
    "tests/test_sprint259_historical_replay.py",
    "tests/test_sprint260_historical_replay_hardening.py",
    "tests/test_sprint261_historical_replay_isolation.py",
    "reports/sprint263_collection_report.json",
    "reports/sprint263_test_count_reconciliation.json",
    "reports/sprint264_collection_report.json",
    "reports/sprint264_test_count_reconciliation.json",
    "reports/sprint265_collection_report.json",
    "reports/sprint265_test_count_reconciliation.json",
    "reports/archive/sprint262_windows_collection_report.json",
    "reports/archive/sprint258_windows_collection_report.json",
    "release_manifest.json",
    "planner/docs/RELEASE_MANIFEST.md",
    "scripts/build_release_manifest.py",
    "tests/test_sprint265_release_manifest.py",
    "tests/test_sprint266_package_path_safety.py",
    "tests/test_sprint267_manifest_schema_hardening.py",
    "tests/test_sprint268_zip_symlink_rejection.py",
    "tests/test_sprint269_zip_metadata_resource_limits.py",
    "tests/test_sprint270_zip_special_file_metadata.py",
    "tests/test_sprint271_zip_filename_collisions.py",
    "tests/test_sprint272_windows_filename_safety.py",
    "tests/test_sprint273_zip_local_header_integrity.py",
    "tests/test_sprint274_zip_data_descriptor_integrity.py",
    "scripts/release_evidence.py",
    "tests/test_sprint275_release_evidence.py",
    "planner/docs/REPRODUCIBLE_RELEASE_EVIDENCE.md",
    ".github/workflows/release.yml",
    "planner/docs/RELEASE_WORKFLOW.md",
    "scripts/build_release_archive.py",
    "tests/test_sprint276_release_workflow.py",
    "scripts/audit_assumption_coverage.py",
    "tests/test_sprint277_assumption_coverage_audit.py",
    "tests/test_sprint278_gui_assumptions_coverage.py",
    "planner/docs/GUI_ASSUMPTIONS_COVERAGE.md",
    "reports/sprint278_collection_report.json",
    "tests/test_sprint279_inflation_adjusted_isa_allowance.py",
    "planner/docs/INFLATION_ADJUSTED_ISA_ALLOWANCE.md",
    "reports/sprint279_collection_report.json",
    "tests/test_sprint280_pension_funding_forecast_integration.py",
    "planner/docs/PENSION_FUNDING_FORECAST_INTEGRATION.md",
    "reports/sprint280_collection_report.json",
    "tests/test_sprint281_end_to_end_scenario_integration.py",
    "planner/docs/END_TO_END_SCENARIO_INTEGRATION.md",
    "reports/sprint281_collection_report.json",
    "tests/test_sprint282_tax_withdrawal_scenarios.py",
    "planner/docs/TAX_WITHDRAWAL_SCENARIO_INTEGRATION.md",
    "reports/sprint282_collection_report.json",
    "tests/test_sprint283_deterministic_monte_carlo_parity.py",
    "planner/docs/DETERMINISTIC_MONTE_CARLO_PARITY.md",
    "reports/sprint283_collection_report.json",
    "tests/test_sprint284_golden_scenario_regression_pack.py",
    "tests/test_sprint285_release_readiness.py",
    "planner/docs/SPRINT285_RELEASE_READINESS.md",
    "reports/sprint285_collection_report.json",
    "tests/golden/sprint284_scenarios.json",
    "planner/docs/GOLDEN_SCENARIO_REGRESSION_PACK.md",
    "reports/sprint284_collection_report.json",
    "planner/docs/ASSUMPTION_COVERAGE_AUDIT.md",
    "reports/sprint277_assumption_coverage_audit.json",
    "tests/test_sprint278_gui_assumptions_workflow_matrix.py",
    "planner/docs/GUI_ASSUMPTIONS_WORKFLOW_COVERAGE.md",
    "reports/sprint278_collection_report.json",
    "tests/test_sprint279_inflation_adjusted_isa_allowance.py",
    "planner/docs/INFLATION_ADJUSTED_ISA_ALLOWANCE.md",
    "reports/sprint279_collection_report.json",
    "reports/sprint276_collection_report.json",
    "reports/sprint277_collection_report.json",
    "reports/sprint275_collection_report.json",
    "planner/docs/ZIP_SPECIAL_ENTRY_SAFETY.md",
    "planner/docs/ZIP_METADATA_RESOURCE_LIMITS.md",
    "planner/docs/ZIP_SPECIAL_FILE_METADATA.md",
    "planner/docs/ZIP_FILENAME_COLLISION_SAFETY.md",
    "planner/docs/ZIP_WINDOWS_FILENAME_SAFETY.md",
    "planner/docs/ZIP_LOCAL_HEADER_INTEGRITY.md",
    "planner/docs/ZIP_SECURITY_REVIEW.md",
    "reports/sprint268_collection_report.json",
    "reports/sprint269_collection_report.json",
    "reports/sprint270_collection_report.json",
    "reports/sprint270_test_count_reconciliation.json",
    "reports/sprint271_collection_report.json",
    "reports/sprint271_test_count_reconciliation.json",
    "reports/sprint272_collection_report.json",
    "reports/sprint272_test_count_reconciliation.json",
    "reports/sprint273_collection_report.json",
    "reports/sprint273_test_count_reconciliation.json",
    "reports/sprint274_collection_report.json",
    "reports/sprint274_test_count_reconciliation.json",
    "reports/sprint269_test_count_reconciliation.json",
    "reports/sprint268_test_count_reconciliation.json",
    "planner/docs/RELEASE_MANIFEST_SCHEMA.md",
    "reports/sprint267_collection_report.json",
    "reports/sprint267_test_count_reconciliation.json",
    "planner/docs/PACKAGE_PATH_SAFETY.md",
    "reports/sprint266_collection_report.json",
    "reports/sprint266_test_count_reconciliation.json",
    "tests/test_sprint263_collection_report_validation.py",
    "tests/test_sprint264_collection_evidence_freshness.py",
}
FORBIDDEN_PARTS = {"__pycache__", ".pytest_cache", ".git", ".venv", "venv", "dist"}
FORBIDDEN_LOCAL_EVIDENCE = {"local-collection.json", "collection-local.json", "full_test.txt"}
# Bound decompression work before testzip() or manifest reads touch payloads.
MAX_ARCHIVE_ENTRIES = 10_000
MAX_ENTRY_UNCOMPRESSED_BYTES = 32 * 1024 * 1024
MAX_TOTAL_UNCOMPRESSED_BYTES = 256 * 1024 * 1024
MAX_COMPRESSION_RATIO = 200.0
ALLOWED_COMPRESSION_METHODS = {zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED}


def is_unsafe_archive_path(name: str) -> bool:
    """Reject non-portable and traversal paths before any extraction occurs.

    ZIP member names should use canonical POSIX separators. Backslashes are
    rejected rather than normalized so a package cannot behave differently on
    POSIX and Windows extraction tools.
    """
    if not name or "\\" in name or "\x00" in name:
        return True
    if name.startswith("/") or re.match(r"^[A-Za-z]:", name):
        return True
    return ".." in PurePosixPath(name).parts


def _unique_json_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    """JSON object hook that rejects duplicate keys instead of silently overwriting."""
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON object key: {key}")
        result[key] = value
    return result


def _archive_metadata_errors(infos: list[zipfile.ZipInfo]) -> list[str]:
    """Check central-directory metadata before any potentially expensive decompression."""
    errors: list[str] = []
    if len(infos) > MAX_ARCHIVE_ENTRIES:
        errors.append(
            f"archive contains too many entries: {len(infos)} (maximum {MAX_ARCHIVE_ENTRIES})"
        )
    total_uncompressed = 0
    for info in infos:
        if info.flag_bits & 0x1:
            errors.append(f"encrypted archive entry is not allowed: {info.filename}")
        if info.compress_type not in ALLOWED_COMPRESSION_METHODS:
            errors.append(f"unsupported ZIP compression method for entry: {info.filename}")
        if info.file_size < 0 or info.compress_size < 0:
            errors.append(f"negative ZIP entry size: {info.filename}")
            continue
        total_uncompressed += info.file_size
        if info.file_size > MAX_ENTRY_UNCOMPRESSED_BYTES:
            errors.append(
                f"ZIP entry exceeds uncompressed size limit: {info.filename} "
                f"({info.file_size} bytes; maximum {MAX_ENTRY_UNCOMPRESSED_BYTES})"
            )
        if info.file_size > 0 and info.compress_size == 0:
            errors.append(f"ZIP entry has zero compressed size but nonzero content: {info.filename}")
        elif info.compress_size > 0 and info.file_size / info.compress_size > MAX_COMPRESSION_RATIO:
            errors.append(
                f"ZIP entry compression ratio exceeds limit: {info.filename} "
                f"({info.file_size / info.compress_size:.1f}:1; maximum {MAX_COMPRESSION_RATIO:.0f}:1)"
            )
    if total_uncompressed > MAX_TOTAL_UNCOMPRESSED_BYTES:
        errors.append(
            f"archive exceeds total uncompressed size limit: {total_uncompressed} bytes "
            f"(maximum {MAX_TOTAL_UNCOMPRESSED_BYTES})"
        )
    return errors


def _archive_entry_type_errors(infos: list[zipfile.ZipInfo]) -> list[str]:
    """Reject special Unix file types and path/type disagreements from metadata.

    ZIP archives can encode FIFO, device, socket, directory, and symlink types
    in external attributes. The release format only needs regular files and
    directories; accepting other types can create extraction-dependent results.
    """
    errors: list[str] = []
    allowed_types = {0, stat.S_IFREG, stat.S_IFDIR, stat.S_IFLNK}
    for info in infos:
        # Unix file-type bits are meaningful only for entries created on Unix.
        if info.create_system != 3:
            continue
        mode = info.external_attr >> 16
        file_type = stat.S_IFMT(mode)
        if file_type not in allowed_types:
            errors.append(f"special file archive entry is not allowed: {info.filename}")
            continue
        if file_type == stat.S_IFDIR and not info.is_dir():
            errors.append(f"ZIP entry has directory metadata but no directory path suffix: {info.filename}")
        elif file_type == stat.S_IFREG and info.is_dir():
            errors.append(f"ZIP entry has regular-file metadata but a directory path suffix: {info.filename}")
    return errors


def _archive_path_collision_errors(infos: list[zipfile.ZipInfo]) -> list[str]:
    """Reject archive paths that alias on common case-insensitive/Unicode filesystems.

    ZIP paths are compared after NFC normalization and case folding. This is
    intentionally stricter than POSIX so the same release cannot overwrite or
    shadow another member when extracted on Windows or a normalization-aware
    filesystem. File entries may not also be parent paths of other entries.
    """
    errors: list[str] = []
    canonical_to_original: dict[str, str] = {}
    file_paths: set[str] = set()
    all_paths: set[str] = set()

    for info in infos:
        raw_name = info.filename.rstrip("/") if info.is_dir() else info.filename
        canonical = unicodedata.normalize("NFC", raw_name).casefold()
        previous = canonical_to_original.get(canonical)
        if previous is not None and previous != info.filename:
            errors.append(
                f"archive paths collide after case/Unicode normalization: {previous!r} and {info.filename!r}"
            )
        else:
            canonical_to_original[canonical] = info.filename
        all_paths.add(canonical)
        if not info.is_dir():
            file_paths.add(canonical)

    # A regular file cannot safely coexist as a parent directory for another
    # member (e.g. "assets" and "assets/logo.png"). Build the parent set in
    # one pass so the check remains bounded for archives near the entry limit.
    parent_paths: set[str] = set()
    for path in all_paths:
        parts = path.split("/")
        for index in range(1, len(parts)):
            parent_paths.add("/".join(parts[:index]))
    for file_path in sorted(file_paths & parent_paths):
        errors.append(f"archive file path conflicts with a child path: {file_path}")
    return errors


def _windows_filename_errors(infos: list[zipfile.ZipInfo]) -> list[str]:
    """Reject ZIP components that cannot be represented safely on Windows.

    Windows forbids control characters and several punctuation characters in
    ordinary file names, trims trailing dots/spaces, and reserves DOS device
    names even when they have extensions. ZIP members are never extracted by
    this function; it performs a conservative cross-platform portability check.
    """
    errors: list[str] = []
    invalid_chars = set('<>:"|?*')
    reserved = {"CON", "PRN", "AUX", "NUL"}
    reserved.update(f"COM{i}" for i in range(1, 10))
    reserved.update(f"LPT{i}" for i in range(1, 10))
    # Windows also recognizes superscript 1, 2, and 3 in COM/LPT device names.
    reserved.update(f"COM{i}" for i in ("¹", "²", "³"))
    reserved.update(f"LPT{i}" for i in ("¹", "²", "³"))

    for info in infos:
        name = info.filename.rstrip("/") if info.is_dir() else info.filename
        for component in name.split("/"):
            if not component:
                continue
            if component.endswith((".", " ")):
                errors.append(
                    f"ZIP path component has a trailing dot or space: {info.filename}"
                )
            if any(ord(char) < 32 or char in invalid_chars for char in component):
                errors.append(
                    f"ZIP path component contains a Windows-invalid character: {info.filename}"
                )
            # Device names remain reserved before an extension (e.g. CON.txt).
            device_stem = component.split(".", 1)[0].rstrip(" .").upper()
            if device_stem in reserved:
                errors.append(
                    f"ZIP path component uses a reserved Windows device name: {info.filename}"
                )
    return errors



def _local_header_errors(archive: zipfile.ZipFile, infos: list[zipfile.ZipInfo]) -> list[str]:
    """Validate local ZIP headers against central-directory metadata without extraction.

    Different ZIP readers may trust different header fields. Require names, flags,
    compression methods, and (when no data descriptor is used) CRC/size metadata to
    agree, and reject local records whose byte ranges overlap another record or the
    central directory.
    """
    errors: list[str] = []
    stream = archive.fp
    if stream is None:
        return ["ZIP stream is unavailable for local-header validation"]
    central_start = archive.start_dir
    ranges: list[tuple[int, int, str]] = []
    for info in infos:
        offset = info.header_offset
        if offset < 0 or offset + 30 > central_start:
            errors.append(f"ZIP local header offset is outside the data region: {info.filename}")
            continue
        try:
            stream.seek(offset)
            fixed = stream.read(30)
            if len(fixed) != 30:
                errors.append(f"truncated ZIP local header: {info.filename}")
                continue
            (signature, _version, flags, method, _mtime, _mdate, crc, compressed_size,
             uncompressed_size, name_length, extra_length) = struct.unpack("<IHHHHHIIIHH", fixed)
            if signature != 0x04034B50:
                errors.append(f"invalid ZIP local-header signature: {info.filename}")
                continue
            data_offset = offset + 30 + name_length + extra_length
            if data_offset > central_start:
                errors.append(f"ZIP local header extends into central directory: {info.filename}")
                continue
            raw_name = stream.read(name_length)
            raw_extra = stream.read(extra_length)
            if len(raw_name) != name_length or len(raw_extra) != extra_length:
                errors.append(f"truncated ZIP local-header fields: {info.filename}")
                continue
            try:
                local_name = raw_name.decode("utf-8" if flags & 0x800 else "cp437")
            except UnicodeDecodeError:
                errors.append(f"invalid ZIP local-header filename encoding: {info.filename}")
                continue
            if local_name != info.orig_filename:
                errors.append(
                    f"ZIP local-header filename disagrees with central directory: "
                    f"{local_name!r} != {info.orig_filename!r}"
                )
            if flags != info.flag_bits:
                errors.append(f"ZIP local-header flags disagree with central directory: {info.filename}")
            if method != info.compress_type:
                errors.append(f"ZIP local-header compression method disagrees with central directory: {info.filename}")

            # Resolve ZIP64 sizes from the local extra field when the 32-bit
            # fields are sentinels. The ZIP64 extra stores uncompressed then compressed size.
            local_uncompressed = uncompressed_size
            local_compressed = compressed_size
            if uncompressed_size == 0xFFFFFFFF or compressed_size == 0xFFFFFFFF:
                cursor = 0
                zip64_data = None
                while cursor + 4 <= len(raw_extra):
                    field_id, field_size = struct.unpack_from("<HH", raw_extra, cursor)
                    cursor += 4
                    field_data = raw_extra[cursor:cursor + field_size]
                    if len(field_data) != field_size:
                        break
                    cursor += field_size
                    if field_id == 0x0001:
                        zip64_data = field_data
                        break
                if zip64_data is None:
                    errors.append(f"ZIP local header is missing required ZIP64 size data: {info.filename}")
                else:
                    cursor = 0
                    if uncompressed_size == 0xFFFFFFFF:
                        if len(zip64_data) < cursor + 8:
                            errors.append(f"ZIP local header has truncated ZIP64 uncompressed size: {info.filename}")
                        else:
                            local_uncompressed = struct.unpack_from("<Q", zip64_data, cursor)[0]
                            cursor += 8
                    if compressed_size == 0xFFFFFFFF:
                        if len(zip64_data) < cursor + 8:
                            errors.append(f"ZIP local header has truncated ZIP64 compressed size: {info.filename}")
                        else:
                            local_compressed = struct.unpack_from("<Q", zip64_data, cursor)[0]
            has_descriptor = bool(flags & 0x08)
            if not has_descriptor:
                if crc != info.CRC:
                    errors.append(f"ZIP local-header CRC disagrees with central directory: {info.filename}")
                if local_compressed != info.compress_size or local_uncompressed != info.file_size:
                    errors.append(f"ZIP local-header sizes disagree with central directory: {info.filename}")
            else:
                if crc not in (0, info.CRC):
                    errors.append(f"ZIP local-header CRC disagrees with central directory: {info.filename}")
                if local_compressed not in (0, info.compress_size) or local_uncompressed not in (0, info.file_size):
                    errors.append(f"ZIP local-header sizes disagree with central directory: {info.filename}")

            data_end = data_offset + info.compress_size
            if data_end > central_start:
                errors.append(f"ZIP entry data extends into central directory: {info.filename}")
                continue
            record_end = data_end
            if has_descriptor:
                # Data descriptors are another source of parser disagreement:
                # verify their CRC and sizes rather than merely skipping their
                # expected length. The signature is optional, and a CRC can
                # coincidentally equal the signature bytes, so test both legal
                # layouts against the central-directory values.
                zip64_descriptor = (
                    info.file_size > 0xFFFFFFFF
                    or info.compress_size > 0xFFFFFFFF
                    or compressed_size == 0xFFFFFFFF
                    or uncompressed_size == 0xFFFFFFFF
                )
                value_format = "<IQQ" if zip64_descriptor else "<III"
                value_length = struct.calcsize(value_format)
                stream.seek(data_end)
                available = min(4 + value_length, max(0, central_start - data_end))
                descriptor_bytes = stream.read(available)
                expected = (info.CRC, info.compress_size, info.file_size)
                candidates: list[tuple[tuple[int, int, int], int]] = []
                if len(descriptor_bytes) >= value_length:
                    try:
                        candidates.append((struct.unpack_from(value_format, descriptor_bytes, 0), value_length))
                    except struct.error:
                        pass
                if descriptor_bytes[:4] == b"PK\x07\x08" and len(descriptor_bytes) >= 4 + value_length:
                    try:
                        candidates.insert(0, (struct.unpack_from(value_format, descriptor_bytes, 4), 4 + value_length))
                    except struct.error:
                        pass
                matching = next((length for values, length in candidates if values == expected), None)
                if matching is not None:
                    record_end += matching
                elif len(descriptor_bytes) < value_length:
                    errors.append(f"truncated ZIP data descriptor: {info.filename}")
                    record_end += len(descriptor_bytes)
                else:
                    errors.append(f"ZIP data descriptor CRC/sizes disagree with central directory: {info.filename}")
                    # Bound the record using the standard signed layout when
                    # its signature is present; otherwise use the unsigned one.
                    record_end += (4 if descriptor_bytes[:4] == b"PK\x07\x08" else 0) + value_length
            if record_end > central_start:
                errors.append(f"ZIP local record extends into central directory: {info.filename}")
            ranges.append((offset, record_end, info.filename))
        except (OSError, struct.error, ValueError) as exc:
            errors.append(f"ZIP local-header validation failed for {info.filename}: {exc}")

    ranges.sort(key=lambda item: (item[0], item[1], item[2]))
    for previous, current in zip(ranges, ranges[1:]):
        if current[0] < previous[1]:
            errors.append(
                f"overlapping ZIP local records: {previous[2]!r} and {current[2]!r}"
            )
    return errors


def audit_archive(path: str) -> list[str]:
    """Return audit errors; an empty list means the ZIP passed structural checks."""
    errors: list[str] = []
    try:
        with zipfile.ZipFile(path) as archive:
            infos = archive.infolist()
            metadata_errors = _archive_metadata_errors(infos)
            local_header_errors = _local_header_errors(archive, infos)
            entry_type_errors = _archive_entry_type_errors(infos)
            path_collision_errors = _archive_path_collision_errors(infos)
            windows_filename_errors = _windows_filename_errors(infos)
            errors.extend(metadata_errors)
            errors.extend(local_header_errors)
            errors.extend(entry_type_errors)
            errors.extend(path_collision_errors)
            errors.extend(windows_filename_errors)
            # Never decompress a package whose metadata indicates encryption, an
            # unsupported method, or excessive resource requirements.
            payload_read_safe = (
                not metadata_errors and not local_header_errors and not entry_type_errors
                and not path_collision_errors and not windows_filename_errors
            )
            if payload_read_safe:
                try:
                    bad_member = archive.testzip()
                    if bad_member:
                        errors.append(f"CRC/integrity failure in {bad_member}")
                except (NotImplementedError, RuntimeError, zipfile.BadZipFile) as exc:
                    errors.append(f"ZIP integrity check could not safely read entries: {exc}")
                    payload_read_safe = False
            names = [info.filename for info in infos if not info.is_dir()]
            # Count in one pass: avoid quadratic behavior on large or hostile ZIPs.
            seen_names: set[str] = set()
            duplicate_names: set[str] = set()
            for info in infos:
                if info.filename in seen_names:
                    duplicate_names.add(info.filename)
                seen_names.add(info.filename)
                if is_unsafe_archive_path(info.filename.rstrip("/") if info.is_dir() else info.filename):
                    errors.append(f"unsafe archive path: {info.filename}")
                # Keep the Sprint 268 symlink check independent of special-file
                # preflight so the auditor still evaluates the manifest of an
                # otherwise readable archive and reports path-set mismatches.
                unix_mode = info.external_attr >> 16
                if info.create_system == 3 and stat.S_IFMT(unix_mode) == stat.S_IFLNK:
                    errors.append(f"symbolic link archive entry is not allowed: {info.filename}")
            if duplicate_names:
                errors.append("duplicate archive entries: " + ", ".join(sorted(duplicate_names)))
            name_set = set(names)
            missing = sorted(REQUIRED_ENTRIES - name_set)
            if missing:
                errors.append("missing required entries: " + ", ".join(missing))
            for name in names:
                parts = PurePosixPath(name).parts
                if any(part in FORBIDDEN_PARTS for part in parts):
                    errors.append(f"transient directory included: {name}")
                if name.endswith((".pyc", ".pyo")):
                    errors.append(f"compiled Python artifact included: {name}")
                if PurePosixPath(name).name in FORBIDDEN_LOCAL_EVIDENCE:
                    errors.append(f"stale/local test-run artifact included: {name}")
            if "release_manifest.json" in name_set and payload_read_safe:
                try:
                    manifest = json.loads(archive.read("release_manifest.json"), object_pairs_hook=_unique_json_object)
                    if manifest.get("manifest_format") != "retirement-planner-release-manifest":
                        errors.append("release manifest has unsupported or missing manifest_format")
                    if manifest.get("manifest_version") != 1:
                        errors.append("release manifest has unsupported or missing manifest_version")
                    sprint = manifest.get("sprint")
                    if isinstance(sprint, bool) or not isinstance(sprint, int) or sprint < 1:
                        errors.append("release manifest sprint must be a positive integer")
                    files = manifest.get("files")
                    if not isinstance(files, dict):
                        errors.append("release manifest files must be an object")
                    else:
                        file_count = manifest.get("file_count")
                        if isinstance(file_count, bool) or not isinstance(file_count, int) or file_count < 0:
                            errors.append("release manifest file_count must be a non-negative integer")
                        elif file_count != len(files):
                            errors.append("release manifest file_count does not match files")
                        archive_payload = name_set - {"release_manifest.json"}
                        manifest_paths = set(files)
                        if archive_payload != manifest_paths:
                            errors.append("release manifest file paths do not match archive contents")
                        for relative, record in files.items():
                            if not isinstance(relative, str) or not isinstance(record, dict):
                                errors.append(f"release manifest entry is malformed: {relative!r}")
                                continue
                            if is_unsafe_archive_path(relative):
                                errors.append(f"release manifest contains an invalid path; unsafe path: {relative}")
                                continue
                            if relative not in name_set or relative == "release_manifest.json":
                                errors.append(f"release manifest contains an invalid path: {relative}")
                                continue
                            digest = record.get("sha256")
                            size = record.get("size_bytes")
                            if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
                                errors.append(f"release manifest has invalid SHA-256 for {relative}")
                                continue
                            if isinstance(size, bool) or not isinstance(size, int) or size < 0:
                                errors.append(f"release manifest has invalid size for {relative}")
                                continue
                            try:
                                content = archive.read(relative)
                            except KeyError:
                                continue
                            if size != len(content):
                                errors.append(f"release manifest size mismatch for {relative}")
                            if digest != hashlib.sha256(content).hexdigest():
                                errors.append(f"release manifest SHA-256 mismatch for {relative}")
                except (UnicodeDecodeError, json.JSONDecodeError, AttributeError, ValueError) as exc:
                    errors.append(f"release manifest is invalid: {exc}")
            if "data/assumptions.json" in name_set and payload_read_safe:
                try:
                    json.loads(archive.read("data/assumptions.json"))
                except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                    errors.append(f"packaged assumptions JSON is invalid: {exc}")
            if names and all("/" in name for name in names):
                roots = {PurePosixPath(name).parts[0] for name in names}
                if len(roots) == 1 and next(iter(roots)) not in {"data", "planner", "scripts", "tests", "reports", "charts", "docs"}:
                    errors.append("archive appears wrapped in an unexpected top-level directory")
    except (OSError, zipfile.BadZipFile) as exc:
        errors.append(f"cannot read ZIP archive: {exc}")
    return errors


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", help="checkpoint ZIP to audit")
    args = parser.parse_args(argv)
    errors = audit_archive(args.archive)
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print(f"PASS: package structure, required files, assumptions JSON and ZIP integrity: {args.archive}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Sprint 272: reject ZIP path components unsafe on Windows."""
from __future__ import annotations

import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from package_audit import _windows_filename_errors  # noqa: E402


def _info(name: str) -> zipfile.ZipInfo:
    return zipfile.ZipInfo(name)


def test_rejects_reserved_device_names() -> None:
    errors = _windows_filename_errors([_info("CON"), _info("NUL.txt"), _info("COM1.log")])
    assert len(errors) == 3
    assert all("reserved Windows device name" in error for error in errors)


def test_rejects_reserved_device_names_case_insensitively() -> None:
    errors = _windows_filename_errors([_info("docs/aux.md"), _info("reports/lPt9.csv")])
    assert len(errors) == 2


def test_rejects_superscript_reserved_device_names() -> None:
    errors = _windows_filename_errors([_info("COM¹.txt"), _info("LPT³")])
    assert len(errors) == 2


def test_rejects_trailing_dot() -> None:
    errors = _windows_filename_errors([_info("report.")])
    assert len(errors) == 1 and "trailing dot or space" in errors[0]


def test_rejects_trailing_space() -> None:
    errors = _windows_filename_errors([_info("report ")])
    assert len(errors) == 1 and "trailing dot or space" in errors[0]


def test_rejects_alternate_data_stream_colon() -> None:
    errors = _windows_filename_errors([_info("report.txt:payload")])
    assert len(errors) == 1 and "Windows-invalid character" in errors[0]


def test_rejects_windows_invalid_punctuation() -> None:
    errors = _windows_filename_errors([_info('bad<name>.txt'), _info('bad"name.txt'), _info("bad?.txt")])
    assert len(errors) == 3


def test_rejects_control_characters() -> None:
    errors = _windows_filename_errors([_info("bad\x1fname.txt")])
    assert len(errors) == 1 and "Windows-invalid character" in errors[0]


def test_checks_directory_components_and_nested_paths() -> None:
    errors = _windows_filename_errors([_info("CON/") , _info("assets./logo.png")])
    assert len(errors) == 2


def test_accepts_portable_regular_names_and_directories() -> None:
    errors = _windows_filename_errors([_info("planner/docs/guide.md"), _info("assets/"), _info("report-2026.txt")])
    assert errors == []


def test_sprint272_docs_status_and_roadmap_are_traceable() -> None:
    assert (ROOT / "planner/docs/ZIP_WINDOWS_FILENAME_SAFETY.md").is_file()
    assert "Sprint 272" in (ROOT / "PROJECT_STATUS.md").read_text(encoding="utf-8")
    assert "Sprint 272" in (ROOT / "RC4_ROADMAP.md").read_text(encoding="utf-8")

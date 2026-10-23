"""Sprint 271 cross-platform ZIP path alias and file/child collision tests."""
from __future__ import annotations

import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from package_audit import _archive_path_collision_errors  # noqa: E402


def _info(name: str) -> zipfile.ZipInfo:
    return zipfile.ZipInfo(name)


def test_rejects_case_insensitive_path_aliases() -> None:
    errors = _archive_path_collision_errors([_info("README.md"), _info("readme.md")])
    assert len(errors) == 1
    assert "collide after case/Unicode normalization" in errors[0]


def test_rejects_unicode_canonical_equivalence() -> None:
    composed = "caf\u00e9.txt"
    decomposed = "cafe\u0301.txt"
    errors = _archive_path_collision_errors([_info(composed), _info(decomposed)])
    assert len(errors) == 1
    assert "collide after case/Unicode normalization" in errors[0]


def test_rejects_case_collision_in_nested_paths() -> None:
    errors = _archive_path_collision_errors([_info("Docs/Guide.md"), _info("docs/guide.md")])
    assert len(errors) == 1
    assert "collide after case/Unicode normalization" in errors[0]


def test_rejects_file_that_is_parent_of_another_entry() -> None:
    errors = _archive_path_collision_errors([_info("assets"), _info("assets/logo.png")])
    assert any("file path conflicts with a child path" in error for error in errors)


def test_accepts_non_conflicting_case_distinct_paths_in_separate_directories() -> None:
    errors = _archive_path_collision_errors([_info("images/cover.png"), _info("docs/cover.png")])
    assert errors == []


def test_accepts_explicit_directory_with_children() -> None:
    errors = _archive_path_collision_errors([_info("assets/"), _info("assets/logo.png")])
    assert errors == []


def test_rejects_directory_and_file_alias() -> None:
    errors = _archive_path_collision_errors([_info("assets/"), _info("ASSETS")])
    assert any("collide after case/Unicode normalization" in error for error in errors)


def test_sprint271_docs_status_and_roadmap_are_traceable() -> None:
    assert (ROOT / "planner/docs/ZIP_FILENAME_COLLISION_SAFETY.md").is_file()
    assert "Sprint 271" in (ROOT / "PROJECT_STATUS.md").read_text(encoding="utf-8")
    assert "Sprint 271" in (ROOT / "RC4_ROADMAP.md").read_text(encoding="utf-8")

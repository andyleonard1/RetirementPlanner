"""Sprint 267 release-manifest metadata and symlink hardening regressions."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from package_audit import REQUIRED_ENTRIES, audit_archive  # noqa: E402

spec = importlib.util.spec_from_file_location(
    "rc4_release_manifest_sprint267", ROOT / "scripts" / "build_release_manifest.py"
)
assert spec is not None and spec.loader is not None
manifest_builder = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = manifest_builder
spec.loader.exec_module(manifest_builder)


def _entries() -> dict[str, bytes]:
    entries = {
        name: (b'{"ok": true}' if name == "data/assumptions.json" else b"checkpoint")
        for name in REQUIRED_ENTRIES if name != "release_manifest.json"
    }
    manifest = {
        "manifest_format": "retirement-planner-release-manifest",
        "manifest_version": 1,
        "sprint": 267,
        "file_count": len(entries),
        "files": {
            name: {"size_bytes": len(content), "sha256": hashlib.sha256(content).hexdigest()}
            for name, content in entries.items()
        },
    }
    entries["release_manifest.json"] = json.dumps(manifest).encode()
    return entries


def _write_zip(path: Path, entries: dict[str, bytes]) -> None:
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, content in entries.items():
            archive.writestr(name, content)


def test_manifest_rejects_boolean_sprint_number(tmp_path: Path) -> None:
    entries = _entries()
    manifest = json.loads(entries["release_manifest.json"])
    manifest["sprint"] = True
    entries["release_manifest.json"] = json.dumps(manifest).encode()
    path = tmp_path / "bool-sprint.zip"
    _write_zip(path, entries)
    assert any("sprint must be a positive integer" in e for e in audit_archive(str(path)))


def test_manifest_rejects_nonpositive_sprint_number(tmp_path: Path) -> None:
    entries = _entries()
    manifest = json.loads(entries["release_manifest.json"])
    manifest["sprint"] = 0
    entries["release_manifest.json"] = json.dumps(manifest).encode()
    path = tmp_path / "zero-sprint.zip"
    _write_zip(path, entries)
    assert any("sprint must be a positive integer" in e for e in audit_archive(str(path)))


def test_manifest_rejects_boolean_file_count(tmp_path: Path) -> None:
    entries = _entries()
    manifest = json.loads(entries["release_manifest.json"])
    manifest["file_count"] = True
    entries["release_manifest.json"] = json.dumps(manifest).encode()
    path = tmp_path / "bool-count.zip"
    _write_zip(path, entries)
    assert any("file_count must be a non-negative integer" in e for e in audit_archive(str(path)))


def test_manifest_rejects_negative_file_size(tmp_path: Path) -> None:
    entries = _entries()
    manifest = json.loads(entries["release_manifest.json"])
    manifest["files"]["README.md"]["size_bytes"] = -1
    entries["release_manifest.json"] = json.dumps(manifest).encode()
    path = tmp_path / "negative-size.zip"
    _write_zip(path, entries)
    assert any("invalid size for README.md" in e for e in audit_archive(str(path)))


def test_manifest_rejects_boolean_file_size(tmp_path: Path) -> None:
    entries = _entries()
    manifest = json.loads(entries["release_manifest.json"])
    manifest["files"]["README.md"]["size_bytes"] = True
    entries["release_manifest.json"] = json.dumps(manifest).encode()
    path = tmp_path / "bool-size.zip"
    _write_zip(path, entries)
    assert any("invalid size for README.md" in e for e in audit_archive(str(path)))


def test_manifest_rejects_noncanonical_manifest_path(tmp_path: Path) -> None:
    entries = _entries()
    manifest = json.loads(entries["release_manifest.json"])
    record = manifest["files"].pop("README.md")
    manifest["files"][r"folder\README.md"] = record
    manifest["file_count"] = len(manifest["files"])
    entries["release_manifest.json"] = json.dumps(manifest).encode()
    path = tmp_path / "bad-path.zip"
    _write_zip(path, entries)
    assert any("unsafe path" in e for e in audit_archive(str(path)))


def test_manifest_rejects_duplicate_json_object_keys(tmp_path: Path) -> None:
    entries = _entries()
    entries["release_manifest.json"] = (
        b'{"manifest_format":"retirement-planner-release-manifest",'
        b'"manifest_format":"retirement-planner-release-manifest",'
        b'"manifest_version":1,"sprint":267,"file_count":0,"files":{}}'
    )
    path = tmp_path / "duplicate-json-key.zip"
    _write_zip(path, entries)
    assert any("duplicate JSON object key" in e for e in audit_archive(str(path)))


def test_manifest_builder_rejects_file_symlink_outside_root(tmp_path: Path) -> None:
    root = tmp_path / "root"
    root.mkdir()
    external = tmp_path / "external.txt"
    external.write_text("outside", encoding="utf-8")
    link = root / "external.txt"
    try:
        link.symlink_to(external)
    except (OSError, NotImplementedError):
        pytest.skip("symlink creation is unavailable on this platform")
    with pytest.raises(ValueError, match="symbolic links are not allowed"):
        manifest_builder.build_manifest(root, sprint=267)


def test_manifest_builder_rejects_symlinked_directory(tmp_path: Path) -> None:
    root = tmp_path / "root"
    root.mkdir()
    external = tmp_path / "external"
    external.mkdir()
    (external / "payload.txt").write_text("outside", encoding="utf-8")
    try:
        (root / "linked-dir").symlink_to(external, target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("symlink creation is unavailable on this platform")
    with pytest.raises(ValueError, match="symbolic links are not allowed"):
        manifest_builder.build_manifest(root, sprint=267)


def test_sprint267_docs_and_status_are_traceable() -> None:
    assert "Sprint 267" in (ROOT / "PROJECT_STATUS.md").read_text(encoding="utf-8")
    assert "Sprint 267" in (ROOT / "RC4_ROADMAP.md").read_text(encoding="utf-8")
    assert (ROOT / "planner" / "docs" / "RELEASE_MANIFEST_SCHEMA.md").is_file()


def test_manifest_builder_default_sprint_is_current() -> None:
    assert manifest_builder.build_manifest(Path(__file__).resolve().parents[1])["sprint"] == 285

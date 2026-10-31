"""Sprint 265 release manifest generation and verification tests."""
from __future__ import annotations

import importlib.util
import json
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_release_manifest.py"
spec = importlib.util.spec_from_file_location("rc4_release_manifest_sprint265", SCRIPT)
assert spec is not None and spec.loader is not None
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)
sys.path.insert(0, str(ROOT / "scripts"))
from package_audit import REQUIRED_ENTRIES, audit_archive  # noqa: E402


def test_manifest_records_sha256_and_size_for_each_file(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_bytes(b"checkpoint")
    manifest = module.build_manifest(tmp_path, sprint=265)
    assert manifest["manifest_format"] == "retirement-planner-release-manifest"
    assert manifest["manifest_version"] == 1
    assert manifest["sprint"] == 265
    assert manifest["files"]["README.md"] == {
        "size_bytes": 10,
        "sha256": module.sha256_bytes(b"checkpoint"),
    }
    assert manifest["file_count"] == 1


def test_manifest_excludes_itself_and_transient_artifacts(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("ok", encoding="utf-8")
    (tmp_path / "release_manifest.json").write_text("old", encoding="utf-8")
    (tmp_path / "local-collection.json").write_text("{}", encoding="utf-8")
    (tmp_path / "scratch.tmp").write_text("temporary", encoding="utf-8")
    cache = tmp_path / "__pycache__"
    cache.mkdir()
    (cache / "junk.pyc").write_bytes(b"cache")
    manifest = module.build_manifest(tmp_path)
    assert set(manifest["files"]) == {"README.md"}


def test_manifest_generation_is_deterministic(tmp_path: Path) -> None:
    (tmp_path / "a.txt").write_text("a", encoding="utf-8")
    (tmp_path / "b.txt").write_text("b", encoding="utf-8")
    assert module.build_manifest(tmp_path) == module.build_manifest(tmp_path)


def test_write_manifest_serializes_current_manifest(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("ok", encoding="utf-8")
    output = module.write_manifest(tmp_path, sprint=265)
    parsed = json.loads(output.read_text(encoding="utf-8"))
    assert parsed == module.build_manifest(tmp_path, sprint=265)
    assert parsed["file_count"] == 1


def test_package_audit_accepts_valid_manifest(tmp_path: Path) -> None:
    entries = {
        name: (b"{}" if name == "data/assumptions.json" else b"checkpoint")
        for name in REQUIRED_ENTRIES if name != "release_manifest.json"
    }
    manifest = {
        "manifest_format": module.MANIFEST_FORMAT,
        "manifest_version": module.MANIFEST_VERSION,
        "sprint": 265,
        "file_count": len(entries),
        "files": {
            name: {"size_bytes": len(data), "sha256": module.sha256_bytes(data)}
            for name, data in entries.items()
        },
    }
    archive = tmp_path / "valid-manifest.zip"
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as handle:
        for name, data in entries.items():
            handle.writestr(name, data)
        handle.writestr("release_manifest.json", json.dumps(manifest))
    assert audit_archive(str(archive)) == []


def test_package_audit_rejects_manifest_path_set_mismatch(tmp_path: Path) -> None:
    entries = {"README.md": b"checkpoint"}
    manifest = {
        "manifest_format": module.MANIFEST_FORMAT,
        "manifest_version": module.MANIFEST_VERSION,
        "sprint": 265,
        "file_count": 0,
        "files": {},
    }
    archive = tmp_path / "path-mismatch.zip"
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as handle:
        handle.writestr("README.md", entries["README.md"])
        handle.writestr("release_manifest.json", json.dumps(manifest))
    errors = audit_archive(str(archive))
    assert any("file paths do not match archive contents" in error for error in errors)


def test_package_audit_rejects_manifest_size_mismatch(tmp_path: Path) -> None:
    content = b"checkpoint"
    manifest = {
        "manifest_format": module.MANIFEST_FORMAT,
        "manifest_version": 1,
        "sprint": 265,
        "file_count": 1,
        "files": {"README.md": {"size_bytes": 999, "sha256": module.sha256_bytes(content)}},
    }
    archive = tmp_path / "size-mismatch.zip"
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as handle:
        handle.writestr("README.md", content)
        handle.writestr("release_manifest.json", json.dumps(manifest))
    errors = audit_archive(str(archive))
    assert any("size mismatch for README.md" in error for error in errors)


def test_package_audit_rejects_invalid_manifest_digest(tmp_path: Path) -> None:
    manifest = {
        "manifest_format": module.MANIFEST_FORMAT,
        "manifest_version": 1,
        "sprint": 265,
        "file_count": 1,
        "files": {"README.md": {"size_bytes": 1, "sha256": "bad"}},
    }
    archive = tmp_path / "bad-digest.zip"
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as handle:
        handle.writestr("README.md", b"x")
        handle.writestr("release_manifest.json", json.dumps(manifest))
    errors = audit_archive(str(archive))
    assert any("invalid SHA-256 for README.md" in error for error in errors)

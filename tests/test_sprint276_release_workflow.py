"""Sprint 276 release workflow and deterministic archive regression tests."""
from __future__ import annotations

import hashlib
import json
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_release_archive  # noqa: E402
import build_release_manifest  # noqa: E402


def _tiny_release(root: Path) -> None:
    (root / "README.md").write_text("hello release\n", encoding="utf-8")
    build_release_manifest.write_manifest(root, sprint=276)


def test_release_workflow_runs_pytest_before_packaging_and_only_publishes_tags() -> None:
    workflow = (ROOT / ".github/workflows/release.yml").read_text(encoding="utf-8")
    assert "python -m pytest -ra" in workflow
    assert "needs: verify" in workflow
    assert "workflow_dispatch" in workflow
    assert "tags:" in workflow and "'v*'" in workflow
    assert "softprops/action-gh-release@v2" in workflow
    assert "startsWith(github.ref, 'refs/tags/v')" in workflow
    assert "contents: write" in workflow


def test_release_archive_has_sorted_paths_fixed_metadata_and_manifest(tmp_path: Path) -> None:
    _tiny_release(tmp_path)
    first = build_release_archive.build_archive(tmp_path, tmp_path / "one.zip")
    second = build_release_archive.build_archive(tmp_path, tmp_path / "two.zip")
    assert hashlib.sha256(first.read_bytes()).hexdigest() == hashlib.sha256(second.read_bytes()).hexdigest()
    with zipfile.ZipFile(first) as archive:
        assert archive.namelist() == ["README.md", "release_manifest.json"]
        assert all(info.date_time == build_release_archive.FIXED_ZIP_TIME for info in archive.infolist())
        embedded = json.loads(archive.read("release_manifest.json"))
        assert embedded["sprint"] == 276


def test_release_archive_refuses_stale_manifest_hash(tmp_path: Path) -> None:
    _tiny_release(tmp_path)
    (tmp_path / "README.md").write_text("changed after manifest\n", encoding="utf-8")
    try:
        build_release_archive.build_archive(tmp_path, tmp_path / "bad.zip")
    except ValueError as exc:
        assert "manifest hash or size is stale" in str(exc)
    else:
        raise AssertionError("stale manifest should block packaging")


def test_release_archive_refuses_traversal_manifest_path(tmp_path: Path) -> None:
    _tiny_release(tmp_path)
    manifest_path = tmp_path / "release_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["files"]["../outside.txt"] = {"size_bytes": 0, "sha256": hashlib.sha256(b"").hexdigest()}
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    try:
        build_release_archive.build_archive(tmp_path, tmp_path / "bad.zip")
    except ValueError as exc:
        assert "unsafe manifest path" in str(exc)
    else:
        raise AssertionError("traversal path should block packaging")


def test_release_docs_distinguish_artifact_publication_from_source_push() -> None:
    doc = (ROOT / "planner/docs/RELEASE_WORKFLOW.md").read_text(encoding="utf-8")
    assert "does not create a GitHub Release" in doc
    assert "not evidence that source changes were committed to `main`" in doc
    assert "workflow run URL/status" in doc

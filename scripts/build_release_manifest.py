"""Build a SHA-256 manifest for a RetirementPlanner release directory.

Usage: python scripts/build_release_manifest.py [project-root] [--sprint 285]
The manifest excludes itself to avoid a recursive digest.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

MANIFEST_NAME = "release_manifest.json"
MANIFEST_FORMAT = "retirement-planner-release-manifest"
MANIFEST_VERSION = 1
EXCLUDED_PARTS = {".git", ".pytest_cache", "__pycache__", ".venv", "venv", "dist"}
EXCLUDED_SUFFIXES = {".pyc", ".pyo", ".tmp"}
EXCLUDED_NAMES = {MANIFEST_NAME, "local-collection.json", "collection-local.json", "full_test.txt", "sprint275_release_evidence.json", "sprint277_release_evidence.json", "sprint278_release_evidence.json", "sprint279_release_evidence.json", "sprint280_release_evidence.json", "sprint281_release_evidence.json", "sprint282_release_evidence.json", "sprint283_release_evidence.json", "sprint284_release_evidence.json", "sprint285_release_evidence.json"}


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def should_include(path: Path, root: Path) -> bool:
    relative = path.relative_to(root)
    if any(part in EXCLUDED_PARTS for part in relative.parts):
        return False
    if path.name in EXCLUDED_NAMES or path.suffix in EXCLUDED_SUFFIXES:
        return False
    return path.is_file()


def build_manifest(root: Path, sprint: int = 285) -> dict[str, Any]:
    root = root.resolve()
    files: dict[str, dict[str, Any]] = {}
    for path in sorted(root.rglob("*")):
        # A symlink can point outside the release root; never hash its target
        # and accidentally publish an external file as part of the manifest.
        if path.is_symlink():
            raise ValueError(f"symbolic links are not allowed in release inputs: {path.relative_to(root).as_posix()}")
        if not should_include(path, root):
            continue
        relative = path.relative_to(root).as_posix()
        content = path.read_bytes()
        files[relative] = {"size_bytes": len(content), "sha256": sha256_bytes(content)}
    return {
        "manifest_format": MANIFEST_FORMAT,
        "manifest_version": MANIFEST_VERSION,
        "sprint": sprint,
        "file_count": len(files),
        "files": files,
    }


def write_manifest(root: Path, sprint: int = 285) -> Path:
    root = root.resolve()
    manifest = build_manifest(root, sprint=sprint)
    destination = root / MANIFEST_NAME
    destination.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return destination


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path, default=Path.cwd(), help="project root directory")
    parser.add_argument("--sprint", type=int, default=285, help="sprint number recorded in the manifest")
    args = parser.parse_args()
    path = write_manifest(args.root, sprint=args.sprint)
    manifest = json.loads(path.read_text(encoding="utf-8"))
    print(f"Wrote {path} ({manifest['file_count']} files, Sprint {manifest['sprint']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Reconcile release evidence against one final source tree and checkpoint ZIP.

This validates consistency; it does not execute tests and never treats a collection
count as proof that tests passed. Run from the repository root:
    python scripts/release_evidence.py --collection reports/sprint275_collection_report.json \
        --archive path/to/checkpoint.zip --output reports/sprint275_release_evidence.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import zipfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_collection_against_tree(report: dict[str, Any], root: Path) -> list[str]:
    """Check collection structure and prove its referenced files/config are current."""
    from test_collection_report import validate_report

    errors = validate_report(report)
    for field in ("test_file_sha256", "config_sha256"):
        values = report.get(field, {})
        for relative, expected in values.items():
            path = root / relative
            if not path.is_file():
                errors.append(f"{field} references missing file: {relative}")
            elif sha256_file(path) != expected:
                errors.append(f"{field} is stale for: {relative}")
    for relative in report.get("counts_by_file", {}):
        if not (root / relative).is_file():
            errors.append(f"collection references missing test file: {relative}")
    return errors


def validate_manifest_against_tree(manifest: dict[str, Any], root: Path) -> list[str]:
    """Compare a release manifest with files in the current tree, excluding itself."""
    from build_release_manifest import build_manifest

    errors: list[str] = []
    try:
        current = build_manifest(root, sprint=manifest.get("sprint", 285))
    except (OSError, ValueError) as exc:
        return [f"could not rebuild source manifest: {exc}"]
    if manifest.get("manifest_format") != current["manifest_format"]:
        errors.append("manifest_format differs from current source manifest")
    if manifest.get("manifest_version") != current["manifest_version"]:
        errors.append("manifest_version differs from current source manifest")
    if manifest.get("file_count") != len(manifest.get("files", {})):
        errors.append("manifest file_count does not match files object")
    old_files = manifest.get("files")
    if not isinstance(old_files, dict):
        errors.append("manifest files must be an object")
        return errors
    current_files = current["files"]
    missing = sorted(set(current_files) - set(old_files))
    extra = sorted(set(old_files) - set(current_files))
    if missing:
        errors.append("manifest missing source files: " + ", ".join(missing[:10]))
    if extra:
        errors.append("manifest contains stale/extra files: " + ", ".join(extra[:10]))
    for relative in sorted(set(current_files) & set(old_files)):
        if old_files[relative] != current_files[relative]:
            errors.append(f"manifest size/hash is stale for: {relative}")
    return errors


def validate_archive_inventory(archive_path: Path, manifest: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    try:
        with zipfile.ZipFile(archive_path) as archive:
            names = [info.filename for info in archive.infolist() if not info.is_dir()]
            if len(names) != len(set(names)):
                errors.append("archive contains duplicate file entries")
            expected = set(manifest.get("files", {})) | {"release_manifest.json"}
            actual = set(names)
            if actual != expected:
                missing = sorted(expected - actual)
                extra = sorted(actual - expected)
                if missing:
                    errors.append("archive missing entries: " + ", ".join(missing[:10]))
                if extra:
                    errors.append("archive has unmanifested entries: " + ", ".join(extra[:10]))
            # Ensure the manifest embedded in the archive is the evidence supplied.
            try:
                embedded = json.loads(archive.read("release_manifest.json"))
                if embedded != manifest:
                    errors.append("embedded release_manifest.json differs from supplied manifest")
            except (KeyError, json.JSONDecodeError, UnicodeDecodeError):
                errors.append("archive release_manifest.json is missing or invalid JSON")
    except (OSError, zipfile.BadZipFile) as exc:
        errors.append(f"could not inspect checkpoint ZIP: {exc}")
    return errors


def reconcile(root: Path, collection_path: Path, archive_path: Path) -> dict[str, Any]:
    errors: list[str] = []
    collection_loaded = False
    manifest_loaded = False
    try:
        collection = json.loads(collection_path.read_text(encoding="utf-8"))
        if not isinstance(collection, dict):
            raise ValueError("collection report root must be an object")
        collection_loaded = True
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        collection = {}
        errors.append(f"collection report cannot be read: {exc}")
    try:
        manifest = json.loads((root / "release_manifest.json").read_text(encoding="utf-8"))
        if not isinstance(manifest, dict):
            raise ValueError("release manifest root must be an object")
        manifest_loaded = True
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        manifest = {}
        errors.append(f"release manifest cannot be read: {exc}")
    if collection_loaded:
        errors.extend("collection: " + error for error in validate_collection_against_tree(collection, root))
    if manifest_loaded:
        errors.extend("manifest: " + error for error in validate_manifest_against_tree(manifest, root))
        errors.extend("archive: " + error for error in validate_archive_inventory(archive_path, manifest))
    return {
        "report_format": "retirement-planner-release-evidence-reconciliation",
        "report_version": 1,
        "sprint": manifest.get("sprint", 285),
        "source_root": root.name,
        "collection_report": str(collection_path),
        "collected_test_count": collection.get("total_collected"),
        "collection_test_file_count": collection.get("test_file_count"),
        "archive": archive_path.name,
        "manifest_file_count": manifest.get("file_count"),
        "archive_sha256": sha256_file(archive_path) if archive_path.is_file() else None,
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "test_execution_status": "NOT_VERIFIED_BY_THIS_REPORT",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--collection", type=Path, required=True)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    result = reconcile(args.root.resolve(), args.collection.resolve(), args.archive.resolve())
    serialized = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(serialized, encoding="utf-8")
    print(serialized, end="")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

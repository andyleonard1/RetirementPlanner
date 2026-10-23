"""Build a deterministic ZIP from a validated release manifest.

Usage: python scripts/build_release_archive.py PROJECT_ROOT OUTPUT_ZIP

The output is stable for identical payload bytes and manifest contents: entries
are sorted, timestamps and Unix file modes are fixed, and no parent directory is
added to archive paths. The manifest itself is included as the final entry.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import stat
import zipfile
from pathlib import Path, PurePosixPath

MANIFEST_NAME = "release_manifest.json"
FIXED_ZIP_TIME = (2020, 1, 1, 0, 0, 0)


def build_archive(root: Path, output: Path) -> Path:
    root = root.resolve()
    manifest_path = root / MANIFEST_NAME
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    files = manifest.get("files")
    if not isinstance(files, dict):
        raise ValueError("release manifest files must be an object")
    output = output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for relative in sorted(files):
            posix_path = PurePosixPath(relative)
            if posix_path.is_absolute() or not posix_path.parts or ".." in posix_path.parts or "\\" in relative:
                raise ValueError(f"unsafe manifest path: {relative!r}")
            source = root.joinpath(*posix_path.parts)
            if source.is_symlink() or not source.is_file():
                raise ValueError(f"manifest path is missing or is a symlink: {relative}")
            content = source.read_bytes()
            expected = files[relative]
            digest = hashlib.sha256(content).hexdigest()
            if expected.get("size_bytes") != len(content) or expected.get("sha256") != digest:
                raise ValueError(f"manifest hash or size is stale for: {relative}")
            info = zipfile.ZipInfo(relative, date_time=FIXED_ZIP_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = (stat.S_IFREG | 0o644) << 16
            archive.writestr(info, content, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
        manifest_info = zipfile.ZipInfo(MANIFEST_NAME, date_time=FIXED_ZIP_TIME)
        manifest_info.compress_type = zipfile.ZIP_DEFLATED
        manifest_info.create_system = 3
        manifest_info.external_attr = (stat.S_IFREG | 0o644) << 16
        archive.writestr(manifest_info, manifest_path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    result = build_archive(args.root, args.output)
    print(f"Built deterministic release ZIP: {result}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

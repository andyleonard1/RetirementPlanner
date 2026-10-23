# Release Manifest and Artifact Integrity

Sprint 265 adds a deterministic SHA-256 manifest to release checkpoint ZIPs.

## Build the manifest

From the project root, before creating the ZIP:

```bash
python scripts/build_release_manifest.py . --sprint 265
```

The script writes `release_manifest.json`. It records the sprint number and, for every packaged file other than the manifest itself, the relative POSIX path, byte size and SHA-256 digest. It excludes itself, VCS/cache/virtual-environment directories, compiled Python files, and local test-run evidence files that the package audit already forbids.

## Verify the ZIP

```bash
python scripts/package_audit.py path/to/checkpoint.zip
```

The audit checks manifest format/version, file count, exact path coverage, file sizes and SHA-256 digests, alongside the existing required-file, unsafe-path, transient-artifact, assumptions JSON and ZIP CRC checks. A manifest is an integrity check, not a digital signature: it detects accidental or unsynchronised changes, but does not prove who produced the package.

The manifest must be regenerated after any package file changes and before the final ZIP is built.

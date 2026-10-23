# Sprint 273 — ZIP Local-Header Integrity

Release archives contain both local file headers and central-directory records. Different ZIP readers can rely on different copies of this metadata, so a disagreement can cause the same archive to be interpreted differently by an auditor and an extractor.

The release auditor now checks local records before CRC validation or payload decompression. It verifies:

- the local-header signature and bounded header/name/extra-field lengths;
- the local filename, general-purpose flags, and compression method against central-directory metadata;
- CRC and compressed/uncompressed sizes when data descriptors are not used, including ZIP64 size fields;
- data boundaries against the central directory and overlaps between local records.

Malformed or conflicting local records block payload reads. The checks complement the existing canonical path, filename portability, case/Unicode collision, duplicate-entry, special-file, compression/resource-limit, and SHA-256 release-manifest checks.

The ZIP is audited in place; no extraction occurs. SHA-256 manifests provide integrity checks but are not digital signatures. Sprint 273 does not modify production financial calculations, assumptions defaults, or the golden scenario baseline.

## Validation

Run the focused checks with:

```powershell
python -m pytest -q tests/test_sprint273_zip_local_header_integrity.py
python -m pytest -q tests/test_sprint269_zip_metadata_resource_limits.py tests/test_sprint270_zip_special_file_metadata.py tests/test_sprint271_zip_filename_collisions.py tests/test_sprint272_windows_filename_safety.py tests/test_sprint273_zip_local_header_integrity.py
```

Audit a release ZIP with:

```powershell
python scripts/package_audit.py path\to\checkpoint.zip
```

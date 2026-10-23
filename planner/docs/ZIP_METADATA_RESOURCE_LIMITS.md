# ZIP Metadata and Resource Limits (Sprint 269)

The release package auditor performs a central-directory preflight **before** running ZIP CRC validation or reading manifest/assumptions payloads. This avoids blindly decompressing archives whose metadata advertises risky or unsupported content.

The current acceptance limits are:

- At most 10,000 ZIP entries.
- At most 32 MiB uncompressed per entry.
- At most 256 MiB total advertised uncompressed data.
- At most a 200:1 uncompressed-to-compressed ratio for any non-empty entry.
- No encrypted entries, zero compressed size for non-empty content, or compression methods other than ZIP Stored and Deflate.

These checks use ZIP central-directory metadata as a preflight, not as proof that a file is safe. Accepted entries still pass CRC validation and the release-manifest size/SHA-256 checks. A malformed archive can lie about metadata, so the audit still treats decompression/CRC errors as failures. Limits are intentionally generous for this repository's source, test, and evidence files; revise them only with a documented release need and regression tests.

Run the checks from the repository root:

```powershell
python -m pytest -q tests/test_sprint269_zip_metadata_resource_limits.py
python scripts/package_audit.py path\to\checkpoint.zip
```

The release manifest is an integrity inventory, not a digital signature. No production financial calculation logic, assumptions defaults, or golden baseline is changed by these package checks.

# Sprint 271 — ZIP Filename Collision Safety

Release archives must behave consistently when extracted on Windows, POSIX, and filesystems that normalize Unicode filenames. The package auditor therefore compares archive member paths using Unicode NFC normalization and case folding, rejecting distinct names that alias under those rules.

The audit also rejects a regular file used as the parent of another archive member (for example, `assets` together with `assets/logo.png`), because extractors cannot materialize both paths consistently. Explicit directory entries with child files remain valid.

These checks complement exact duplicate-name detection, canonical path validation, Unix special-file checks, and ZIP resource limits. They run during archive metadata inspection, before CRC checks or payload decompression. The release manifest continues to hash the exact canonical paths and bytes; it does not override path-collision rejection.

Run the focused tests with:

```powershell
python -m pytest -q tests/test_sprint271_zip_filename_collisions.py tests/test_sprint270_zip_special_file_metadata.py
```

No financial calculation logic, assumptions defaults, or golden baseline is changed by this sprint.

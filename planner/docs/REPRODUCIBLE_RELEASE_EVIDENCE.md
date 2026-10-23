# Reproducible Release Evidence (Sprint 275)

## Purpose

A release checkpoint needs a consistent set of evidence tied to the same source tree and ZIP. Test collection is not test execution: this workflow never reports a test pass based on the number of collected node IDs.

## Recommended sequence

Run these commands from the repository root after the final source and test changes:

1. `python -m pytest --collect-only -q` to inspect the collection count.
2. `python scripts/test_collection_report.py --output reports/sprint275_collection_report.json` to record node IDs, per-test-file SHA-256 hashes, and test configuration hashes.
3. `python -m pytest -ra` (or run every documented deterministic partition and retain each result) to execute tests. Record passed, skipped, failed, and duration separately; do not infer outcomes from collection.
4. `python -m compileall -q .` and parse `data/assumptions.json` without modifying it.
5. `python scripts/build_release_manifest.py . --sprint 275` to hash the final payload tree.
6. Create the checkpoint ZIP using the established release packaging process, with `release_manifest.json` at the archive root.
7. `python scripts/package_audit.py path/to/checkpoint.zip` to run archive security, inventory, manifest hash/size and CRC checks.
8. `python scripts/release_evidence.py --collection reports/sprint275_collection_report.json --archive path/to/checkpoint.zip --output reports/sprint275_release_evidence.json` to reconcile the collection report, current source tree, manifest and ZIP inventory.

If any source or test file changes after step 2, regenerate the collection report and rerun tests. If any payload file changes after step 5, rebuild the manifest and ZIP and rerun both archive audit and reconciliation. Evidence JSON records archive SHA-256 so the exact ZIP can be identified.

## What the reconciler checks

- Collection-report structure, unique node IDs and counts.
- Every referenced test file and configuration hash against the current source tree.
- Manifest file count, payload path set, file sizes and SHA-256 values against the current source tree.
- Exact archive file inventory against manifest paths plus `release_manifest.json`.
- Equality of the embedded archive manifest and the source manifest.
- ZIP SHA-256 for identifying the tested artifact.

The reconciler explicitly emits `test_execution_status: NOT_VERIFIED_BY_THIS_REPORT`. It does not execute pytest and cannot establish a passing test result. A passing reconciliation only means the supplied evidence is internally consistent with the selected source tree and archive; keep actual pytest output as separate release evidence.

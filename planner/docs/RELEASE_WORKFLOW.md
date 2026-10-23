# Release Workflow and GitHub Publication (Sprint 276)

## Local checkpoint procedure

Run these commands from the repository root after all source and test edits are complete:

1. Install the test dependencies: `python -m pip install pytest pypdf -r planner/requirements.txt`.
2. Execute the suite: `python -m pytest -ra`. Save the complete output; collection totals are not test results.
3. Run `python -m compileall -q .` and validate `data/assumptions.json` with Python's JSON parser.
4. Capture current collection evidence: `python scripts/test_collection_report.py --output reports/sprint276_collection_report.json`.
5. Build the source manifest: `python scripts/build_release_manifest.py . --sprint 276`.
6. Build the deterministic ZIP: `python scripts/build_release_archive.py . dist/RetirementPlanner_RC4_Sprint276.zip`.
7. Audit the ZIP: `python scripts/package_audit.py dist/RetirementPlanner_RC4_Sprint276.zip`.
8. Reconcile source, collection report, manifest and ZIP: `python scripts/release_evidence.py --collection reports/sprint276_collection_report.json --archive dist/RetirementPlanner_RC4_Sprint276.zip --output dist/sprint276_release_evidence.json`.
9. Retain the ZIP, reconciliation JSON, full pytest output and archive SHA-256 together. A reconciliation PASS does not replace test-execution evidence.

If any test/configuration changes after step 4, regenerate the collection report and rerun tests. If a payload file changes after step 5, rebuild the manifest and ZIP, then rerun the audit and reconciliation.

## GitHub Actions behavior

- `.github/workflows/release.yml` runs the full pytest suite, compilation and assumptions JSON validation before packaging.
- `workflow_dispatch` builds and uploads a 30-day workflow artifact; it does not create a GitHub Release.
- Pushing a version tag matching `v*` runs the same checks and publishes the checkpoint ZIP and evidence JSON to a GitHub Release using the repository-provided `GITHUB_TOKEN`.
- The workflow records the workflow artifact/release output separately from whether a local checkpoint was manually copied or pushed to a repository branch. A successful artifact upload is not evidence that source changes were committed to `main`.
- GitHub Actions must pass the `verify` job before the `package` job starts. A failed test run prevents publication.

## Publication record

For every actual remote update, record repository, branch or tag, commit SHA, workflow run URL/status, artifact or release URL, and verification time. Never infer a successful push or release from a locally built ZIP. This checkpoint's workflow configuration is implemented locally; remote publication is a separate operation and is only confirmed when GitHub returns the resulting commit/ref or release URL.

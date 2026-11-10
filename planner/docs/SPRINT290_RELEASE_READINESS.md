# Sprint 290 — RC4 Release Candidate Readiness

## Scope and source

Sprint 290 completed a release-candidate verification pass against committed source revision `e79bf1cbc251bd6df9f4c1b1dce31bfa2506ee70` on branch `integration/sprint-285-source-import`. The source was exported with Git metadata excluded into a clean staging directory. This checkpoint records verification only; it does not grant formal release approval.

No production financial calculation logic, shipped assumptions defaults, or golden baseline values were changed.

## Test and source validation

| Check | Result |
|---|---|
| Full Windows pytest run | **1,560 passed, 2 skipped, 0 failed** in 134.55 seconds |
| Test collection | **1,562 items across 180 test files** |
| Python / pytest | Python 3.14.6 / pytest 9.1.1 |
| Python compilation | `python -m compileall -q .` passed |
| Assumptions JSON | `data/assumptions.json` parsed successfully |
| Staged source export | 479 files from the committed source revision |
| Protected golden baselines | Both SHA-256 values matched before and after packaging |

The two skipped tests are the known Windows symlink-creation limitations in `tests/test_sprint267_manifest_schema_hardening.py:134` and `:148`. They are platform-related skips, not failures. The collection count is not an execution pass count.

### Protected golden-baseline SHA-256

- `tests/golden/baseline.json`: `A9C51CB9161E0874B42F5A4B62C92C8EDC845AA83D8EB49B977BCB18475F6EB6`
- `tests/golden/sprint284_scenarios.json`: `F1981FDD7C9CA12F90A72D3A34C8037BB6103C013A76D171109F1A22769F5A34`

## Manifest, archive and evidence

- Sprint 290 release manifest: **477 files**.
- Deterministic archive build: completed successfully.
- Package audit: **PASS** — package structure, required files, assumptions JSON and ZIP integrity.
- Release-evidence reconciliation: **PASS**, with **zero errors**; 1,562 collected tests, 180 test files and 477 manifest entries.
- The reconciliation report records `test_execution_status: NOT_VERIFIED_BY_THIS_REPORT`. This is expected: the report reconciles evidence and archive contents; the separate pytest result above is the test-execution evidence.

### Candidate archive

- Local archive: `C:\\Temp\\RetirementPlanner_Sprint290_RC4_e79bf1c.zip`
- Local collection report: `C:\\Temp\\sprint290_collection_report.json`
- Local release-evidence report: `C:\\Temp\\sprint290_release_evidence.json`
- SHA-256: `8664d190167a6c245574db5a433cc8456a08149e30eb77725553ad414859aea8`

An independent PowerShell `Get-FileHash -Algorithm SHA256` calculation matched the archive hash in the reconciliation report.

The ZIP and supporting JSON reports remain local in the Windows Temp directory; they have not been committed to the repository.

## Outcome and publication boundary

**Recommendation: Sprint 290 passes the technical release-candidate readiness checks performed in the target Windows environment.**

This is a technical readiness recommendation, not formal release approval. No release tag or GitHub Release has been created. Formal publication remains a separate action requiring explicit authorisation.


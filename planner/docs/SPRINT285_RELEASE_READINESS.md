# Sprint 285 — Release Readiness

## Purpose

Sprint 285 consolidates the RC4 release-readiness checks into a traceable checkpoint. It adds automated checks that the current sprint manifest includes this sprint's artifacts, the release checklist names its required gates, and the shipped assumptions and existing golden baseline remain unchanged.

## Required acceptance sequence

From the extracted project root:

1. Run `python -m pytest -ra` and record passed, skipped, failed and error counts.
2. Run `python -m compileall -q .`.
3. Parse `data/assumptions.json` and confirm it has not been rewritten by release preparation.
4. Build the release manifest and deterministic archive using the documented scripts.
5. Run `python scripts/package_audit.py path/to/checkpoint.zip` and `python scripts/release_evidence.py` with the current collection report and archive.
6. Inspect the final ZIP and verify the manifest digest and inventory correspond to the same source tree.
7. Record any platform-specific skips and confirm all required gates have actually run before describing the checkpoint as release-ready.

## Boundaries

This sprint changes release traceability and regression checks only. It does not change production financial calculations, assumptions defaults, tax treatment, State Pension logic, withdrawal order, Monte Carlo behavior or the reviewed golden fixture. The expected SHA-256 digests of `data/assumptions.json` and `tests/golden/baseline.json` are asserted in the Sprint 285 tests.

## Evidence policy

A collection report states which tests pytest discovers; it does not show that they passed. A package audit checks archive structure and integrity; it does not execute the tests. A release-evidence reconciliation checks consistency between source, manifest, collection report and archive; its `test_execution_status` remains `NOT_VERIFIED_BY_THIS_REPORT`. Full-suite acceptance requires a completed test run in the target environment. For this authoring checkpoint, full-suite acceptance is pending the user's local `python -m pytest -ra` result.

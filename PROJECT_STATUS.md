# Retirement Planner

## Current Version

2.0 RC2

## Current Sprint

Sprint 39 - Documentation and Architecture Consolidation

## Branch

rc2-architecture

## Build Status

| Application | Status |
|-------------|--------|
| main.py | ✅ |
| create_report.py | ✅ |
| monte_carlo.py | ✅ |
| compare.py | ✅ |
| recommend.py | ✅ |
| health_check.py | ✅ |

## Completed

- Retirement timeline
- Pension engine
- ISA engine
- Savings engine
- Tax engine
- Cash Flow engine
- Withdrawal engine
- Summary engine
- Recommendation engine
- Health engine
- Goal engine
- Monte Carlo simulation
- PDF report
- Sensitivity analysis reporting
- Charts
- Optimisation prototype
- Standard result objects for scenario, decision, risk and histogram engines

## Sprint 35 Result Standardisation

- Added `ScenarioResult`, `DecisionResult`, `RiskResult` and `HistogramResult`.
- Migrated ScenarioEngine, DecisionEngine, RiskEngine and HistogramEngine to return result objects.
- Retained read-only `result["field"]` compatibility for existing callers during migration.
- Added four result-contract tests.
- `create_report.py` continues to generate the PDF successfully.
- Full test suite: 119 tests passing.

## Sprint 36 Optimisation Framework Consolidation

- Consolidated the optimisation traversal and limit calculation into `OptimisationEngine`.
- `TaxOptimizerEngine` now reuses the shared framework with its historical basic-rate-band policy.
- Added `OptimiserEngine` as the British-spelling compatibility alias.
- Added three optimisation framework regression tests.
- Existing planner behaviour remains unchanged.
- Full test suite: 125 tests passing.

## Technical Debt

### High

- Documentation expansion

### Medium

- Documentation expansion
- Additional integration coverage

### Low

- Documentation expansion
- Test coverage improvements

## Engineering Score

Architecture        8.8 / 10

Maintainability     8.3 / 10

Extensibility       9.0 / 10

Documentation       6.0 / 10

Testing             5.8 / 10

Overall             8.7 / 10

## Sensitivity checkpoint 23
- 27 real planner cases executed.
- Recommended ages: 56 (18 cases), 58 (3 cases), 67 (6 cases).
- Range: 56-67.
- Informational only; live recommendation unchanged.

## Sensitivity reporting checkpoint 24
- 27 real planner cases are calculated during PDF report generation.
- Recommended ages: 56 (18 cases), 58 (3 cases), 67 (6 cases).
- Range: 56-67.
- Driver breakdown for pension growth, net spending and ISA growth is included in the PDF.
- Sensitivity remains informational only; the live recommendation is unchanged.
- Full test suite: 115 tests passing.


## Sprint 37 Logging Consistency

- Replaced recommendation-engine diagnostic stdout with module logging at DEBUG level.
- Replaced validation warnings printed directly to stdout with module logging at WARNING level.
- Added two regression tests covering the logging contract.
- Full test suite: 127 tests passing.
- create_report.py, recommend.py and health_check.py continue to run successfully.


## Sprint 38 Typed Interfaces and Engine Contracts

- Added structural Protocol contracts in `planner/contracts.py`.
- Defined contracts for assumptions access, timeline construction, timeline transformation, summary generation and validation.
- Added type annotations to the core timeline-processing engines without changing runtime behaviour.
- Added four contract tests covering the shared interfaces and representative engines.
- Full test suite: 131 tests passing.
- `create_report.py`, `recommend.py` and `health_check.py` continue to run successfully.


## Sprint 39 Documentation and Architecture Consolidation

- Reworked the README to describe the current application rather than the obsolete V5 feature list.
- Expanded architecture documentation with layer responsibilities and dependency rules.
- Added `planner/docs/ENGINE_CATALOG.md` as a component/responsibility reference.
- Consolidated coding standards, assumptions guidance, roadmap and release notes.
- Added the Sprint 39 architecture/documentation entry to the changelog.
- No calculation code was changed.
- Baseline validation remains 131 tests passing.

## Sprint 40 — Integration-Test Strengthening

- Added `tests/test_integration_pipeline.py` covering the real planner result pipeline.
- Added scenario-manager → decision → recommendation integration coverage.
- Added recommendation/risk → legacy report adapter integration coverage.
- Added real timeline → chart generation → PDF creation coverage.
- Verified `recommend.py` and `health_check.py` continue to run successfully.
- Full suite: **135 tests passing** (6 subtests).
- No retirement calculation logic changed.

## Sprint 41 — End-to-End CLI and Report Testing

- Added `tests/test_cli_entrypoints.py` covering the public command-line workflows.
- Added end-to-end checks for `main.py`, `recommend.py`, `health_check.py` and `create_report.py`.
- CLI tests execute the real scripts in clean temporary project copies and verify successful exit codes and key user-facing output.
- PDF CLI coverage verifies that `RetirementReport.pdf` is actually created and has non-trivial content.
- No retirement calculation logic changed.
- Full suite: **139 tests passing** (6 subtests).

## Sprint 43 — Configuration and Schema Validation

- Added `planner/assumptions_schema.py` as the central structural configuration contract.
- Validates required assumption keys, numeric/string/boolean types, finite numeric values and goal structure before domain validation.
- Unknown configuration keys are retained for forward compatibility and logged as warnings.
- Existing range/business rules remain in `ValidationEngine`.
- Added seven schema/regression tests and updated the missing-assumption resilience expectation.
- No retirement calculation logic changed.
- Full suite: **154 tests passing** (6 subtests).
- `recommend.py`, `health_check.py` and `create_report.py` continue to run successfully.

## Sprint 44 — Schema Documentation and Configuration Editing Safety

- Expanded `planner/docs/assumptions.md` with the structural schema contract and safe-editing workflow.
- Added `Assumptions.validate()` as the explicit validation boundary for in-memory configuration.
- Changed `Assumptions.save()` to validate before persistence and reject invalid changes without touching the existing file.
- Made configuration writes atomic using a temporary file followed by `os.replace`.
- Added regression tests for valid persistence, invalid structural/domain values, non-finite values, validation without writing and forward-compatible unknown keys.
- No retirement calculation logic changed.

## Sprint 45 — Configuration Change Tracking and Auditability

- Added `AssumptionChange` and lightweight configuration change tracking to `Assumptions`.
- `changes()` reports key, nested-path, added and removed configuration differences since the last load or successful save.
- `has_changes()` provides a simple dirty-state check.
- `reset_change_tracking()` allows an application to explicitly accept the current in-memory state as its audit baseline without writing it.
- Successful `Assumptions.save()` now establishes the persisted configuration as the new audit baseline.
- Nested goal edits are detected through full configuration snapshot comparison.
- Added six auditability regression tests.
- Updated assumptions documentation with the audit contract and its deliberate scope.
- No retirement calculation logic changed.
- Full suite: **166 tests passing** (6 subtests).
- `recommend.py`, `health_check.py` and `create_report.py` continue to run successfully.

## Sprint 48 — Audit/Report Quality

- Added human-readable descriptions for audited assumption changes.
- Added display-safe before/after values, including unset values.
- Updated console recommendation reporting to present the explanation separately from the raw path/value change.
- Updated PDF reporting with the same human-readable audit presentation and compatibility fallback for older result objects.
- Added six regression tests covering descriptions, context wording, value formatting, and console output.
- Full suite: 184 tests passing, 6 subtests.

## Sprint 50 — Audit Completeness

- Added `planner/audit_catalog.py` as the central catalogue for human-readable assumption-change descriptions.
- The catalogue is checked automatically against every schema-defined assumption key.
- Added explicit descriptions for all current top-level schema fields and retirement-goal nested paths.
- Added deterministic fallback descriptions for future/unknown paths.
- Updated `RecommendationReportAdapter` to use the central catalogue rather than an ad-hoc description map.
- Added eight regression tests covering schema-field coverage, nested goals, fallbacks and context-specific retirement-age wording.
- No retirement calculation logic changed.
- Full suite: **192 tests passing** (6 subtests).
- `recommend.py`, `health_check.py` and `create_report.py` continue to run successfully.

## Sprint 51 — Optimisation Policy Comparison

- Expanded `OptimisationEngine` with an explicit supported-policy catalogue and descriptions.
- Added a read-only `calculate()` API for policy limits without mutating timeline objects.
- Added a read-only `compare_policies()` API for comparing the Personal Allowance and Basic-rate-band policies over the same timeline.
- Added clear validation errors for unknown optimisation policies.
- Preserved the existing `apply()` behaviour used by the live planner and `TaxOptimizerEngine` compatibility wrapper.
- Added eight optimisation framework regression tests.
- No retirement calculation rules were changed; the new comparison API reuses the existing limit calculations.
- Full suite: **198 tests passing** (6 subtests).
- `recommend.py`, `health_check.py` and `create_report.py` continue to run successfully.

## Sprint 53

Optimisation decision support added; 205 tests passing.

## RC4 Sprint 62 — Sequence-of-Returns Risk

- Added isolated sequence-of-returns risk analysis with withdrawal support.
- Added 7 focused regression tests.
- Deterministic retirement engines remain unchanged.
- Sprint 61 protected baseline: 241 tests passing.
- Sprint 62 focused tests: 7 passing.

## Sprint 102 — Desktop Scenario Comparison GUI

- Added an optional Tkinter desktop presentation for the scenario projection view model.
- Added scenario cards, ending-balance summary and year-level projection table.
- GUI formatting is calculation-free and consumes `ScenarioProjectionViewModel` only.
- Tkinter is imported lazily so headless/core planner workflows remain unaffected.
- Added GUI regression coverage without opening a desktop window during tests.

## Sprint 103 — GUI Input Binding & Scenario Selection

- Added `ScenarioProjectionInputs` as an immutable GUI/application input contract.
- Added `ScenarioProjectionApplication` as the orchestration boundary between assumptions, portfolio statistics, scenario comparison and the GUI view model.
- GUI edits are applied to assumptions in memory and validated; persistence remains explicit via `Assumptions.save()`.
- Added selected-scenario support without changing the underlying financial engines.
- Added seven regression tests covering input validation, binding, scenario selection and calculation-boundary behaviour.

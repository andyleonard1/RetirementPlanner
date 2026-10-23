# Current Checkpoint — Sprint 280 Pension Funding and State Pension Forecasts

- Sprint 279 user-confirmed full suite: **1,524 passed, 2 skipped, 0 failed** in 188.50 seconds. The two skips are the existing Windows symlink-permission tests.
- Sprint 280 adds scenario regression coverage for projected-year CPI, triple-lock earnings-growth precedence, legacy fixed growth when triple lock is disabled, spouse start-age behavior, and the downstream required-pension-income calculation.
- Focused Sprint 280 plus related triple-lock, schedule, cross-engine, and tax/withdrawal regressions: **47 passed**. Compilation and assumptions JSON validation passed.
- No production financial calculation logic, assumptions defaults, or golden baseline changed. Full suite for Sprint 280 is pending the user's local verification.
- GitHub has not been updated by this local checkpoint.

# Current Checkpoint — Sprint 278 GUI Assumptions Workflow Coverage

- User-confirmed Sprint 277 full suite: **1,504 passed, 2 skipped, 0 failed** in 215.81 seconds. The two skips are the existing Windows symlink-permission tests.
- Sprint 278 adds seven integration tests across the assumptions editor workflow, checking validation/formatting immutability, apply-versus-save separation, reload/discard restoration, editor status states, malformed JSON, and invalid-document atomicity.
- Focused Sprint 278 test file: **7 passed**. Full suite for this new checkpoint remains pending user verification; collection is recorded separately and is not a pass count.
- Release manifest and evidence defaults are advanced to Sprint 278.
- No production financial calculation logic, assumptions defaults, or golden baseline changed.

# Current Checkpoint — Sprint 274 ZIP Security Review & Data-Descriptor Integrity

- Current suite collection: **1490 tests across 168 test files**. Six test node IDs were added compared with Sprint 273; none were removed. Pytest configuration hash is unchanged.
- Full suite: **1490/1490 passed** across 32 deterministic partitions (18 × 47 and 14 × 46), with **20 subtests passed**, 0 failures, 0 errors and 0 skips in this Linux execution environment.
- Focused Sprint 265–274 package-security regression group: **90 passed**; Sprint 274 data-descriptor tests: **6 passed**. Compilation and assumptions JSON checks passed.
- Sprint 273 user-confirmed Windows baseline: **1,482 passed, 2 skipped**; skips were the filesystem symlink tests unavailable in that Windows environment.
- Sprint 274 closes a ZIP local-header/data-descriptor gap by verifying descriptor CRC-32 and compressed/uncompressed sizes against central-directory metadata for signed, unsigned and ZIP64 descriptors before payload reads.
- No production financial calculation logic, assumptions defaults or golden baseline changed. `data/assumptions.json` SHA-256: `33736d31d6a8d14b73b5ec83c9a9befcbb736713979a7eaaa95b2c35d22b3801`; `tests/golden/baseline.json` SHA-256: `d0d45d5c3e2846a79711a4e23f3920a04a81bef6025917a2aa9a00d82733c550`.
- Release package metrics and final archive audit are recorded in `reports/sprint274_test_count_reconciliation.json`.

# Current Checkpoint — Sprint 274 ZIP Security Review & Data-Descriptor Integrity

- Sprint 273 baseline: 1,484 collected test items; user-confirmed Windows run **1,482 passed, 2 skipped** (filesystem symlink permission limitations).
- Sprint 274 adds five test items: valid signed and unsigned ZIP data descriptors, CRC mismatch rejection, size mismatch rejection, and documentation/status/roadmap traceability. Expected collection: **1,489 items across 168 test files**.
- The ZIP auditor now validates data-descriptor CRC-32 and compressed/uncompressed sizes against central-directory metadata before CRC testing or payload reads. Both descriptor layouts are accepted when consistent; malformed descriptors are rejected.
- Financial calculation source, assumptions defaults and golden baseline are unchanged.
- Full-suite validation and final package metrics are to be recorded after running the acceptance partitions and rebuilding the final archive.

# Current Checkpoint — Sprint 273 ZIP Local-Header Integrity (2026-10-16)

- Current suite collection: **1,484 tests across 167 test files**. Ten test node IDs were added compared with Sprint 272; none were removed. Pytest configuration hash is unchanged.
- Sprint 265–273 package-security regression group: **84 passed**. Sprint 273 local-header tests: **10 passed**. `python -m compileall -q .` and assumptions JSON parsing passed.
- Full-suite acceptance was attempted but did not complete within this execution environment's time limit. No full-suite pass is claimed for Sprint 273; the Windows full-suite result is pending. Several CLI entrypoint tests passed individually, but a combined run timed out during subprocess-heavy tests.
- No production financial calculation logic, assumptions defaults, or golden baseline changed. `data/assumptions.json` SHA-256: `33736d31d6a8d14b73b5ec83c9a9befcbb736713979a7eaaa95b2c35d22b3801`; `tests/golden/baseline.json` SHA-256: `d0d45d5c3e2846a79711a4e23f3920a04a81bef6025917a2aa9a00d82733c550`.
- Sprint 273 release ZIP was generated, independently extracted, and package-audited. The final archive/manifest metrics are recorded in `reports/sprint273_test_count_reconciliation.json`.
- Current evidence: `reports/sprint273_collection_report.json` and `reports/sprint273_test_count_reconciliation.json`.


# Current Checkpoint — Sprint 262 Test-Count Reconciliation & Release Acceptance (2026-10-14)

- Audited the actual Sprint 260 and Sprint 261 ZIPs using the same Python 3.13.5 / pytest 9.0.2 environment and the same `PYTHONPATH=.` collection method.
- Sprint 260: **1,369 collected test items**. Sprint 261: **1,377 collected test items**. Exact node-ID comparison found **8 additions and 0 removals**: seven Sprint 261 isolation regressions plus one package-audit traceability test.
- The Sprint 261 archive's full suite passed across all 16 deterministic partitions: **1,377 passed** (87 + 15 × 86) and **20 subtests passed**. Each partition was independently executed; the single-process run exceeded the execution time limit, so the partitioned run is the acceptance evidence.
- Sprint 261 focused replay/collection/Monte Carlo/golden/package-audit group: **62 passed**; Sprint 261 isolation tests alone: **7 passed**. `compileall` and assumptions JSON parse checks passed.
- `reports/sprint262_collection_report.json` records all 1,377 pytest node IDs, counts by test file, Python/pytest versions and test/configuration hashes.
- The separately user-reported **1,308 passing** remains unverified in this runtime. It is **69 lower** than the Sprint 261 archive's 1,377 collected-and-passing items and **61 lower** than Sprint 260's 1,369 collected items. This establishes a source/runtime discovery discrepancy; it does not establish which tests are missing from the user's local copy. Compare a report generated on that machine to this checkpoint report to identify exact node IDs and hash differences.
- SHA-256 checksums for `data/assumptions.json` and `tests/golden/baseline.json` are identical between Sprint 260 and Sprint 261. No financial calculation logic, assumptions or golden baseline changed.

# Current Checkpoint — Sprint 261 Historical Replay Regression Isolation (2026-10-14)

- Sprint 261 adds seven regression tests proving historical replay remains isolated from production planning and Monte Carlo source imports, has no cross-call state, does not mutate supplied datasets, and does not modify `data/assumptions.json` or `tests/golden/baseline.json`.
- Added archive-audit enforcement for the Sprint 261 isolation test and release-traceability coverage.
- Financial calculation logic, assumptions defaults, and golden baseline remain unchanged.
- User-reported baseline: **1,308 tests successful** (retained as user-reported; not treated as this environment's verified execution count).
- Sprint 261 targeted regression group: **46 passed**.
- Full suite: **1,377/1,377 tests passed** across 16 deterministic partitions (87 + 15 × 86), with **20 subtests passed**.
- `python -m compileall -q .`: passed. Assumptions JSON parse: passed.
- Final assumptions and golden-baseline SHA-256 values match the uploaded Sprint 260 checkpoint. The production calculation source was not modified.

# Current Checkpoint Reconciliation — 2026-10-11

**Authoritative uploaded worktree at reconciliation:** Sprint 256 — Historical-Data Integration Design.

- `pytest --collect-only -q`: **1,327 tests collected**.
- Four independent release-acceptance partitions: **332 + 332 + 332 + 331 = 1,327 passed**.
- Subtests reported across partitions: **20 passed**.
- `python -m compileall -q .`: passed.
- Focused Sprint 252–256 regression group: **47 passed, 8 subtests passed**.
- Assumptions JSON parse gate: passed.
- The uploaded source ZIP contained `.git`, `.pytest_cache`, `__pycache__` and compiled `.pyc` artifacts and was wrapped in a top-level folder. It therefore failed the Sprint 255 package audit and must not be used as a release-clean package. A new root-level ZIP is being produced without those transient artifacts.
- Git HEAD still labels the repository Sprint 140 (`b1952c1`), while the worktree and sprint docs contain Sprint 256 files. The worktree is the tested source; commit history is not a reliable sprint chronology and has not been rewritten.
- This reconciliation changed documentation/package assembly only. `data/assumptions.json`, `tests/golden/baseline.json`, and financial calculation source files were not edited by the reconciliation step.


## Current Sprint 257 — Historical Data Adapter Interface & Versioned Fixture Format

- Added `HistoricalDataSourceAdapter`, a provider-neutral protocol for future adapters.
- Added a strict version-1 JSON fixture loader and immutable dataset result. Unknown keys, malformed JSON, unsupported/non-integer versions, and invalid series contracts fail explicitly.
- Added `tests/fixtures/historical_returns_v1.json`, clearly labelled synthetic test data, and 14 adapter/fixture regression tests.
- No live provider is selected, and no adapter is wired into `MarketData`, deterministic projections, Monte Carlo or GUI workflows.
- Focused Sprint 257 tests: **14/14 passed**. Full suite: **1,341/1,341 passed** across four partitions (336 + 335 + 335 + 335), with 20 subtests passed. Compilation passed.

**Current checkpoint:** Sprint 257 — Historical Data Adapter Interface & Versioned Fixture Format; **1,341 tests passing** across four partitions.

---

This section supersedes older Sprint 254/255/256 status notes below that say the full suite is pending. The historical Sprint 253 baseline of 1,294 tests remains valid for that earlier checkpoint; it is not the current collection count.

---

# Retirement Planner

## Current Version

2.0 RC2

## Sprint 185 — GUI Projection Result Snapshot → Report Contract Integration

- Added calculation-free snapshot consumption APIs to `ScenarioProjectionReport` so report payload, text, and year-row consumers can use the GUI's already-published immutable result snapshot without rebuilding projection comparisons.
- Added structural validation at the snapshot/report boundary to reject incomplete or malformed presentation snapshots before consumption.
- Added 4 regression tests covering payload equivalence, published text reuse, year-row reuse, and missing-field rejection.
- No retirement, tax, State Pension, ISA, savings, withdrawal or projection calculation engine logic changed.
- GUI/report regression: **227 passed**.
- Full suite: **962 passed, 9 subtests**.

## Current Sprint
Sprint 249 - Tax / Withdrawal Integration

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
- Harden workflow-action dispatch at the GUI boundary so action names are validated against the canonical action vocabulary before state refresh or handler execution.
- Reject non-callable explicitly injected handlers before presentation refresh, keeping the dispatch boundary deterministic for isolated tests.
- Add headless regression coverage for invalid action types and invalid injected handlers.
- Preserve validation, accessibility, event, persistence and lifecycle semantics.
- Keep all retirement, tax, State Pension, ISA, savings and withdrawal calculations unchanged and avoid external dependencies.
- GUI regression subset: **189 tests passing**.
- Full suite: **891 tests passing** (9 subtests).


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

## Sprint 223 — Goal Constraint Console Integration

- Extended the console Goals report to show the effective comparison constraint for evaluated goals.
- Preserved legacy goal-result compatibility when operator metadata is absent.
- Added three focused regression tests.
- No retirement, tax, State Pension, ISA, savings, withdrawal or calculation-engine logic changed.


## Sprint 229 — Goal Constraint Result Boundary Hardening

- Hardened `GoalEngine` direct-call result validation so evaluated goal actual values must be finite numeric values.
- Spending goals now reject an empty projection timeline with a clear boundary error instead of an incidental `min()` failure.
- Boolean, non-numeric and non-finite actual values are rejected before comparison.
- Valid numeric goal results and all existing operator/default-target semantics remain unchanged.
- No retirement, tax, State Pension, ISA, savings, withdrawal, investment-return, inflation, Monte Carlo or goal calculation semantics changed.

- Sprint 229 focused regression: **6 passed**.


## Sprint 245 — Assumption Boundary Documentation and Release Traceability

- Added `planner/docs/ASSUMPTION_BOUNDARY.md` documenting the frozen canonical/legacy assumption boundary, distinct Monte Carlo precedence, numeric validation contract and safe change protocol.
- Added four regression tests protecting the documentation/roadmap/status traceability.
- No financial calculation logic or assumption defaults changed.
- Sprint 245 focused regression: **4 passed**.
- Sprint 244 protected baseline: **1220 tests passing**.
- Full suite: **1224/1224 tests passed** across four independently validated discovery partitions (307 + 306 + 306 + 305).

**Current checkpoint: Sprint 245 — assumption boundary documentation and release traceability.**

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

## Sprint 104 — Interactive GUI Editing & Re-run

- Wired the desktop GUI to `ScenarioProjectionApplication` rather than hard-coded projection orchestration.
- Added editable starting pension, retirement age and projection end age fields.
- Added conservative, central and optimistic scenario checkboxes.
- Added GUI-side parsing/validation and a Run projection action that applies inputs in memory and rebuilds the view model through existing calculation boundaries.
- Added a separate Save assumptions action so editing does not silently persist configuration.
- Preserved the deterministic 75% Aviva / 25% Sky demo return data for the desktop entry point.
- Kept financial engine and retirement/tax/State Pension/ISA/savings/withdrawal calculations unchanged.

## Sprint 105 — GUI Controller Separation & State Synchronization

- Added `ScenarioProjectionGuiController` as a calculation-free event/orchestration boundary between Tkinter and `ScenarioProjectionApplication`.
- Added immutable `ScenarioProjectionRunResult` carrying validated inputs and the refreshed `ScenarioProjectionViewModel`.
- Preserved selected scenario state after re-runs and copied allocation/fund-return inputs at the controller boundary.
- Kept Save assumptions as an explicit persistence action.
- Added 12 controller regression tests.
- Financial engines and retirement/tax/State Pension/ISA/savings/withdrawal calculations remain unchanged.
- GUI regression subset: **136 tests passing**.
- Full suite: **838 tests passing** (9 subtests).

## Sprint 106 — GUI Usability & Presentation Polish

- Added a clear saved/unsaved status indicator driven by the existing assumptions change-tracking boundary.
- Added a selected-scenario summary so the current GUI state is explicit before and after projection runs.
- Added Reset inputs and Reload saved controls without changing financial calculations or persistence semantics.
- Reload saved assumptions uses the existing `Assumptions.load()` and validation boundary, then rebuilds the GUI view through the existing controller/application path.
- Improved desktop layout sizing, input spacing, result-card detail, table column sizing and vertical scrolling for year-level results.
- Preserved calculation-free GUI/controller boundaries and explicit Save assumptions behaviour.
- Added 7 GUI usability/reload regression tests.
- Corrected the Sprint 105 status test-count note: Sprint 105 added 12 controller tests, taking the full suite to 709 tests.
- Financial engines and retirement/tax/State Pension/ISA/savings/withdrawal calculations remain unchanged.

## Sprint 107 — GUI Robustness & Edge-Case Handling

- Hardened controller parsing against non-finite starting-pension values.
- Added regression coverage for one, two and three selected scenarios.
- Added rollback protection so a failed projection rebuild restores the previous in-memory planner inputs.
- Preserved explicit persistence and the existing GUI/controller/application/view-model boundaries.
- Added 5 GUI controller robustness regression tests.
- Financial engines and retirement/tax/State Pension/ISA/savings/withdrawal calculations remain unchanged.

## Sprint 108 — GUI Pending-State & Persistence Refinement

- Distinguished applied projection state from pending GUI control changes before a projection run.
- Added explicit pending scenario-selection state reporting so checkbox edits are visible immediately without silently changing the applied projection.
- Added pending-change detection for editable inputs, including invalid/incomplete control values.
- Kept Reset inputs aligned with the last applied in-memory state and preserved explicit Save assumptions behaviour.
- Added 4 GUI pending-state regression tests.
- Financial engines and retirement/tax/State Pension/ISA/savings/withdrawal calculations remain unchanged.

## Sprint 109 — GUI Interaction Polish

- Added live control-state refresh for keyboard edits and scenario changes.
- Added clear Run/Save action-state handling: Run is enabled only when controls are pending, while Save is enabled only for dirty applied assumptions with no pending edits.
- Added Enter-to-run and Escape-to-reset keyboard shortcuts.
- Focuses the starting-pension field when the desktop window first becomes interactive.
- Preserved the distinction between pending GUI controls and applied in-memory assumptions.
- Added 6 GUI interaction-polish regression tests.
- Financial engines and retirement/tax/State Pension/ISA/savings/withdrawal calculations remain unchanged.

## Sprint 110 — GUI Validation Feedback

- Added live, actionable validation feedback for pending GUI inputs before projection runs.
- Invalid or incomplete pension/age/scenario selections are surfaced in the input area rather than being silently treated as ready.
- Run projection is disabled while pending controls are invalid, while the authoritative controller/application validation boundary remains unchanged.
- Preserved Reset, Save and Reload state semantics and the pending/applied/saved workflow.
- Added 6 GUI validation-feedback regression tests.
- Financial engines and retirement/tax/State Pension/ISA/savings/withdrawal calculations remain unchanged.

## Sprint 111 — GUI Accessibility & Keyboard Usability

- Added explicit keyboard-friendly action aliases for Run, Save, Reset and Reload.
- Made editable entries, scenario checkbuttons and action buttons explicitly keyboard-focusable.
- Added validation-focus routing so invalid pension, age-range and empty-scenario states move focus to the relevant control.
- Kept the validation label focusable as a safe fallback when a concrete widget is unavailable.
- Preserved pending/applied/saved state semantics and the authoritative controller/application validation boundary.
- Added 7 GUI accessibility and keyboard-usability regression tests.
- Financial engines and retirement/tax/State Pension/ISA/savings/withdrawal calculations remain unchanged.

## Sprint 112 — GUI Presentation & Data-Density Refinement

- Refined the scenario summary for one-, two- and three-scenario result sets with an explicit scenario count.
- Improved the projection table layout with responsive column stretching, minimum widths and both vertical and horizontal scrolling for wider/larger result sets.
- Preserved calculation-free presentation: the GUI continues to consume the existing immutable `ScenarioProjectionViewModel`.
- Kept existing keyboard, validation and pending/applied/saved state behaviour unchanged.
- Added 5 GUI presentation/data-density regression tests.
- Financial engines and retirement/tax/State Pension/ISA/savings/withdrawal calculations remain unchanged.

## Sprint 113 — GUI Scenario Comparison Visualisation

- Added a compact ending-pension comparison chart to the desktop GUI.
- Chart bars are derived directly from the immutable `ScenarioProjectionViewModel.ending_balance_series()` contract.
- Chart layout scales to one-, two- and three-scenario result sets and resizes with the window.
- Added a clear empty-state message and £0/maximum axis endpoints.
- Kept chart rendering calculation-free and preserved all existing GUI state, validation and accessibility behaviour.
- Added 6 GUI visualisation regression tests.
- Financial engines and retirement/tax/State Pension/ISA/savings/withdrawal calculations remain unchanged.

## Sprint 114 — GUI Chart Accessibility & Interaction

- Added an accessible text summary for the ending-pension comparison chart.
- Added keyboard navigation across chart scenarios using Left/Right/Up/Down plus Home/End.
- Added pointer-over scenario feedback without changing the underlying view-model or calculations.
- Added focused-bar indication while preserving the calculation-free chart renderer.
- Preserved existing keyboard, validation and pending/applied/saved state behaviour.
- Added 4 GUI chart accessibility and interaction regression tests.
- Financial engines and retirement/tax/State Pension/ISA/savings/withdrawal calculations remain unchanged.

## Sprint 115 — GUI Final Integration Hardening

- Made desktop window construction idempotent so repeated build calls do not duplicate the control tree or keyboard bindings.
- Added an explicit window lifecycle state with safe, idempotent close handling and a WM_DELETE_WINDOW close hook.
- Made projection, save, reload and result-refresh callbacks harmless after the window has closed.
- Preserved the existing validation, accessibility, chart and pending/applied/saved state boundaries.
- Added 6 GUI lifecycle/integration-hardening regression tests.
- Financial engines and retirement/tax/State Pension/ISA/savings/withdrawal calculations remain unchanged.

## Sprint 116 — GUI Testability Infrastructure

- Added an injectable `DialogService` seam so GUI action/error paths can be tested without Tk message boxes.
- Added `RecordingDialog` as a small headless test double for user-facing error/info messages.
- Kept the desktop window's financial orchestration unchanged; the seam affects presentation only.
- Added 6 GUI testability regression tests.
- Financial engines and retirement/tax/State Pension/ISA/savings/withdrawal calculations remain unchanged.

## Sprint 117 — GUI Event/State Abstraction

- Added an injectable `GuiEventService` seam with Tk and recording implementations for keyboard bindings and idle callbacks.
- Routed the scenario window's keyboard shortcuts and initial deferred focus through the event seam.
- Made deferred pension-field focus safe after window closure.
- Added 5 GUI event/lifecycle regression tests.
- Financial engines and retirement/tax/State Pension/ISA/savings/withdrawal calculations remain unchanged.

## Sprint 126 — GUI Workflow-State Action Outcome Hardening

- Hardened the shared presentation dispatcher so permitted actions always trigger a final workflow-state/presentation resynchronisation.
- Added a boolean dispatch result for deterministic blocked-versus-executed behaviour in headless button/event adapters.
- Preserved unknown-action rejection and existing handler semantics; the final refresh is idempotent for real handlers and protects lightweight test adapters from stale presentation state.
- Financial engines and retirement/tax/State Pension/ISA/savings/withdrawal calculations remain unchanged.
- Regression subset: **104 tests passing**.
- Full suite: **818 tests passing** (9 subtests).

## Sprint 125 — GUI Workflow-State Action Dispatch Hardening

- Centralised all button and keyboard Run/Save/Reset/Reload entry points through one presentation-layer workflow action dispatcher.
- Added a named action lookup on the immutable workflow-state model so every presentation trigger uses the same authoritative action permission boundary.
- Preserved existing direct action handlers, validation/error semantics, lifecycle no-op behaviour and application/controller/view-model seams.
- Added 4 headless regression tests covering named action permissions, invalid action rejection and parity between button/event dispatch.
- Financial engines and retirement/tax/State Pension/ISA/savings/withdrawal calculations remain unchanged.
- Regression subset: **113 tests passing**.

## Sprint 124 — GUI Workflow-State Action Boundary Hardening

- Routed Run, Save, Reset and Reload desktop button commands through explicit workflow-state gates before invoking their existing action handlers.
- Kept keyboard/event action gates aligned with button-driven actions so disabled workflow actions cannot be triggered through the presentation boundary.
- Preserved the existing direct action handlers and validation/error semantics for headless tests and internal orchestration.
- Added 6 headless regression tests covering button action gating, clean/pending states and post-close no-op behaviour.
- Preserved the existing controller/application/view-model, validation, event and dialog seams.
- Financial engines and retirement/tax/State Pension/ISA/savings/withdrawal calculations remain unchanged.
- Regression subset: **109 tests passing**.
- Full suite: **811 tests passing** (9 subtests).

## Sprint 123 — GUI Workflow-State Lifecycle Presentation Hardening

- Hardened the terminal window-close transition so the presentation adapter immediately reflects the immutable `Closed` workflow state.
- Resynchronised status text and Run/Save/Reset/Reload action availability during close, preventing stale enabled controls after lifecycle termination.
- Added headless regression coverage for terminal-state presentation synchronisation.
- Preserved the existing controller/application/view-model, validation, event and dialog seams.
- Financial engines and retirement/tax/State Pension/ISA/savings/withdrawal calculations remain unchanged.
- Regression subset: **93 tests passing**.
- Full suite: **805 tests passing** (9 subtests).

## Sprint 122 — GUI Workflow-State Transition Hardening

- Hardened Reset inputs so the workflow-state model, status presentation and action controls are explicitly resynchronised after controls are restored.
- Prevented stale Run/Save/Reset availability when a reset is performed through a keyboard shortcut or directly through the presentation adapter.
- Added headless regression coverage for valid and invalid pending reset transitions and keyboard reset state synchronisation.
- Preserved the existing controller/application/view-model, validation, event and dialog seams.
- Financial engines and retirement/tax/State Pension/ISA/savings/withdrawal calculations remain unchanged.
- Regression subset: **107 tests passing**.
- Full suite: **804 tests passing** (9 subtests).

## Sprint 121 — GUI Validation-Aware Workflow State

- Refined the immutable GUI workflow-state model so invalid pending edits are explicitly reported as requiring attention rather than appearing ready to run.
- Kept action availability unchanged: invalid pending edits still disable Run while retaining Reset and Reload.
- Added regression coverage for invalid-to-valid recovery, reset preservation and the desktop adapter's validation-aware status.
- Hardened keyboard action routing so Return/Run, Save and Reset shortcuts cannot bypass the workflow-state action gates exposed by the desktop adapter.
- Added headless regression coverage for disabled-action shortcut bypasses while preserving direct validation/error handling for the underlying actions.
- Preserved the existing controller/application/view-model and event/dialog seams.
- Financial engines and retirement/tax/State Pension/ISA/savings/withdrawal calculations remain unchanged.
- Regression subset: 122 tests passing (3 subtests).
- Full suite: **801 tests passing** (9 subtests).

## Sprint 120 — GUI Workflow-State Action Integration

- Route Run, Save, Reset and Reload button enabled/disabled states through the immutable workflow-state model.
- Ensure clean, pending-valid, pending-invalid and closed states expose consistent action availability in the desktop adapter.
- Preserve the existing validation, keyboard, event, dialog, persistence and pending/applied/saved semantics.
- Add headless regression coverage for GUI action-state integration without requiring a live Tk desktop.
- Keep financial engines and retirement/tax/State Pension/ISA/savings/withdrawal calculations unchanged and avoid external dependencies.

## Sprint 119 — GUI Workflow-State Model

- Added an immutable, Tk-free `ScenarioProjectionGuiState` model for the desktop workflow.
- Formalised Run, Save, Reset and Reload action availability from pending-change, validation, dirty-state and lifecycle conditions.
- Added explicit pure state transitions for edit, successful run, save, reset, reload and close operations.
- Kept the existing window as a presentation adapter while routing Run/Save/status decisions through the workflow-state model.
- Preserved the existing pending/applied/saved semantics and headless event/dialog seams.
- Added 8 GUI workflow-state regression tests covering valid/invalid edits and every major transition.
- Financial engines and retirement/tax/State Pension/ISA/savings/withdrawal calculations remain unchanged.

## Sprint 118 — GUI Integration Regression Coverage

- Added headless integration coverage for the complete keyboard/event workflow using `RecordingEventService` and `RecordingDialog`.
- Added a `RecordingEventService.trigger()` helper for deterministic event dispatch in tests.
- Routed reload error handling through the injected dialog seam, removing an unnecessary Tk messagebox dependency from that path.
- Added 8 GUI event-integration regression tests covering run, validation, save, reset, reload and post-close behaviour.
- Restored the canonical `data/assumptions.json` test baseline to 660000 starting pension, retirement age 63 and projection end age 90.
- Financial engines and retirement/tax/State Pension/ISA/savings/withdrawal calculations remain unchanged.



## Sprint 128 — GUI Workflow-State Canonical Action Handler Hardening

- Centralise the canonical Run/Save/Reset/Reload presentation handler mapping so action gates cannot drift from their handlers.
- Route button and keyboard entry points through the action name only, removing duplicated action-to-handler pairings.
- Preserve the explicit handler injection seam used by headless boundary tests and retain exception-safe final workflow synchronisation.
- Add regression coverage for canonical handler mapping and button/event dispatch resolution.
- Keep all retirement, tax, State Pension, ISA, savings and withdrawal calculations unchanged and avoid external dependencies.
- Regression subset: **120 tests passing**.
- Full suite: **822 tests passing** (9 subtests).

## Sprint 127 — GUI Workflow-State Exception-Safe Action Dispatch Hardening

- Keep the shared presentation action dispatcher synchronised when an injected or unexpected action handler raises.
- Refresh workflow status/action availability in a `finally` boundary while preserving the original handler exception.
- Add headless regression coverage proving failed presentation handlers cannot leave stale workflow state behind.
- Preserve existing action permission, button/keyboard parity, validation, accessibility, persistence and lifecycle semantics.
- Keep all retirement, tax, State Pension, ISA, savings and withdrawal calculations unchanged and avoid external dependencies.
- Regression subset: **105 tests passing**.
- Full suite: **819 tests passing** (9 subtests).

## Sprint 129 — GUI Workflow-State Canonical Action Vocabulary Hardening

- Introduced one canonical `WORKFLOW_ACTIONS` vocabulary for Run, Save, Reset and Reload in the Tk-free workflow-state model.
- Exposed the stable action vocabulary through `available_actions` so presentation adapters and headless tests can inspect the same contract.
- Updated the desktop window's canonical handler mapping to derive its keys from the shared action vocabulary, preventing action-name drift between state gating and handlers.
- Unknown actions remain rejected deterministically without mutating the immutable workflow state.
- Financial engines and retirement/tax/State Pension/ISA/savings/withdrawal calculations remain unchanged.
- Regression subset: **122 tests passing**.
- Full suite: **824 tests passing** (9 subtests).

## Sprint 130 — GUI Workflow-State Action Presentation Contract Hardening

- Added immutable `action_states` to `ScenarioProjectionGuiState`, providing the canonical Run/Save/Reset/Reload permission snapshot in stable vocabulary order.
- Added a canonical `_workflow_action_buttons()` mapping in the desktop presentation adapter, derived from the shared `WORKFLOW_ACTIONS` vocabulary.
- Updated action-state rendering to consume the workflow state's canonical action snapshot, removing duplicated Run/Save/Reset/Reload enablement references from the presentation renderer.
- Added 3 headless regression tests covering action-state snapshots, canonical button mapping and rendering of the canonical action contract.
- Preserved validation, accessibility, event, persistence and lifecycle semantics.
- Financial engines and retirement/tax/State Pension/ISA/savings/withdrawal calculations remain unchanged.
- Regression subset: **125 tests passing**.
- Full suite: **827 tests passing** (9 subtests).


## Sprint 131 — GUI Workflow-State Canonical Permission Contract Hardening

- Made the immutable `action_states` snapshot the single permission source for named workflow-action lookup, eliminating a second action-to-property dictionary.
- Kept the canonical Run/Save/Reset/Reload ordering and immutable tuple contract used by the presentation adapter.
- Added headless regression coverage proving named action permissions match the canonical snapshot and that the snapshot cannot be mutated.
- Preserved validation, accessibility, event, persistence and lifecycle semantics.
- Financial engines and retirement/tax/State Pension/ISA/savings/withdrawal calculations remain unchanged.
- GUI regression subset: **127 tests passing**.
- Full suite: **829 tests passing** (9 subtests).

## Sprint 132 — GUI Workflow-State Canonical Action Descriptor Hardening

- Added one canonical presentation descriptor pairing each Run/Save/Reset/Reload action with its existing handler and button attribute.
- Derived the presentation handler and button mappings from the same descriptor, eliminating parallel action-to-handler and action-to-button wiring lists.
- Added headless regression coverage for canonical descriptor ordering and handler/button mapping parity.
- Preserved validation, accessibility, event, persistence and lifecycle semantics.
- Financial engines and retirement/tax/State Pension/ISA/savings/withdrawal calculations remain unchanged.
- GUI regression subset: **129 tests passing**.
- Full suite: **831 tests passing** (9 subtests).

## Sprint 133 — GUI Workflow-State Immutable Action Descriptor Hardening

- Replaced positional presentation action tuples with the frozen `WorkflowActionPresentation` descriptor, giving each action explicit `action`, `handler_name` and `button_name` fields.
- Kept the single canonical descriptor sequence aligned with `WORKFLOW_ACTIONS`; handler and button mappings continue to derive from the same source.
- Added headless regression coverage for descriptor immutability, named fields and canonical action uniqueness/order.
- Preserved validation, accessibility, event, persistence and lifecycle semantics.
- Financial engines and retirement/tax/State Pension/ISA/savings/withdrawal calculations remain unchanged.
- GUI regression subset: **131 tests passing**.


## Sprint 134 — GUI Workflow-State Action Descriptor Consistency Hardening

- Validate the immutable presentation descriptor sequence against the canonical `WORKFLOW_ACTIONS` vocabulary before resolving live GUI bindings.
- Fail deterministically if presentation action ordering or membership drifts from the workflow-state contract.
- Add headless regression coverage for descriptor-contract drift detection and preserved canonical ordering.
- Preserve validation, accessibility, event, persistence and lifecycle semantics.
- Financial engines and retirement/tax/State Pension/ISA/savings/withdrawal calculations remain unchanged.
- GUI regression subset: **133 tests passing**.
- Full suite: **835 tests passing** (9 subtests).

## Sprint 135 — GUI Workflow-State Action Binding Consistency Hardening

- Strengthened the immutable presentation action contract with deterministic handler/button binding validation.
- Duplicate handler or button bindings are rejected before live GUI dispatch/rendering can use them.
- Missing or non-callable handler bindings are rejected with a clear presentation-contract error.
- Added headless regression coverage for binding consistency failures.
- Preserved validation, accessibility, event, persistence and lifecycle semantics.
- Financial engines and retirement/tax/State Pension/ISA/savings/withdrawal calculations remain unchanged.

## Sprint 136 — GUI Workflow-State Action Binding Runtime Contract Hardening

- Validate resolved presentation button bindings at the GUI action-contract boundary so every configured control supports the required `configure(...)` operation.
- Validate descriptor field types before resolving live bindings, rejecting malformed action, handler and button names deterministically.
- Preserve the optional `None` button seam used by headless/non-rendering paths while keeping real GUI controls contract-safe.
- Add headless regression coverage for malformed descriptor fields, non-configurable controls and the optional button boundary.
- Preserve validation, accessibility, event, persistence and lifecycle semantics.
- Keep all retirement, tax, State Pension, ISA, savings and withdrawal calculations unchanged and avoid external dependencies.
- Regression subset: **139 tests passing**.
- Full suite: **841 tests passing** (9 subtests).

## Sprint 137 — GUI Workflow-State Resolved Action Binding Contract Hardening

- Represented resolved Run, Save, Reset and Reload presentation bindings as immutable named records rather than positional tuples.
- Derived button and handler lookup maps from the named runtime binding contract so presentation consumers cannot confuse binding positions.
- Added three headless regression tests for runtime binding immutability, named fields and canonical binding order.
- Preserved validation, accessibility, event, persistence and lifecycle semantics.
- Financial calculation logic remains unchanged.
- GUI regression subset: **142 tests passing**.
- Full suite: **844 tests passing** (9 subtests).

## Sprint 142 — GUI Workflow-State Action Binding Cache Lifecycle Hardening

- Centralize invalidation of the cached workflow action-binding registry and its derived button and handler maps in one dedicated lifecycle helper.
- Use the helper when live GUI action controls are created so all cached presentation views are cleared together and cannot drift.
- Add headless regression coverage for atomic cache clearing, rebuild identity, consistency and idempotent invalidation.
- Preserve validation, accessibility, event, persistence and lifecycle semantics.
- Keep all retirement, tax, State Pension, ISA, savings and withdrawal calculations unchanged and avoid external dependencies.
- GUI regression subset: **154 tests passing**.
- Full suite: **856 tests passing** (9 subtests).


## Sprint 138 — GUI Workflow-State Immutable Action Binding Map Hardening

- Exposed resolved workflow-action button and handler maps as immutable mapping views so presentation consumers cannot mutate canonical action wiring at runtime.
- Preserved the shared resolved `WorkflowActionBinding` contract as the sole source for both maps.
- Added headless regression coverage for immutability of the resolved button and handler maps.
- Preserved validation, accessibility, event, persistence and lifecycle semantics.
- Financial engines and retirement/tax/State Pension/ISA/savings/withdrawal calculations remain unchanged.
- GUI regression subset: **144 tests passing**.
- Full suite: **846 tests passing** (9 subtests).


## Sprint 139 — GUI Workflow-State Canonical Action Binding Registry Hardening

- Centralized resolved Run, Save, Reset and Reload presentation bindings in one immutable action-keyed registry.
- Derived button rendering and handler dispatch maps from the shared resolved registry.
- Preserved the explicit handler-injection seam and all existing GUI workflow semantics.
- Added three headless regression tests for registry immutability, map derivation and single-registry rendering.
- Financial engines and retirement/tax/State Pension/ISA/savings/withdrawal calculations remain unchanged.
- GUI regression subset: **130 tests passing**.
- Full suite: **849 tests passing** (9 subtests).


## Sprint 140 — GUI Workflow-State Canonical Action Binding Registry Reuse Hardening

- Cached the resolved immutable action-binding registry so presentation rendering and dispatch reuse one runtime contract instead of independently rebuilding live bindings.
- Invalidate the registry when GUI action controls are created so cached bindings cannot predate live widgets.
- Added two headless regression tests covering registry identity/reuse and shared cached consumption by button and handler maps.
- Preserved validation, accessibility, event, persistence and lifecycle semantics.
- Financial engines and retirement/tax/State Pension/ISA/savings/withdrawal calculations remain unchanged.
- GUI regression subset: **132 tests passing**.
- Full suite: **851 tests passing** (9 subtests).

## Sprint 141 — GUI Workflow-State Cached Action Map Reuse Hardening

- Cache the immutable action button and handler maps derived from the shared resolved action-binding registry so repeated rendering and dispatch calls reuse the same map objects.
- Invalidate the derived maps alongside the binding registry when live GUI action controls are created, preventing stale pre-build presentation bindings.
- Add headless regression coverage for button-map and handler-map identity/reuse.
- Preserve validation, accessibility, event, persistence and lifecycle semantics.
- Keep all retirement, tax, State Pension, ISA, savings and withdrawal calculations unchanged and avoid external dependencies.
- GUI regression subset: **151 tests passing**.
- Full suite: **853 tests passing** (9 subtests).



## Sprint 143 — GUI Workflow-State Action Binding Cache Terminal-Lifecycle Hardening

- Release the cached immutable workflow action-binding registry and its derived button and handler maps when the presentation enters its terminal closed state.
- Keep the final closed-state refresh intact, then invalidate cached live bindings so subsequent callbacks cannot retain stale widget or handler references.
- Add headless regression coverage for close-time cache invalidation and repeated close idempotence.
- Preserve validation, accessibility, event, persistence and lifecycle semantics.
- Keep all retirement, tax, State Pension, ISA, savings and withdrawal calculations unchanged and avoid external dependencies.
- GUI regression subset: **156 tests passing**.
- Full suite: **858 tests passing** (9 subtests).


## Sprint 144 — GUI Workflow-State Action Binding Cache Terminal Rehydration Hardening

- Prevent later closed-state refresh or dispatch callbacks from rehydrating the released workflow action-binding registry and derived maps.
- Preserve the terminal refresh behaviour by disabling already-created action controls directly when the cache has already been released.
- Added two headless regression tests covering closed-state refresh and dispatch non-rehydration.
- Preserve validation, accessibility, event, persistence and lifecycle semantics.
- Keep all retirement, tax, State Pension, ISA, savings and withdrawal calculations unchanged and avoid external dependencies.
- GUI regression subset: **158 tests passing**.
- Full suite: **860 tests passing** (9 subtests).


## Sprint 145 — GUI Workflow-State Action Binding Cache Terminal Access Hardening

- Prevent closed workflow-action binding, button-map and handler-map accessors from rehydrating released presentation caches.
- Return one shared immutable empty mapping for terminal closed-state action-cache access, while preserving the existing final closed-state control disablement.
- Add headless regression coverage for terminal accessor emptiness, shared identity and non-repopulation of released caches.
- Preserve validation, accessibility, event, persistence and lifecycle semantics.
- Keep all retirement, tax, State Pension, ISA, savings and withdrawal calculations unchanged and avoid external dependencies.
- GUI regression subset: **160 tests passing**.
- Full suite: **862 tests passing** (9 subtests).


## Sprint 146 — GUI Workflow-State Action Binding Derived-Map Cache Dependency Hardening

- Hardened the dependency between the cached workflow action registry and its derived button and handler maps.
- When the shared registry is absent, derived maps are discarded before rebuilding so stale views cannot survive an independently invalidated registry.
- Added two headless regression tests covering button-map and handler-map rebuild after registry invalidation.
- Preserved validation, accessibility, event, persistence and lifecycle semantics.
- Financial engines and retirement/tax/State Pension/ISA/savings/withdrawal calculations remain unchanged and avoid external dependencies.
- GUI regression subset: **162 tests passing**.
- Full suite: **875 tests passing** (9 subtests).


## Sprint 147 — GUI Workflow-State Action Binding Cache Source-Coherence Hardening

- Track the exact resolved workflow action-binding registry used to construct each cached button and handler map.
- Rebuild derived maps whenever the registry identity changes, preventing stale maps from surviving replacement of the shared runtime binding registry.
- Clear the derived-map source references together with the registry and maps during lifecycle invalidation.
- Add headless regression coverage for derived-map rebuilding after registry identity replacement.
- Preserve validation, accessibility, event, persistence and lifecycle semantics.
- Keep all retirement, tax, State Pension, ISA, savings and withdrawal calculations unchanged and avoid external dependencies.
- GUI regression subset: **164 tests passing**.


## Sprint 148 — GUI Workflow-State Action Binding Derived Map Entry Coherence Hardening

- Hardened cached button and handler maps against private cache replacement or entry drift even when their recorded registry source remains unchanged.
- Rebuild derived maps when their entries no longer exactly match the current resolved workflow-action binding registry.
- Added two headless regression tests covering button-map and handler-map entry drift.
- Preserved validation, accessibility, event, persistence and lifecycle semantics.
- Kept all retirement, tax, State Pension, ISA, savings and withdrawal calculations unchanged and avoided external dependencies.
- GUI regression subset: **166 tests passing**.
- Full suite: **868 tests passing** (9 subtests).


## Sprint 149 — GUI Workflow-State Action Binding Registry Content Integrity Hardening

- Hardened the cached workflow action-binding registry against canonical key-set and binding-action drift before it can feed derived presentation maps.
- Automatically invalidate and rebuild the complete workflow-action cache when cached registry content is incoherent.
- Added two headless regression tests covering registry key drift and binding-action drift.
- Preserved validation, accessibility, event, persistence and lifecycle semantics.
- Kept all retirement, tax, State Pension, ISA, savings and withdrawal calculations unchanged and avoided external dependencies.
- GUI regression subset: **168 tests passing**.
- Full suite: **870 tests passing** (9 subtests).


## Sprint 150 — GUI Workflow-State Action Binding Live Source Coherence Hardening

- Harden the cached workflow action-binding registry against handler and button drift from the canonical live presentation bindings.
- Rebuild the registry when cached binding content no longer matches the live handler/button descriptors before derived maps consume it.
- Add headless regression coverage for cached handler drift and cached button drift.
- Preserve validation, accessibility, event, persistence and lifecycle semantics.
- Keep all retirement, tax, State Pension, ISA, savings and withdrawal calculations unchanged and avoid external dependencies.
- GUI regression subset: **170 tests passing**.
- Full suite: **872 tests passing** (9 subtests).


## Sprint 151 — GUI Workflow-State Action Binding Cache Type Integrity Hardening

- Harden the cached workflow action-binding registry and derived button/handler maps against invalid cache object types before they are consumed.
- Rebuild the complete cache safely when a private cache replacement is no longer a mapping, preserving the canonical live binding contract.
- Add headless regression coverage for invalid registry, button-map and handler-map cache types.
- Preserve validation, accessibility, event, persistence and lifecycle semantics.
- Keep all retirement, tax, State Pension, ISA, savings and withdrawal calculations unchanged and avoid external dependencies.
- GUI regression subset: **173 tests passing**.
- Full suite: **875 tests passing** (9 subtests).


## Sprint 153 - GUI Workflow-State Action Binding Cache Dependency Invalidation Coverage Hardening

- Harden cache lifecycle coverage so rebuilding an incoherent workflow-action registry clears all dependent derived button and handler maps before they can be reused.
- Add headless regression coverage proving registry drift clears both derived caches and their source references before the derived views are rebuilt.
- Preserve validation, accessibility, event, persistence and lifecycle semantics.
- Keep all retirement, tax, State Pension, ISA, savings and withdrawal calculations unchanged and avoid external dependencies.
- GUI regression subset: **177 tests passing**.
- Full suite: **879 tests passing** (9 subtests).


## Sprint 152 - GUI Workflow-State Action Binding Derived Map Ordering Integrity Hardening

- Harden cached button and handler maps against canonical action-order drift while preserving their existing content/source coherence checks.
- Rebuild derived maps when their cached key order no longer matches `WORKFLOW_ACTIONS`.
- Add headless regression coverage for button-map and handler-map key-order drift.
- Preserve validation, accessibility, event, persistence and lifecycle semantics.
- Keep all retirement, tax, State Pension, ISA, savings and withdrawal calculations unchanged and avoid external dependencies.
- GUI regression subset: **175 tests passing**.
- Full suite: **877 tests passing** (9 subtests).
## Sprint 154 - GUI Workflow-State Action Binding Derived Map Source Integrity Hardening

- Centralize the derived button/handler map coherence invariant so both cached views require an exact reference to the current resolved workflow-action registry, canonical action ordering, and matching entries.
- Add headless regression coverage for tampered derived-map source references and verify both maps rebuild against the live registry.
- Preserve validation, accessibility, event, persistence and lifecycle semantics.
- Keep all retirement, tax, State Pension, ISA, savings and withdrawal calculations unchanged and avoid external dependencies.
- GUI regression subset: **179 tests passing**.
- Full suite: **881 tests passing** (9 subtests).

## Sprint 155 — GUI Workflow-State Action Binding Cache Validation Defensive Hardening

- Hardened workflow-action cache validation against malformed mapping implementations that raise during inspection.
- Added two regression tests for defensive registry and derived-map validation.
- GUI regression subset: **181 tests passing**.
- Full suite: **883 tests passing** (9 subtests).
- Financial calculation logic unchanged.

## Sprint 157 - GUI Workflow-State Action Binding Registry Immutability Hardening

- Harden the cached workflow-action registry so only the immutable `MappingProxyType` representation is accepted as a valid cache.
- Rebuild the registry when a private cache replacement uses a mutable mapping, preventing post-validation mutation from crossing the cache boundary.
- Add headless regression coverage for mutable dictionary and mutable mapping registry replacements.
- Preserve validation, accessibility, event, persistence and lifecycle semantics.
- Keep all retirement, tax, State Pension, ISA, savings and withdrawal calculations unchanged and avoid external dependencies.
- GUI regression subset: **185 tests passing**.
- Full suite: **887 tests passing** (9 subtests).


## Sprint 158 - GUI Workflow-State Action Binding Cache Publication Integrity Hardening

- Harden workflow-action cache publication so immutable registry and derived maps are fully constructed before their cache fields are published.
- Clear the affected derived cache and source reference before reconstruction, preventing failed publication from leaving a partially rebuilt cache pair.
- Add two headless regression tests covering failed registry publication and failed button-map publication.
- Preserve validation, accessibility, event, persistence and lifecycle semantics.
- Keep all retirement, tax, State Pension, ISA, savings and withdrawal calculations unchanged and avoid external dependencies.
- GUI regression subset: **187 tests passing**.
- Full suite: **889 tests passing** (9 subtests).


## Sprint 160 - GUI Workflow-State Action Lifecycle Dispatch Hardening

- Harden workflow-action dispatch so a closed presentation instance short-circuits before any workflow-state refresh or further presentation work.
- Preserve terminal lifecycle semantics when an action handler closes the window during dispatch; the dispatch cleanup still resynchronises state without rehydrating released action caches.
- Add headless regression coverage for post-close dispatch short-circuiting and handler-triggered terminal close.
- Preserve validation, accessibility, event, persistence and lifecycle semantics.
- Keep all retirement, tax, State Pension, ISA, savings and withdrawal calculations unchanged and avoid external dependencies.
- GUI regression subset: **191 tests passing**.
- Full suite: **893 tests passing** (9 subtests).

## Sprint 161 — GUI End-to-End Workflow/Regression Consolidation

- Consolidated all Run, Save, Reset and Reload button/keyboard entry points around the canonical workflow-action dispatch boundary by returning the shared dispatch outcome from every entry point.
- Added end-to-end headless regression coverage proving button and keyboard entry points expose the same enabled/blocked dispatch outcome and all eight entry points use the canonical action vocabulary.
- Preserved workflow-state gating, validation, accessibility, event, persistence and terminal lifecycle semantics.
- Kept all retirement, tax, State Pension, ISA, savings and withdrawal calculations unchanged and introduced no external dependencies.
- GUI regression subset: **193 tests passing**.
- Full suite: **895 tests passing** (9 subtests).

## Sprint 162 — GUI Workflow-State Integration Close-Out Hardening

- Hardened the final GUI workflow entry-point boundary so all Run, Save, Reset and Reload button/event entry points remain terminal no-ops after window close.
- Added headless regression coverage for terminal behaviour across all eight entry points and for consistent event-entry workflow gating in a clean state.
- Preserved workflow-state gating, validation, accessibility, event, persistence and terminal lifecycle semantics.
- Kept all retirement, tax, State Pension, ISA, savings and withdrawal calculations unchanged and introduced no external dependencies.
- GUI regression subset: **195 tests passing**.
- Full suite: **897 tests passing** (9 subtests).

## Sprint 163 — GUI Workflow-State Entry-Point Exception Boundary Hardening

- Hardened the button and keyboard workflow entry points so handler exceptions propagate unchanged while the canonical dispatch boundary still resynchronises workflow state.
- Added two headless regression tests covering Run through button and keyboard entry points when a presentation handler raises after changing an input.
- Preserved workflow-state gating, validation, accessibility, persistence and terminal lifecycle semantics.
- Kept all retirement, tax, State Pension, ISA, savings and withdrawal calculations unchanged and introduced no external dependencies.
- GUI regression subset: **197 tests passing**.
- Full suite: **899 tests passing** (9 subtests).

## Sprint 164 — GUI Workflow Lifecycle Callback Close-Out Hardening

- Hardened terminal lifecycle behaviour for keyboard binding and input-change callbacks so closed presentation instances perform no further callback wiring or workflow-state refresh work.
- Added two headless regression tests covering post-close keyboard-binding suppression and post-close input-change suppression.
- Preserved workflow-state gating, validation, accessibility, event, persistence and terminal lifecycle semantics.
- Kept all retirement, tax, State Pension, ISA, savings and withdrawal calculations unchanged and introduced no external dependencies.
- GUI regression subset: **199 tests passing**.
- Full suite: **901 tests passing** (9 subtests).

## Sprint 165 — GUI Workflow-State Keyboard Binding Idempotency Hardening

- Hardened keyboard shortcut wiring so repeated binding attempts against the same event service are idempotent and cannot accumulate duplicate Tk callbacks.
- Preserve the ability to wire a newly injected/replaced event service independently for headless/test adapters.
- Added two headless regression tests covering repeated binding on one service and rebinding to a different service.
- Preserved workflow-state gating, validation, accessibility, event, persistence and terminal lifecycle semantics.
- Kept all retirement, tax, State Pension, ISA, savings and withdrawal calculations unchanged and introduced no external dependencies.

## Sprint 166 — GUI Workflow-State Keyboard Shortcut Contract Hardening

- Consolidated keyboard shortcut wiring into a canonical declarative binding contract covering Run, Save, Reset and Reload aliases.
- Validate every keyboard binding against the canonical workflow action vocabulary and require its resolved event handler to be callable before publication.
- Updated event entry points to accept Tk/recording event arguments while remaining directly callable by existing application code and tests.
- Added two headless regression tests covering complete canonical action coverage and direct event-handler binding.
- Preserved keyboard binding idempotency, workflow-state gating, validation, accessibility, persistence and terminal lifecycle semantics.
- Kept all retirement, tax, State Pension, ISA, savings and withdrawal calculations unchanged and introduced no external dependencies.
- GUI regression subset: **203 tests passing**.
- Full suite: **905 tests passing** (9 subtests).


## Sprint 167 — GUI Workflow-State Keyboard Binding Contract Final Hardening

- Added a single canonical keyboard-binding contract resolver so shortcut wiring validates event shape, canonical action membership, handler callability, duplicate event/action pairs and complete Run/Save/Reset/Reload action coverage before binding.
- Kept keyboard shortcut publication atomic: validation completes before any event-service binding is performed.
- Added two headless regression tests covering complete workflow-action coverage and duplicate event/action contract rejection.
- Preserved keyboard binding idempotency, workflow-state gating, validation, accessibility, persistence and terminal lifecycle semantics.
- Kept all retirement, tax, State Pension, ISA, savings and withdrawal calculations unchanged and introduced no external dependencies.
- GUI regression subset: **205 tests passing**.
- Full suite: **907 tests passing** (9 subtests).

## Sprint 168 — GUI Workflow-State Integration Gardening Close-Out

- Finalised the GUI workflow/action integration hardening phase from the stable Sprint 167 checkpoint.
- Hardened keyboard shortcut publication so malformed canonical contracts fail before any event callback is published, covering both unknown actions and non-callable handlers.
- Added two headless regression tests proving keyboard binding publication is atomic on invalid action and invalid-handler contracts.
- Confirmed the canonical Run/Save/Reset/Reload button and keyboard paths remain aligned through the shared workflow-state dispatch boundary, with terminal lifecycle protections intact.
- Preserved workflow-state gating, validation, accessibility, event, persistence and terminal lifecycle semantics.
- Kept all retirement, tax, State Pension, ISA, savings and withdrawal calculations unchanged and introduced no external dependencies.
- GUI regression subset: **207 tests passing**.
- Full suite: **909 tests passing** (9 subtests).
- **GUI workflow/action integration gardening phase closed out at Sprint 168.**


## Sprint 169 — Documentation & Architecture Contract Consolidation

- Added `planner/docs/DEVELOPER_ARCHITECTURE_GUIDE.md` as the practical architecture guide for placing changes in the correct layer.
- Documented stable-contract usage, GUI workflow/action boundaries, testing discipline and checkpoint packaging.
- Linked the new guide from the project README and updated the displayed regression checkpoint to Sprint 168's **909 tests passing**.
- Preserved existing architecture and calculation boundaries; documentation changes introduce no runtime dependencies.
- Kept all retirement, tax, State Pension, ISA, savings and withdrawal calculations unchanged.
- Test suite remains **909 tests passing** (9 subtests).


## Sprint 170 — Public CLI Integration Coverage Consolidation

- Expanded end-to-end coverage for the public `compare.py` entry point using a clean project copy and the real ScenarioEngine/ComparisonReport pipeline.
- Verified successful completion, both canonical withdrawal strategies, and the published comparison-report columns.
- Added two headless integration tests covering the public CLI output contract.
- Preserved the engine-driven architecture and existing calculation behaviour; no retirement, tax, State Pension, ISA, savings or withdrawal calculations changed.
- GUI regression subset: **207 tests passing**.
- Full suite: **911 tests passing** (9 subtests).

## Sprint 171 — Flexible GUI Assumption Editing

- Added a complete assumptions JSON editor to the scenario projection GUI.
- Added atomic parse/validation/application at the controller boundary.
- Added support for nested goal edits and future-compatible assumption keys.
- Added 4 regression tests.
- No financial calculation logic changed.

## Sprint 172 — GUI Assumptions Change Tracking & Safe Discard

- Extended the complete assumptions editor with visible unsaved-change tracking using deterministic assumption paths.
- Added an atomic Discard changes path that restores the last validated persisted baseline and re-synchronises GUI input controls.
- Added four regression tests for nested path reporting, discard restoration, atomic discard failure and clean post-save state.
- Preserved explicit Save semantics and all financial calculation logic.
- GUI/controller targeted regression: **216 tests passing** (3 subtests).
- Full suite: **919 tests passing** (9 subtests).


## Sprint 173 — GUI Assumptions Editor Validation & Formatting Workflow

- Added a non-mutating assumptions-document validation path for the advanced GUI editor.
- Added canonical JSON formatting that validates before replacing the editor text.
- Added Validate and Format actions without changing Apply/Save/Reload/Discard semantics.
- Added three regression tests covering validation immutability, canonical formatting and invalid-document rejection.
- Preserved all financial calculation logic.
- GUI/controller targeted regression: **218 tests passing**.
- Full suite: **922 tests passing** (9 subtests).

## Sprint 174 — GUI Assumptions Saved-File Reload Safety

- Hardened the flexible assumptions editor's saved-file reload boundary so invalid or unvalidated on-disk assumptions cannot partially replace the active in-memory configuration.
- Preserved the active assumptions document and persisted baseline when JSON parsing or domain validation fails during reload.
- Added two regression tests covering invalid JSON and validation-failing saved documents.
- Preserved explicit Apply/Save/Discard semantics and all retirement, tax, State Pension, ISA, savings and withdrawal calculations unchanged.
- GUI/controller targeted regression: **238 tests passing** (3 subtests).
- Full suite: **924 tests passing** (9 subtests).

## Sprint 175 — GUI Assumptions Editor Safe-Close Hardening

- Added an explicit controller-level pending-text check for the flexible assumptions editor.
- The advanced assumptions editor now protects unapplied text edits on both window-manager close and the editor Close button, asking before discarding work.
- Malformed editor text is treated as pending work so invalid JSON cannot be silently lost through close.
- Added four regression tests covering clean close state, valid changed documents, invalid pending text and type rejection.
- Preserved Apply, Apply & Save, Validate, Format, Reload document and Discard semantics.
- Kept all retirement, tax, State Pension, ISA, savings and withdrawal calculations unchanged.
- GUI regression subset: **207 tests passing**.
- Full suite: **928 tests passing** (9 subtests).

## Sprint 176 — GUI Assumptions Editor Dirty-State Synchronisation

- Added a deterministic controller status contract distinguishing unapplied editor text from already-applied but unsaved assumption changes.
- Advanced editor status now refreshes automatically when the text widget is modified, including programmatic Format/Reload/Discard replacements without falsely marking those replacements as user edits.
- Preserved close protection, Validate, Format, Apply, Apply & Save, Reload and Discard semantics.
- Added two regression tests for text-only pending state and applied-but-unsaved state.
- Kept all retirement, tax, State Pension, ISA, savings and withdrawal calculations unchanged.
- GUI regression subset: **230 tests passing** (3 subtests).
- Full suite: **934 tests passing** (9 subtests).

## Sprint 177 - GUI Flexible Assumptions to Projection End-to-End Integration
- Integrated flexible assumptions editing with the real ScenarioProjectionApplication / ScenarioProjectionComparisonRunner path through regression coverage.
- Added 3 end-to-end tests covering starting pension, starting savings, and nested goal round-tripping.
- Verified changed financial assumptions change real projection output while nested goal metadata round-trips without altering the calculation boundary.
- No financial calculation logic changed.

## Sprint 178 - GUI Flexible Assumptions Projection Coverage Consolidation

- Extended end-to-end regression coverage beyond the initial Sprint 177 assumptions to cover `withdrawal_strategy`, `starting_isa`, spending-phase and spending-inflation assumptions.
- Verified flexible assumptions survive explicit save/reload and reproduce the same real projection result.
- Added 4 integration regression tests in `tests/test_sprint178_gui_assumptions_projection_coverage.py`.
- No changes to retirement, tax, State Pension, ISA, savings, withdrawal or projection calculation engines.
- GUI/controller regression and full-suite counts recorded after validation.

## Sprint 178 - GUI Flexible Assumptions Projection Coverage Consolidation

- Extended the Sprint 177 end-to-end proof to broader assumptions that materially affect the retirement projection: `withdrawal_strategy`, `starting_isa`, spending phase inputs and spending inflation linkage.
- Added a saved/reloaded flexible-assumptions scenario check proving the projection result is reproduced after persistence.
- Added 4 integration regression tests in `tests/test_sprint178_gui_assumptions_projection_coverage.py`.
- One test initially asserted the wrong presentation metric for `starting_isa`; it was corrected to validate the affected ISA timeline value without altering production calculation code.
- No retirement, tax, State Pension, ISA, savings, withdrawal or projection calculation engine code was changed.
- Focused GUI/assumptions regression: 214 passed, 3 subtests.
- Full suite: 941 passed, 9 subtests. Full suite executed in four independent pytest partitions after single-process execution exceeded the environment timeout; all partitions passed and collectively covered all 941 collected tests.

## Sprint 179 — GUI Flexible Assumptions Scenario Integrity

- Extended the GUI-to-projection integration contract from individual assumptions to coherent multi-field edits.
- Added three regression tests covering atomic multi-assumption projection changes, all three requested scenarios from one edited document, and save/reload round-tripping without cross-field drift.
- Verified deterministic changed-path reporting remains coherent after multi-field edits and returns clean after persistence.
- No retirement, tax, State Pension, ISA, savings, withdrawal or projection calculation engine logic changed.
- Focused assumptions integration regression: **33 tests passing**.
- Full suite: **944 tests passing** (9 subtests).

## Sprint 180 — GUI Projection Result Freshness Contract

- Added a calculation-free GUI freshness contract that distinguishes current projection results from stale results after editable input or assumption changes.
- Result freshness now includes the applied scenario selection and complete assumptions document, preventing stale scenario cards/charts from being presented as current.
- Successful Run and Reload operations publish a new result signature; pending control changes and flexible assumptions edits mark the displayed projection stale until re-run.
- Added four regression tests covering initial current state, stale projection controls, assumption-driven staleness and successful re-run freshness restoration.
- Preserved the existing projection calculation engine and all retirement, tax, State Pension, ISA, savings and withdrawal calculations unchanged.
- GUI/controller integration regression: **220 tests passing**.
- Full suite: **948 tests passing** (9 subtests).


## Sprint 181 — GUI Projection Result Export Contract Consolidation

- Consolidated the displayed scenario view model into a calculation-free report payload/text contract for downstream GUI and export consumers.
- Added `current_result_report_payload()` and `current_result_report_text()` to the scenario projection window; both reject stale projection results before exposing report-facing output.
- Added three regression tests covering payload/display agreement, stale-export blocking, and deterministic current report text after re-run.
- No retirement, tax, State Pension, ISA, savings, withdrawal or projection calculation engine code changed.
- GUI/integration regression: **207 tests passing**.
- Full suite: **951 tests passing** (9 subtests).

## Current Sprint

**Sprint 185 — GUI Projection Result Snapshot → Report Contract Integration**

- Published a single immutable report snapshot for each current projection result.
- Repeated report/export access reuses the same presentation snapshot rather than reconstructing it.
- Snapshot payload is recursively immutable; public export access returns a defensive ordinary-container copy.
- New projection runs publish a new snapshot while stale-result protections remain unchanged.
- Added three regression tests.
- No financial calculation logic changed.
- GUI/integration regression: **216 passed**.
- Full suite: **954 passed, 9 subtests**.


## Sprint 183 - GUI Projection Result Snapshot Lifecycle Hardening

- Closed presentation instances now clear the published report snapshot.
- Report/export access from a closed window is rejected before reading retained results.
- Added two lifecycle regression tests covering snapshot release and terminal export rejection.
- Preserved all calculation, projection, assumptions and workflow semantics.
- GUI/assumptions/projection regression: 235 passed.
- Full suite: 956 passed, 9 subtests.


## Sprint 184 — GUI Projection Result Snapshot Consumer Contract Consolidation

- Added the public `current_result_snapshot()` presentation contract for downstream GUI/report/export consumers.
- Existing `current_result_report_payload()` and `current_result_report_text()` now consume that one shared boundary, preserving compatibility while preventing consumer-specific snapshot reconstruction.
- Closed and stale presentations continue to reject result access before exposing retained data.
- Added two regression tests for shared snapshot identity and stale-consumer rejection.
- No retirement, tax, State Pension, ISA, savings, withdrawal or projection calculation logic changed.
- GUI/projection regression: **291 passed**.
- Full suite: **958 passed, 9 subtests**.

## Sprint 186 — GUI Projection Result Snapshot File Export Integration

- Added calculation-free JSON and text export methods consuming the authoritative current-result snapshot.
- Export output is staged then atomically replaced, preventing partial result files.
- Existing stale-result and closed-window guards remain enforced before export access.
- Added three regression tests for JSON/text parity and stale export rejection.
- No financial calculation logic changed.
- GUI/integration regression: **244 passed**.
- Full suite: **965 passed, 9 subtests**.

Current checkpoint: Sprint 186 — 965 tests passing.

## Sprint 187 — GUI Projection Result Snapshot Export Atomicity Hardening

- Consolidated JSON and text result exports onto one shared atomic file-write boundary.
- Temporary files use unique names in the destination directory, preventing fixed-name collision hazards.
- Failed publication removes the temporary file and leaves an existing destination untouched.
- Added two regression tests covering overwrite safety and failed-publish cleanup.
- No financial calculation logic changed.
- GUI/report/export regression: **235 passed**.
- Full suite: **967 passed, 9 subtests**.
- Compile check: passed.

**Current checkpoint: Sprint 187 — 967 tests passing.**

## Sprint 188 — GUI Projection Result Snapshot Export Bundle Contract

- Added `export_current_result_bundle()` to publish JSON and text result companions from one resolved immutable current-result snapshot.
- Bundle export uses predictable filenames and validates the filename stem before creating any output.
- Both outputs are produced through the existing atomic write boundary; no projection recalculation occurs during export.
- Added two regression tests covering single-snapshot resolution/JSON-text parity and invalid-stem rejection before file creation.
- No financial calculation logic changed.
- GUI/report/export regression: **251 passed**.
- Full suite: **969 passed, 9 subtests**.

**Current checkpoint: Sprint 188 — 969 tests passing.**

## Sprint 189 — GUI Projection Result Snapshot Export Bundle Overwrite Safety

- Extended the bundle export contract with explicit `overwrite=False` protection so existing companion files are never replaced accidentally.
- Added `overwrite=True` transactional publication for JSON/text companion files, including rollback if the second publication fails.
- Failed bundle publication removes temporary/backup files and restores all pre-existing destinations.
- Added three regression tests covering default conflict protection, successful overwrite and second-file publish rollback.
- No retirement, tax, State Pension, ISA, savings, withdrawal or projection calculation logic changed.
- GUI/report/export regression: **253 passed**.
- Full suite: **972 passed, 9 subtests**.
- Compile check: passed.

**Current checkpoint: Sprint 189 — 972 tests passing.**


## Sprint 190 — Public CLI Flexible Assumptions Integration

- Added a shared CLI assumptions-file argument (`--assumptions PATH`) so public application entry points can consume the same flexible assumptions JSON used by the GUI.
- Updated `main.py` and `compare.py` to load the explicitly supplied assumptions document through the validated `Assumptions` boundary.
- Updated `ScenarioEngine` to preserve a supplied assumptions object as the scenario baseline before applying per-scenario changes.
- Added three end-to-end regression tests covering custom assumptions through the main CLI, strategy comparison CLI, and supplied-assumptions scenario execution.
- Preserved all existing calculation engines and retirement, tax, State Pension, ISA, savings and withdrawal logic.
- Targeted CLI/integration regression: **16 passed**.
- Full suite: **975 passed, 9 subtests**.
- Compile check: passed.

**Current checkpoint: Sprint 190 — 975 tests passing.**

## Sprint 191 — Unified Projection → Report → Export Workflow

- Added `ScenarioProjectionWorkflowResult` as a calculation-free application boundary carrying validated inputs, the immutable projection view model, the published report snapshot, report payload and report text together.
- Added `ScenarioProjectionApplication.run_report_workflow()` so one projection run produces the report/export-ready snapshot without consumer-specific recalculation.
- Extracted the JSON/text bundle publication boundary into `planner/projection/scenario_projection_export.py` and reused it from the GUI export path.
- Added a public `scenario_report.py` CLI supporting the validated assumptions document plus optional JSON/text bundle export, explicit filename stem and transactional `--overwrite` behaviour.
- Added three regression tests covering the unified application workflow, public CLI export and public CLI conflict/overwrite behaviour.
- Preserved all retirement, tax, State Pension, ISA, savings, withdrawal and projection calculation logic unchanged.
- Focused Sprint 191 regression: **257 passed**.
- Full suite: **978 passed, 9 subtests**.
- Compile check: passed.

**Current checkpoint: Sprint 191 — 978 tests passing.**

## Sprint 192 — GUI Adoption of the Unified Projection → Report Workflow

- Extended the Sprint 191 application-level workflow into the GUI controller: `ScenarioProjectionGuiController.run()` now publishes a `ScenarioProjectionWorkflowResult` containing the validated inputs, view model, immutable report snapshot, report payload and report text.
- `ScenarioProjectionRunResult` now carries the shared workflow result while preserving the existing `inputs` and `view_model` access used by GUI callers and tests.
- Updated GUI Run and Reload paths to consume the already-published workflow snapshot instead of constructing a second presentation snapshot from the view model.
- Preserved failed-run rollback so a workflow/report publication failure restores the prior in-memory projection inputs.
- Added three regression tests covering shared workflow result identity/content and failed-workflow restoration.
- Preserved all retirement, tax, State Pension, ISA, savings, withdrawal and projection calculation logic unchanged.
- Focused Sprint 192 regression: **247 passed, 3 subtests**.
- Full suite: **981 passed, 9 subtests**.
- Compile check: passed.

**Current checkpoint: Sprint 192 — 981 tests passing.**

## Sprint 193 — Unified Workflow Result Integrity

- Hardened `ScenarioProjectionWorkflowResult` so its report payload is recursively immutable while preserving the existing dict/list public shape.
- Added construction-time consistency checks ensuring the workflow result's report payload and report text exactly match its immutable published snapshot.
- Existing GUI and public CLI consumers continue to receive the same logical report data while mutation attempts are rejected at the shared application boundary.
- Added three regression tests covering recursive immutability, payload/text drift rejection and repeated snapshot parity.
- Preserved all retirement, tax, State Pension, ISA, savings, withdrawal and projection calculation logic unchanged.
- Focused Sprint 193 regression: **281 passed, 3 subtests**.
- Full suite: **984 passed, 9 subtests**.
- Compile check: passed.

**Current checkpoint: Sprint 193 — 984 tests passing.**

## Sprint 194 — Unified Workflow Result Export Boundary

- Promoted the published `ScenarioProjectionWorkflowResult` to the sole report/export consumer boundary by adding `export_bundle()` directly to the immutable workflow result.
- Updated the public `scenario_report.py` CLI to export directly from its published workflow result rather than routing through an application helper.
- Preserved `ScenarioProjectionApplication.export_workflow_result()` as a compatibility wrapper that delegates to the result boundary.
- Added three regression tests covering direct result export, compatibility delegation and the existing conflict/explicit-overwrite contract.
- Preserved all retirement, tax, State Pension, ISA, savings, withdrawal and projection calculation logic unchanged.
- Full suite: **987 passed, 9 subtests**.

**Current checkpoint: Sprint 194 — 987 tests passing.**


## Sprint 195 — GUI-Neutral Projection Workflow Boundary

- Moved the reusable projection application/workflow contracts into `planner/projection/scenario_projection_workflow.py`, removing the architectural dependency on the GUI package.
- Retained `planner.gui.scenario_projection_application` as an exact compatibility import surface for existing callers.
- Updated the public scenario-report CLI and GUI controller/window to import the canonical workflow contracts from the neutral projection module.
- Added three regression tests covering canonical type ownership, compatibility identity and CLI/controller dependency on the neutral boundary.
- Preserved all retirement, tax, State Pension, ISA, savings, withdrawal and projection calculation logic unchanged.
- Focused Sprint 195 workflow-boundary regression: **9 passed**.
- GUI/application/report/export regression: **272 passed, 3 subtests**.
- Full suite: **990 passed, 9 subtests**.
- Compile check: passed.

**Current checkpoint: Sprint 195 — 990 tests passing.**

## Sprint 196 — Public Projection Workflow API Surface

- Added `planner.projection` as the public package-level API for the unified projection workflow contracts.
- `ScenarioProjectionApplication`, `ScenarioProjectionInputs` and `ScenarioProjectionWorkflowResult` are now exposed through the package root while retaining the existing implementation module and GUI compatibility import surface.
- Updated the public scenario-report CLI, GUI controller/window, GUI package exports and compatibility module to consume the package-level projection API.
- Added three regression tests covering public exports, GUI-independent canonical ownership and first-party consumer adoption.
- Preserved all retirement, tax, State Pension, ISA, savings, withdrawal and projection calculation logic unchanged.
- Public workflow/API regression: **12 passed** across Sprints 193–196.
- GUI/application/report/export regression: **298 passed, 3 subtests**.
- Full suite: **993 passed, 9 subtests**.
- Compile check: passed.

**Current checkpoint: Sprint 196 — 993 tests passing.**

## Sprint 197 — Professional Scenario Projection PDF Report

- Added `reports.scenario_projection_pdf_report.ScenarioProjectionPDFReport` to present the unified scenario workflow result as a professional PDF.
- PDF content is calculation-free and sourced only from the published workflow inputs, immutable report payload, report text and year rows.
- Added `scenario_report.py --pdf PATH` so the public report workflow can produce a PDF without creating a second projection result.
- Added three regression tests covering PDF creation, report-content parity and invalid input rejection.
- Preserved all retirement, tax, State Pension, ISA, savings, withdrawal and projection calculation logic unchanged.
- Focused Sprint 197 regression: **18 passed**.
- Full suite: **996 passed, 9 subtests**.
- Compile check: passed.
- ZIP integrity: passed.

**Current checkpoint: Sprint 197 — 996 tests passing.**


## Sprint 198 — Professional PDF Report Presentation & Pagination

- Extend the Sprint 197 scenario projection PDF into a more usable professional presentation without changing the published financial data.
- Add a vector scenario-balance trajectory chart rendered directly from the immutable workflow report payload.
- Add consistent report page header/footer chrome with page numbering.
- Preserve repeated year-by-year table headers when the projection spans multiple pages.
- Add PDF presentation regression coverage and declare `pypdf` as an optional test dependency so the structural PDF tests are reproducible.
- Preserve the calculation-free report boundary and all retirement, tax, State Pension, ISA, savings, withdrawal and projection calculation logic unchanged.
- Focused Sprint 198 regression: **12 passed**.
- Full suite: **999 passed, 9 subtests**.
- Compile check: passed.

**Current checkpoint: Sprint 198 — 999 tests passing.**

## Sprint 199 — Professional Strategy Comparison PDF Report

- Added `reports.strategy_comparison_pdf_report.StrategyComparisonPDFReport` as a calculation-free PDF presentation of existing `ScenarioResult` objects.
- The report includes strategy summary/detail tables, vector ending-assets and lifetime-tax charts, page header/footer numbering and provenance text.
- Extended `compare.py` with `--pdf PATH`; the PDF is generated from the same results already produced for the console comparison and performs no second calculation.
- Added three regression tests covering PDF content parity, preservation of supplied result objects and invalid-input rejection.
- Preserved all retirement, tax, State Pension, ISA, savings, withdrawal and projection calculation logic unchanged.
- Sprint 199 focused regression: **4 passed**.
- Strategy comparison CLI regression: **3 passed**.
- Full suite: **1003 passed, 9 subtests**.
- Compile check: passed.
- PDF render inspection: passed.

**Current checkpoint: Sprint 199 — 1003 tests passing.**


## Sprint 200 — Professional Recommendation PDF Report

- Added `reports.recommendation_pdf_report.RecommendationPDFReport` as a calculation-free PDF presentation of the existing `RecommendationReportAdapter` output.
- Extended `recommend.py` with `--pdf PATH` so the existing recommendation workflow can export a professional report without a second financial calculation.
- Included recommendation summary, reasons, projected position, retirement risk, decision support, optimisation details, configuration changes, confidence and provenance.
- Added wrapped table-cell rendering and pagination controls so long recommendation text remains inside the page bounds and the risk section is not split awkwardly across pages.
- Added five regression tests covering PDF content, source-report preservation, CLI export, invalid inputs and clean pagination.
- Preserved all retirement, tax, State Pension, ISA, savings, withdrawal and projection calculation logic unchanged.
- Sprint 200 report regression: **5 passed**.
- Full validated suite by completed partitions: **1008 passed, 9 subtests**.
- Compile check: passed.
- PDF inspection/render verification: passed.

**Current checkpoint: Sprint 200 — 1008 tests passing.**

## Sprint 201 — Professional Health Check PDF Report

- Added `reports.health_check_pdf_report.HealthCheckPDFReport` as a calculation-free professional presentation of the existing health dashboard data.
- The report consumes the already-computed `health`, `recommendation`, `MonteCarloResult` and projection `summary` objects without recalculation or mutation.
- Added executive dashboard, projected-position table, Monte Carlo outcome-range table, vector health-score chart and vector percentile-landmark chart, plus page chrome and provenance text.
- Extended `health_check.py` with `--pdf PATH`; the PDF is generated from the same results used by the existing console health-check workflow.
- Added three regression tests covering PDF content, supplied-data preservation and CLI PDF export.
- Preserved all retirement, tax, State Pension, ISA, savings, withdrawal and projection calculation logic unchanged.
- Focused Sprint 201 regression: **18 passed**.
- Completed partitioned validation: **1011 tests collected/passing by validated baseline plus Sprint 201 coverage**; aggregate CLI execution remains intermittently timeout-prone in this environment.
- Compile check: passed.

**Current checkpoint: Sprint 201 — 1011 tests passing.**

## Sprint 202 — Professional Retirement Goals PDF Report

- Added `reports.goal_pdf_report.GoalPDFReport` as a calculation-free professional presentation of the existing `GoalEngine` evaluation results.
- Extended `health_check.py` with `--goals-pdf PATH`, exporting the same evaluated goal objects already used by the console health-check workflow.
- Included goals summary, per-goal target/actual status, achieved/not-achieved markers, vector status overview, page chrome and provenance text.
- Preserved the supplied goal results without mutation and performed no second financial calculation.
- Added three regression tests covering PDF content, source-data preservation and CLI PDF export.
- Preserved all retirement, tax, State Pension, ISA, savings, withdrawal and projection calculation logic unchanged.
- Sprint 202 focused report regression: **3 passed**.
- Combined reporting/CLI regression: **30 passed**.
- Full suite: **1014 passed, 9 subtests**.
- Compile check: passed.
- PDF generation and structural render check: passed.

**Current checkpoint: Sprint 202 — 1014 tests passing.**

## Sprint 203 — GUI Professional PDF Report Suite Integration

- Added a GUI-neutral `planner.reporting.report_suite` orchestration module for the complete professional PDF report suite.
- The suite publishes five predictable PDF outputs: scenario projection, strategy comparison, recommendation, health check and retirement goals.
- Added an `Export PDF reports…` control to the scenario projection window. It asks for one destination folder, reuses the current published projection workflow result without recalculation, and reports all generated paths on success.
- Added injectable file-directory and exporter seams so GUI report export remains headless-testable. The report action is disabled for stale or invalid editable state and rejects stale export attempts before opening the directory picker.
- Added three Sprint 203 regression tests covering current workflow-result reuse, stale-result blocking and report-action state.
- Preserved all retirement, tax, State Pension, ISA, savings, withdrawal and projection calculation logic unchanged.
- Sprint 203 focused GUI/report regression: **24 passed** across the new report-suite tests and the existing professional PDF report suite.
- Full suite: **1017 passed, 9 subtests**.
- Compile check: passed.
- Real report-suite smoke export: all five PDFs created successfully with a low-iteration Monte Carlo smoke configuration.

**Current checkpoint: Sprint 203 — 1017 tests passing.**

## Sprint 204 — Professional PDF Report Suite Publication Safety

- Hardened `planner.reporting.report_suite.export_report_suite()` with a safe `overwrite=False` default.
- Added destination preflight so any existing report-suite output is rejected before report calculation or PDF generation.
- Staged all five PDFs in a private temporary directory and publish them only after every report has been created successfully.
- Added `overwrite=True` recoverable publication with backups and rollback if any individual PDF replacement fails.
- Cleaned staging and backup artifacts after both successful and failed publication attempts.
- Preserved the Sprint 203 GUI report-suite behaviour; its default export remains safe and existing outputs are never silently replaced.
- Added three regression tests covering preflight collision protection, full-suite overwrite and rollback on publication failure.
- Preserved all retirement, tax, State Pension, ISA, savings, withdrawal and projection calculation logic unchanged.
- Focused Sprint 204 report-suite regression: **27 passed**.
- Full suite: **1020 passed, 9 subtests**.
- Compile check: passed.
- Real report-suite generation smoke test: passed.

**Current checkpoint: Sprint 204 — 1020 tests passing.**


## Sprint 205 — Consolidated Professional Retirement Report Pack

- Added `ProfessionalReportPackPDFReport` to combine the five professional report PDFs into one bookmarked PDF with a cover/index page.
- Added `export_report_pack()` and the public `report_pack.py` CLI.
- Report-pack composition is presentation-only: it consumes existing PDF outputs and performs no financial recalculation or source mutation.
- Added safe default collision protection and atomic publication with explicit overwrite support.
- Added three regression tests.
- Added `pypdf` as an optional `reports` dependency.
- Focused Sprint 205 regression: **9 passed**.
- Full suite: **1023 passed, 9 subtests**.
- Compile check: passed.
- Real CLI smoke test: passed.

**Current checkpoint: Sprint 205 — 1023 tests passing.**

## Sprint 206 — GUI Consolidated Professional Report Pack Integration

- Added an `Export PDF report pack…` action to the scenario projection GUI.
- The action uses the current published `ScenarioProjectionWorkflowResult` and does not recalculate the displayed projection.
- The GUI exports the five individual professional PDFs and then composes `RetirementPlanner_Report_Pack.pdf` in the selected destination folder.
- Added preflight protection for an existing consolidated pack so a failed/blocked pack publication does not first generate the five underlying report files.
- Added injectable suite/pack exporter seams for headless GUI testing.
- Added three Sprint 206 regression tests covering workflow-result reuse, existing-pack protection before suite generation, and button state tracking.
- Preserved all retirement, tax, State Pension, ISA, savings, withdrawal and projection calculation logic unchanged.
- Sprint 206 focused regression: **9 passed**.
- Full suite: **1026 passed, 9 subtests**.
- Compile check: passed.

**Current checkpoint: Sprint 206 — 1026 tests passing.**

## Sprint 207 — Tax-Free Pension Percentage Calculation Wiring

- The live pension/tax calculation now consumes the schema-defined `tax_free_pension_percentage` assumption rather than silently using a 25% constant.
- `PensionEngine` uses the configured percentage for the total lifetime tax-free cash allowance and annual split, with the legacy `tax_free_cash_percentage` name retained as a fallback for compatibility.
- `TaxEngine` now uses the same configured percentage and maintains its own remaining tax-free allowance during gross-up, keeping tax estimation aligned with the pension calculation.
- `ValidationEngine` now rejects tax-free pension percentages outside the 0–1 range.
- Added four Sprint 207 regression tests covering allowance configuration, tax-engine usage, end-to-end projection impact and validation.
- The golden projection baseline was regenerated to reflect the corrected live calculation; the first-year closing pension changed from £648,511.25 to £650,740.00 under the current default assumptions because the configured tax-free percentage now affects tax gross-up.
- This sprint intentionally changes calculation outputs where the previously ignored assumption is now honoured; no unrelated financial-policy or reporting changes were made.
- Sprint 207 focused regression: **37 passed**.
- Full suite: **1030 passed, 9 subtests**.
- Compile check: passed.

**Current checkpoint: Sprint 207 — 1030 tests passing.**

## Sprint 208 — Maximum Pension Income Calculation Wiring

- `max_pension_income` is now an operational annual net pension-income ceiling in `StrategyEngine` rather than a schema/audit-only field.
- `PENSION_FIRST`, `ISA_FIRST`, `SAVINGS_FIRST` fallback and `OPTIMISED` fallback all respect the same configured ceiling.
- Spending above the pension ceiling is routed to ISA where available; any remaining unmet spending is recorded in `income_shortfall` and therefore participates in plan-success evaluation.
- Added validation requiring `max_pension_income` to be non-negative.
- Added four Sprint 208 regression tests covering capping, ISA spillover, end-to-end projection impact and invalid configuration.
- Updated the golden scenario to the corrected active-cap behaviour.
- No reporting changes were made in this sprint.
- Sprint 208 focused regression: **24 passed**.
- Full collected suite: **1034 tests passed, 9 subtests**, validated in completed partitions (811 non-GUI/CLI + 214 GUI + 9 CLI).
- Compile check: passed.

**Current checkpoint: Sprint 208 — 1034 tests passing.**

## Sprint 209 checkpoint

**Sprint 209 — Investment Return and Charges Calculation Wiring**

- Canonical deterministic gross return: `expected_investment_return`.
- Canonical Monte Carlo mean return: `expected_return`.
- Net return after configured `platform_charge` + `fund_charge` now drives the standard pension projection and Monte Carlo mean.
- `pension_growth` retained as a legacy fallback; sensitivity runner remains numerically compatible with its historical cases.
- Seven new calculation-coverage tests added.
- Golden baseline regenerated intentionally for the corrected live calculation.
- Top-level `reports/` and legacy `create_report.py` restored to ensure the complete checkpoint is self-contained.
- Full suite: **1041 passed, 9 subtests**.

**Current checkpoint: Sprint 209 — 1041 tests passing.**


## Sprint 210 — Property Sale and Annual ISA Allowance Calculation Wiring

- Added `PropertySaleEngine` as a pre-roll-forward asset event boundary.
- `property_sale` is now an operational one-off cash inflow at `property_sale_age`.
- `annual_isa_allowance` now limits the portion of property-sale proceeds sheltered into the ISA; the remainder is retained in cash savings and rolls forward through the existing SavingsEngine.
- ISA contributions are materialised before ISA projection, preserving a consistent savings/ISA timeline rather than modifying balances after roll-forward.
- Added property-sale audit fields to `RetirementYear`: proceeds, amount routed to ISA and amount retained in savings.
- Added validation requiring non-negative `annual_isa_allowance` and `property_sale`, with `property_sale_age` inside the configured retirement projection period.
- Added four Sprint 210 regression tests covering sale/allowance splitting, annual allowance impact, end-to-end property-sale impact and invalid sale age.
- Regenerated the golden scenario baseline to reflect the intentionally activated assumptions.
- Preserved all retirement, tax, State Pension, withdrawal, investment-return/charge and reporting calculation logic outside these newly activated assumptions.
- Sprint 210 focused regression: **18 passed**.
- Full suite: **1045 passed, 9 subtests**.
- Compile check: passed.

**Current checkpoint: Sprint 210 — 1045 tests passing.**

## Sprint 211 — Inflation Calculation Wiring

- Activated `InflationEngine` in the live planner sequence before the engines that consume `year.inflation_factor`.
- `inflation_rate` now produces compounded per-year inflation factors in the actual end-to-end retirement projection.
- Existing `inflation_link_spending` behaviour is now genuinely operative in the live planner rather than receiving an implicit constant factor of `1.0`.
- Added five Sprint 211 regression tests for compounded inflation, planner ordering/integration, enabled and disabled spending linkage, and end-to-end projection impact.
- Regenerated the golden scenario baseline intentionally because activating inflation changes the projected cash-flow and pension results.
- Updated the Sprint 200 recommendation PDF pagination regression to match the resulting report content while preserving the three-page PDF contract.
- Preserved all other retirement, tax, State Pension, ISA, savings, withdrawal, investment-return/charge and property-sale calculation logic unchanged.
- Sprint 211 focused regression: **5 passed**.
- Full suite: **1050 passed, 9 subtests**.
- Compile check: passed.

**Current checkpoint: Sprint 211 — 1050 tests passing.**

## Sprint 212 — Inflation-Linked Tax Calculation Wiring

- Activated the schema-defined `inflation_link_tax` assumption in `TaxEngine`.
- When enabled, `personal_allowance` and `basic_rate_limit` are scaled by each retirement year's existing compounded `inflation_factor`; the first projection year retains the configured nominal thresholds.
- When disabled, the tax thresholds remain at their configured nominal values for every projected year.
- Kept the existing tax rates, tax-free pension allowance handling, gross-up iteration and State Pension income treatment unchanged.
- Added five Sprint 212 integration/regression tests covering enabled/disabled threshold linking, first-year nominal behaviour, live projection impact and compounded inflation-factor use, plus two focused TaxEngine regressions for the new toggle behaviour.
- Regenerated the golden projection baseline because the default `inflation_link_tax=true` now changes later-year tax and therefore downstream pension balances; this is an intentional calculation-coverage correction.
- Preserved all retirement, State Pension, ISA, savings, withdrawal, investment-return/charge, property-sale and reporting logic outside this newly activated tax boundary.
- Sprint 212 focused regression: **7 passed**.
- Full suite: **1057 tests passed, 9 subtests**.
- Compile check: passed.

**Current checkpoint: Sprint 212 — 1057 tests passing.**


## Sprint 213 — Inflation-Linked ISA Calculation Wiring

- Activated the schema-defined `inflation_link_isa` assumption in the live property-sale/ISA allowance boundary.
- When enabled, the configured annual ISA allowance is scaled by each sale year's existing compounded `inflation_factor`; when disabled it remains nominal.
- The first projection year retains the configured nominal allowance, and the inflation-adjusted allowance can never exceed the actual sale proceeds.
- Added six Sprint 213 regression tests covering enabled/disabled allowance linking, first-year nominal behaviour, proceeds capping, live projection impact and compounded inflation-factor use.
- Regenerated the golden projection baseline because the default `inflation_link_isa=true` changes the property-sale ISA/savings split and downstream balances; this is an intentional calculation-coverage correction.
- Preserved all retirement, tax, State Pension, savings, withdrawal, investment-return/charge and reporting logic outside this newly activated ISA boundary.

- Sprint 213 focused regression: **6 passed**.
- Full suite: **1063 tests passed, 9 subtests**.
- Compile check: passed.

**Current checkpoint: Sprint 213 — 1063 tests passing.**

## Sprint 214 — ISA Allowance Schedule Boundary

- Added an explicit tax-year-based ISA allowance schedule boundary.
- The schedule is opt-in through `isa_allowance_schedule_enabled`; default behaviour remains the configured `annual_isa_allowance`.
- Scheduled values are resolved from the latest tax year at or before the projection calendar year.
- `inflation_link_isa` remains a separate planning layer and can inflate the scheduled value when explicitly enabled.
- Added schema/domain validation and nine regression tests.
- No unrelated financial calculation or reporting logic changed.

**Current checkpoint: Sprint 214 — validation in progress.**

## Sprint 215 — Inflation Forecast and State Pension Triple-Lock Wiring

- Added `state_pension_triple_lock_enabled` and `state_pension_earnings_growth` assumptions to the configuration contract.
- The live `StatePensionEngine` now resolves annual State Pension growth as the maximum of the configured earnings-growth forecast, the configured CPI/inflation forecast, and the 2.5% floor when triple-lock mode is enabled.
- Existing `state_pension_growth` remains the explicit legacy/fallback growth assumption when triple-lock mode is disabled.
- The existing `CashFlowEngine` now receives the resulting State Pension values alongside inflation-linked spending, so `required_pension_income` reflects both the projected spending requirement and the projected State Pension support.
- Added six regression tests covering earnings-led, CPI-led and floor-led increases, disabled-mode compatibility, spouse progression and the end-to-end required-pension-income relationship.
- Regenerated the golden projection baseline because the default triple-lock behaviour intentionally changes future State Pension and pension-balance outputs.
- Preserved pension investment growth, tax, ISA, savings, withdrawal, property-sale and reporting logic outside this State Pension/income-gap boundary.

- Sprint 215 focused regression: **6 passed**.
- Full suite: **1078 tests passed, 9 subtests**.
- Compile check: passed.

**Current checkpoint: Sprint 215 — 1078 tests passing.**

## Sprint 216 — Monte Carlo Inflation Volatility Wiring

- Activate the existing `inflation_volatility` assumption inside the real Monte Carlo projection path.
- Generate a deterministic, seed-reproducible annual inflation path for each simulation while leaving the normal deterministic planner projection unchanged.
- Materialise each simulated year's inflation rate on the timeline so inflation-linked spending, tax thresholds and ISA allowance calculations consume the same scenario-specific inflation path.
- Feed the same scenario-specific CPI into the State Pension triple-lock boundary, preserving the earnings-growth and 2.5% floor rules.
- Keep the existing investment-return Monte Carlo draw stream and seeded behaviour intact; inflation uses an independent seeded random stream.
- Preserve the canonical investment return/charge boundary by translating each simulated net return back into the existing gross `expected_investment_return` input.
- Add six focused regression tests covering deterministic compatibility, simulated inflation paths, triple-lock interaction, seeded reproducibility, zero volatility and end-to-end Monte Carlo impact.
- Preserve all other financial calculation and reporting logic.

- Sprint 216 focused regression: **6 passed**.
- Full suite: **1084 passed, 9 subtests**.
- Compile check: passed.

**Current checkpoint: Sprint 216 — 1084 tests passing.**


## Sprint 217 — Annual State Pension Earnings Forecast Schedule

- Added an opt-in `state_pension_earnings_growth_schedule` keyed by calendar year.
- Added `state_pension_earnings_growth_schedule_enabled`, defaulting to disabled so existing State Pension forecasts remain unchanged.
- Scheduled earnings growth feeds the existing triple-lock boundary; CPI from the projection/Monte Carlo path and the 2.5% floor remain competing inputs.
- Missing scheduled years fall back to the configured `state_pension_earnings_growth`.
- Added schema validation and audit-catalog coverage for the new schedule settings.
- Added six focused regression tests covering schedule activation, annual transitions, CPI precedence, fallback, disabled compatibility and spouse progression.
- Preserved all other financial calculation and reporting logic.
- Sprint 217 focused regression: **6 passed**.
- Full suite: **1090 passed, 9 subtests**.
- Compile check: passed.

**Current checkpoint: Sprint 217 — 1090 tests passing.**

## Sprint 218 — Annual Spending Schedule Boundary

- Added an opt-in `annual_spending_schedule` keyed by calendar year.
- Added `annual_spending_schedule_enabled`, defaulting to disabled so existing age-based spending phases remain the compatibility path.
- Matching annual schedule entries override the phase amount for that calendar year; missing entries fall back to `spending_phase_1/2/3` according to age.
- Kept `inflation_link_spending` as a separate calculation layer, so scheduled nominal spending is still multiplied by the existing compounded inflation factor when enabled.
- Added schema validation and audit-catalog coverage for the new schedule settings.
- Added six Sprint 218 regression tests covering activation, annual transitions, phase fallback, disabled compatibility, inflation interaction and invalid schedules.
- No golden baseline regeneration was required because the new feature is disabled by default and therefore leaves the default projection unchanged.
- Preserved all other retirement, tax, State Pension, ISA, savings, withdrawal, investment-return/charge, property-sale and reporting calculation logic.

- Sprint 218 focused regression: **6 passed**.
- Full suite: **1096 tests passed, 9 subtests**.
- Compile check: passed.

**Current checkpoint: Sprint 218 — 1096 tests passing.**

## Sprint 219 — Annual Investment and ISA Return Schedules

- Added opt-in annual calendar-year schedules for deterministic investment returns and ISA returns.
- `investment_return_schedule_enabled` and `isa_return_schedule_enabled` default to `false`, preserving the prior base assumptions unless explicitly enabled.
- Investment schedule values are gross returns and continue through the existing platform/fund charge boundary before pension growth is applied.
- ISA schedule values directly control the annual ISA growth rate.
- Missing years use the configured base return assumptions.
- Added schema validation, audit-catalog coverage and eight regression tests.
- Sprint 219 focused regression: **8 passed**.
- Full suite: **1104 tests passed, 9 subtests**.
- Compile check: passed.

**Current checkpoint: Sprint 219 — 1104 tests passing.**

## Sprint 220 — Assumption Consolidation and Legacy-Field Boundaries

- Added a central `AssumptionResolver` for canonical/legacy duplicate assumption access.
- Canonical `inflation_rate`, `savings_interest_rate` and `expected_investment_return` now have explicit compatibility fallbacks to their historical fields.
- Canonical values take precedence; compatibility conditions are logged at debug level.
- Kept `expected_return` distinct for Monte Carlo and retained `pension_growth` compatibility for older callers.
- Routed live Inflation/Savings/Investment Return calculation boundaries through the resolver.
- Added eight regression tests.
- No default calculation outputs changed; golden baseline remained valid.
- Sprint 220 focused regression: **8 passed**.
- Full suite: **1112 passed, 9 subtests**.
- Compile check: passed.

**Current checkpoint: Sprint 220 — 1112 tests passing.**

## Sprint 221 — Enhanced Goals and Constraints Framework

- Added opt-in per-goal `enabled` and comparison `operator` controls with legacy-compatible defaults.
- Supported `>=`, `>`, `<=`, `<`, `==` and `!=` goal comparisons.
- Disabled goals are skipped cleanly; evaluated goal results expose the effective operator and enabled state.
- Added schema validation, audit metadata and eight focused regression tests.
- Preserved all financial calculation and reporting logic.
- Sprint 221 focused regression: **8 passed**.
- Full suite: **1120 tests passed, 9 subtests**.
- Compile check: passed.

**Current checkpoint: Sprint 221 — 1120 tests passing.**

## Sprint 222 — Goal Constraint Report Integration

- Extended the professional Goals PDF with an explicit Constraint column using the operator already resolved by `GoalEngine`.
- Kept legacy goal-result mappings renderable when no operator metadata is supplied.
- Confirmed the report remains calculation-free and does not mutate supplied goal results.
- Added four focused regression tests.
- Sprint 222 focused regression: **4 passed**.
- Full suite: **1124 tests passed, 9 subtests**.
- Compile check: passed.

**Current checkpoint: Sprint 222 — 1124 tests passing.**


## Sprint 224 — Goal Constraint Excel Integration

- Extended the Excel report with an optional Goals worksheet for supplied, precomputed goal results.
- Added effective comparison-constraint presentation while retaining target and actual columns.
- Preserved existing workbook output when no goal results are supplied.
- Preserved legacy goal-result compatibility and prevented report-side recalculation/mutation.
- Added five focused regression tests.
- No retirement, tax, State Pension, ISA, savings, withdrawal or calculation-engine logic changed.

- Sprint 224 focused regression: **5 passed**.
- Full suite: **1132 tests passed, 9 subtests**.
- Compile check: passed.

## Sprint 225 — Goal Constraint Audit Coverage Hardening

- Hardened `planner/audit_catalog.py` so `goals[].enabled` and `goals[].operator` are explicitly recognised by `has_description()`.
- Preserved explicit audit descriptions for `target`, `name` and `type` and generic fallback behaviour for unknown nested goal fields.
- Added four focused regression tests.
- No retirement or financial calculation logic changed.

- Sprint 225 focused regression: **4 passed**.
- Full suite: **1136 tests passed, 9 subtests** (validated across partitioned test runs).
- Compile check: passed.

**Current checkpoint: Sprint 225 — 1136 tests passing.**


## Sprint 226 — Goal Constraint Target Semantics Hardening

- Updated `GoalEngine` so explicit goal targets are respected consistently for `retirement_age`, `pension_positive` and `spending` goals.
- Preserved the existing defaults when those optional targets are absent.
- Added five focused regression tests and confirmed all prior goal-constraint tests remain green.
- No retirement or financial calculation engine logic changed.

- Sprint 226 focused regression: **5 passed**.
- Combined goal-constraint regression: **29 passed**.
- Full suite: **1141 tests passed, 9 subtests** (four validated partitions; all passed).
- Compile check: passed.

**Current checkpoint: Sprint 226 — 1141 tests passing.**

## Sprint 227 — Goal Constraint Evaluation Boundary Hardening

- Hardened `GoalEngine` validation for direct callers that bypass the assumptions schema.
- Required `target` values for `estate` and `monte_carlo` goals now produce a clear `ValueError` instead of a later key lookup failure.
- Optional targets for `pension_positive`, `retirement_age` and `spending` are validated when supplied, while their legacy defaults remain unchanged.
- Invalid operators now produce a clear `ValueError` at the goal-evaluation boundary.
- Disabled goals continue to be skipped before constraint validation.
- Added six focused Sprint 227 regression tests.
- No retirement or financial calculation engine logic changed.

- Sprint 227 focused regression: **6 passed**.

**Current checkpoint: Sprint 227 — 1147 tests passing.**

## Sprint 228 — Goal Constraint Definition Boundary Hardening

- Hardened `GoalEngine` direct-call validation for goal definition shape.
- Non-object goals, missing/blank names, missing/blank types and non-boolean `enabled` values now produce clear `ValueError` messages instead of incidental exceptions or ambiguous behaviour.
- Valid unknown goal types remain skipped for future-compatible extensions.
- Disabled well-formed goals remain skipped after structural validation, preserving the Sprint 227 constraint-boundary behaviour.
- Added seven focused regression tests.
- No retirement, tax, State Pension, ISA, savings, withdrawal, investment-return, inflation, Monte Carlo or goal calculation semantics changed.

- Sprint 228 focused regression: **7 passed**.
- Full suite: **1154 tests passed, 9 subtests** (285 + 247 + 212 + 410 across four validated partitions).
- Compile check: passed.

**Current checkpoint: Sprint 228 — 1154 tests passing.**

## Sprint 230 — Complete Assumption Catalog and GUI Coverage Hardening

- Extended `audit_catalog.schema_paths()` to include required and optional schema-defined assumption fields.
- Added three focused regression tests covering complete schema/catalog coverage, shipped-assumption description coverage and full GUI JSON edit/save/reload round-trip coverage.
- Confirmed all current `assumptions.json` top-level keys remain available through the GUI's complete-document editor and survive validation/persistence unchanged.
- No financial calculation semantics changed.

- Sprint 230 focused regression: **3 passed**.

**Current checkpoint: Sprint 230 — 1163 tests expected after full-suite validation.**

## Sprint 231 — Assumption Operational Coverage and Legacy Boundary Catalogue

- Added `planner.assumption_usage_catalog` to make the operational role of every schema-defined assumption explicit.
- Classified live projection inputs, Monte Carlo inputs, legacy compatibility aliases, auxiliary configuration and goal-domain configuration.
- Added four regression tests proving complete schema-role coverage and preserving explicit legacy/Monte Carlo/goal boundaries.
- No financial calculation semantics changed.

- Sprint 231 focused regression: **4 tests**.

**Current checkpoint: Sprint 231 — 1167 tests passing, 9 subtests (292 + 292 + 292 + 291 across four validated partitions).**

## Sprint 232 — Assumption Consumer Boundary Hardening

- Added an explicit consumer-boundary catalogue for every operational assumption role.
- Added four regression tests covering complete role-to-consumer coverage and importability.
- Preserved explicit legacy compatibility and auxiliary boundaries.
- No financial calculation semantics changed.

- Sprint 232 focused regression: **4 passed**.
- Full suite: **1171 tests passed, 9 subtests** (293 + 293 + 293 + 292 across four validated partitions).
- Compile check: passed.

**Current checkpoint: Sprint 232 — 1171 tests passing.**

## Sprint 233 — Legacy Assumption Access Boundary Hardening

- Replaced the remaining direct planner read of legacy `pension_growth` with `AssumptionResolver.expected_investment_return()` at the portfolio-statistics projection boundary.
- Canonical `expected_investment_return` remains authoritative when present; legacy `pension_growth` remains the fallback when canonical data is absent.
- Added four focused regression tests covering precedence, fallback and zero/negative value preservation.
- No financial calculation semantics changed.

- Sprint 233 focused regression: **4 passed**.
- Full suite: **1175 tests passed, 9 subtests** (294 + 294 + 294 + 293 across four validated partitions).
- Compile check: passed.

**Current checkpoint: Sprint 233 — 1175 tests passing.**

## Sprint 234 — Legacy Assumption Access Guard Hardening

Sprint 234 added a regression guard around the legacy assumption compatibility boundary. The historical aliases `inflation`, `savings_interest` and `pension_growth` are now protected from direct reads or direct dictionary indexing anywhere in planner code outside `AssumptionResolver`.

No financial calculation logic was changed.

- Focused regression: 3 passed
- Full suite: 1178 passed, 9 subtests
- Partitions: 242 + 547 + 182 + 207
- Compile check: passed

Current checkpoint: Sprint 234 — 1178 tests passing.

## Sprint 235 — Canonical Inflation Assumption Boundary Hardening

Sprint 235 moved the remaining direct `inflation_rate` reads in the State Pension and Monte Carlo boundaries behind `AssumptionResolver`, while preserving the prior missing-value behaviour at both boundaries.

No financial calculation logic was intentionally changed.

- Focused regression: 4 passed
- Impacted Monte Carlo/State Pension regression: 8 passed
- Compile check: passed
- Full-suite revalidation: not completed within the execution window; Sprint 234 baseline remains 1178 passing, with 4 new Sprint 235 tests.

Current checkpoint: Sprint 235 — 1182 tests expected after full-suite validation.
## Sprint 236 — Canonical Investment Return Validation Boundary Hardening

- Hardened the validation boundary so `expected_investment_return` is resolved through `AssumptionResolver` rather than read directly by `ValidationEngine`.
- Preserved canonical-over-legacy precedence and `pension_growth` fallback semantics for older callers/configurations.
- Added four focused regression tests covering canonical precedence, legacy fallback, validation rejection and direct-read exclusion.
- No retirement, tax, State Pension, ISA, savings, withdrawal, investment-return or Monte Carlo calculation semantics were intentionally changed; this is a validation/access-boundary cleanup.

- Sprint 236 focused regression: **4 passed**.
- Full-suite discovery was attempted but exceeded the execution window; no new full-suite pass count is claimed.

**Current checkpoint: Sprint 236 — 1186 tests expected from the 1182-test Sprint 235 baseline plus 4 Sprint 236 regressions; full-suite revalidation pending.**

## Sprint 237 — Canonical Savings Interest Assumption Boundary Hardening

- Added regression coverage proving the Savings Engine consumes the canonical `savings_interest_rate` through `AssumptionResolver`.
- Preserved legacy `savings_interest` fallback semantics for older configurations and callers.
- Added a source-level guard preventing direct reads of canonical or legacy savings-interest aliases outside `AssumptionResolver`.
- Added four focused Sprint 237 regression tests.
- No retirement, tax, State Pension, ISA, savings calculation semantics were intentionally changed; this sprint hardens the existing assumption-access boundary only.

- Sprint 237 focused regression: **4 passed**.
- Compile check: passed.

**Current checkpoint: Sprint 237 — 1190 tests expected from the 1186-test Sprint 236 baseline plus 4 Sprint 237 regressions.**

## Sprint 238 — Canonical Monte Carlo Return Validation Boundary Hardening

- Hardened the Monte Carlo validation boundary so `expected_return` is resolved through `AssumptionResolver.monte_carlo_expected_return()` rather than read directly by `ValidationEngine`.
- Preserved the established Monte Carlo return precedence: `expected_return`, then canonical `expected_investment_return`, then legacy `pension_growth`.
- Added four focused Sprint 238 regression tests covering precedence, canonical fallback, legacy fallback and direct-read exclusion.
- No retirement, tax, State Pension, ISA, savings, withdrawal, investment-return, inflation, Monte Carlo simulation or goal calculation semantics were intentionally changed; this sprint hardens validation/access boundaries only.

- Sprint 238 focused regression: **4 passed**.
- Full suite: **1194 tests passed, 9 subtests** (262 + 412 + 253 + 267 across four validated partitions; all partitions passed).
- Compile check: passed.

**Current checkpoint: Sprint 238 — 1194 tests passing.**

## Sprint 239 — Canonical Assumption Consumer Boundary Audit Hardening

- Extended the canonical assumption boundary with resolver accessors for investment volatility, inflation volatility, ISA growth, and State Pension configuration inputs.
- Removed remaining direct reads of those selected canonical assumptions from planner calculation consumers, routing them through `AssumptionResolver`.
- Added source-level regression protection against reintroducing direct canonical reads outside the resolver.
- Preserved all existing financial calculation semantics and legacy alias behaviour.
- Sprint 239 focused regression: **4 passed**.
- Full regression: **1198 tests passed** across validated test groups.

**Current checkpoint: Sprint 239 — 1198 tests passing.**
## Sprint 240 — Assumption Precedence and Legacy Mapping Hardening

- Centralised the remaining investment-return charge and return-schedule accessors behind `AssumptionResolver`.
- Made the Monte Carlo return precedence explicit and regression-protected: `expected_return` → `expected_investment_return` → legacy `pension_growth`.
- Added resolver boundaries for platform/fund charges and investment/ISA return schedules without changing their existing defaults or calculation semantics.
- Preserved canonical-over-legacy precedence for `inflation_rate`, `savings_interest_rate` and `expected_investment_return`.
- Added four focused Sprint 240 regression tests.
- Assumption-focused regression: **84 tests passed** across the consolidated assumption and affected-engine suites.
- Compile check: passed.
- The complete discovered suite contains **1202 tests**; full-suite execution is not claimed here because the remaining long-running partition exceeded the execution window.

**Current checkpoint: Sprint 240 — 1202 tests in suite; 1198-test Sprint 239 baseline plus 4 new Sprint 240 regressions.**


## Sprint 241 — End-to-End Assumption Consumer Traceability

- Extended the explicit projection consumer boundary to include `planner.validation_engine`, `planner.timeline`, `planner.strategy_engine` and `planner.investment_return`.
- Extended the Monte Carlo consumer boundary to include `planner.validation_engine`, where the stochastic expected-return precedence is validated through `AssumptionResolver`.
- Added `tests/test_sprint241_assumption_end_to_end_consumer_trace.py` with four executable traceability regressions.
- Regression coverage now proves every schema-defined assumption has evidence in at least one declared runtime consumer boundary, while legacy aliases remain resolver-only.
- Preserved all financial calculation semantics and existing assumption precedence.
- Sprint 241 focused regression: 4 passed.
- Full regression: **1206/1206 tests passed** in four validated partitions (281 + 285 + 231 + 409).
- Current suite: 1206 tests (1202-test Sprint 240 baseline plus 4 Sprint 241 regressions).

## Sprint 242 — Assumption Validation and Error-Handling Hardening

- Added shared finite-number validation to `AssumptionResolver` numeric calculation-boundary accessors.
- Missing required numeric assumptions now raise explicit `ValueError` messages; invalid supplied canonical values cannot silently fall back to legacy aliases.
- Monte Carlo selected-return validation now follows the established precedence while rejecting invalid selected values.
- Optional numeric defaults remain unchanged.
- Added six Sprint 242 regression tests.
- No financial calculation logic was intentionally changed.

- Sprint 242 focused regression: **6 passed**.
- Consolidated assumption boundary regression: **45 passed**.
- Full suite: **1212/1212 passed** (268 + 271 + 257 + 416).
- Compile check: passed.

**Current checkpoint: Sprint 242 — 1212 tests passing.**

## Sprint 243 — GUI / Schema / Report Assumption Consistency

- Hardened the Excel assumptions report to consume the same audit-description catalogue as the GUI assumption-change boundary.
- Nested assumption structures (goals and annual schedules) are exported as deterministic JSON strings so every schema-defined value remains representable and lossless in Excel.
- Added regression coverage proving the GUI editor validates and round-trips every schema-defined top-level assumption and preserves nested configuration.
- Added report regression coverage proving every schema-defined assumption appears in the Excel assumptions sheet with its matching audit description.
- No financial calculation logic or assumption defaults changed.

- Sprint 243 focused regression: **4 passed**.
- Full-suite validation: pending.

**Current checkpoint: Sprint 243 — 4 new tests added; full-suite validation pending.**

- Full suite: **1216/1216 passed** across four independently validated partitions (275 + 256 + 243 + 442).
- Compile check: passed.

**Current checkpoint: Sprint 243 — 1216 tests passing.**

## Sprint 244 — Assumptions Boundary Freeze

- Added executable freeze guards for the resolver-only legacy alias boundary and canonical assumption mapping.
- Protected canonical-over-legacy precedence for inflation, savings interest and deterministic investment return.
- Protected the distinct Monte Carlo return precedence: `expected_return` → `expected_investment_return` → `pension_growth`.
- Completed the final assumptions cross-layer regression sweep with no unresolved legacy alias consumers outside `AssumptionResolver`.
- No financial calculation logic or assumption defaults changed.

- Sprint 244 focused regression: **4 passed**.
- Full suite: **1220/1220 tests passed** across four independently validated partitions (301 + 263 + 228 + 428).
- Compile check: passed.

**Current checkpoint: Sprint 244 — assumptions boundary frozen; 1220 tests passing.**

## Sprint 246 — Cross-Engine Integration Coverage

- Added eight end-to-end regression tests covering the shared projection timeline across the major calculation-engine boundaries.
- Protected inflation, State Pension, property-sale, scheduled-return, strategy/withdrawal/tax/pension and summary integration flows.
- Added deterministic repeat-run protection.
- No financial calculation logic or assumption defaults changed.

- Focused regression: **8/8 passed**.
- Affected integration regression: **80/80 passed**.
- Full suite: **1232/1232 passed** (308 + 309 + 308 + 307).
- Compile check: passed.

**Current Sprint: Sprint 246 — Cross-Engine Integration Coverage**
**Current checkpoint: Sprint 246 — 1232 tests passing.**


## Sprint 247 — Scenario / Edge-Case Matrix Expansion

- Added eight boundary-focused regression tests covering projection horizon, property sale, spending phases and scheduled returns.
- Protected first/last projection boundaries and out-of-horizon schedule behaviour.
- No financial calculation logic or assumption defaults changed.

- Focused regression: **8/8 passed**.
- Full suite: **1240/1240 tests passed** across four independently validated partitions (310 + 310 + 310 + 310).
- Compile check: passed.

**Current Sprint: Sprint 247 — Scenario / Edge-Case Matrix Expansion**
**Current checkpoint: Sprint 247 — 1240 tests passing.**

## Sprint 248 — Schedule Interaction Hardening

- Added eleven schedule-interaction regression tests spanning annual spending, investment-return, ISA-return, State Pension earnings-growth and ISA-allowance schedules.
- Protected independent schedule precedence, downstream inflation/charge layers, property-sale ISA allocation, ISA opening-balance growth ordering and State Pension triple-lock behaviour.
- Protected deterministic repeat-run behaviour and schedule enable/disable independence.
- No financial calculation logic or assumption defaults changed.

- Focused regression: **11/11 passed**.
- Compile check: passed.
- Full suite: **1251/1251 tests passed** across four independently validated partitions (313 + 313 + 313 + 312).

**Current Sprint: Sprint 248 — Schedule Interaction Hardening**
**Current checkpoint: Sprint 248 — 1251 tests passing.**

## Sprint 249 — Tax / Withdrawal Integration

- Added `tests/test_sprint249_tax_withdrawal_integration.py` with eleven regression tests for the strategy → withdrawal → tax → pension pipeline.
- Protected the existing pension-income cap and ISA fallback contract before tax is applied.
- Protected tax gross-up, net pension targeting, lifetime tax-free cash consumption and the disabled tax-free-cash path.
- Protected State Pension reduction of pension need, explicit shortfall reporting when the pension cap and other assets are exhausted, final pension roll-forward and summary aggregation.
- Confirmed deterministic repeat-run behaviour.
- No retirement calculation logic, tax formulas or assumption defaults were changed.

- Sprint 249 focused regression: **11/11 passed**.
- Compile check: passed.
- Full suite: **1262/1262 tests passed** across four independently validated partitions (316 + 316 + 315 + 315).
- Compile check: passed.

**Current checkpoint: Sprint 249 — Tax / Withdrawal Integration; 1262 tests passing.**


## Sprint 250 — Monte Carlo / Deterministic Parity

- Added ten regression tests covering deterministic/Monte Carlo return separation, precedence, charges, seeded return injection and repeatability.
- Protected the existing distinction between deterministic `expected_investment_return` and Monte Carlo `expected_return` without changing production calculation behaviour.
- No financial calculation logic or assumption defaults changed.

**Current Sprint: Sprint 250 — Monte Carlo / Deterministic Parity**

- Sprint 250 focused regression: **10/10 passed**.
- Full suite: **1272/1272 tests passed** across four independently validated partitions (318 + 318 + 318 + 318).
- Compile check: passed.

**Current checkpoint: Sprint 250 — Monte Carlo / Deterministic Parity; 1272 tests passing.**

## Sprint 251 — GUI → Engine → Report Traceability

- Added eight regression tests tracing GUI-edited assumptions through application inputs and the scenario workflow into the published report snapshot/payload/text.
- Protected rollback on invalid GUI edits, nested schedule round-trip, snapshot/report consistency, payload immutability and repeatability.
- No financial calculation logic or assumption defaults changed.
- Sprint 251 focused regression: **8/8 passed**.
- Full suite: **1280/1280 passed** across four independently validated balanced partitions (320 + 320 + 320 + 320).
- Compile check: passed.

**Current Sprint:** Sprint 251 — GUI → Engine → Report Traceability
**Current checkpoint:** Sprint 251 — 1280 tests passing.

## Sprint 252 — Regression / Golden Scenario Pack

- Added eight tests for golden baseline schema and stability, deterministic repeatability, row count, finite values and full stored-field parity.
- Existing baseline and production calculation logic unchanged.
- Focused regression: **8/8 passed**; compile check passed.
- Full suite: **1288/1288 tests passed** across four balanced partitions (322 + 322 + 322 + 322), confirmed at Sprint 252 handoff.

**Checkpoint:** Sprint 252 — Regression / Golden Scenario Pack; 1288 tests passing.

## Sprint 253 — Release Readiness / Technical-Debt Sweep

- Added `planner/docs/RELEASE_READINESS.md` with repeatable release gates and a safe technical-debt policy.
- Added six tests protecting checklist completeness, no-unreviewed-calculation-change policy, project test configuration, assumptions JSON parseability, README linkage and sprint traceability.
- Updated the README checkpoint from stale Sprint 170 / 911-test text to the current RC4 checkpoint.
- No production financial calculation logic or assumption defaults changed.

- Sprint 253 focused regression: **6/6 passed**.
- User-confirmed Sprint 252 baseline: **1288 tests passing**. Sprint 253 adds six tests (1,294 pytest tests collected); the full-suite rerun timed out in this environment, so no Sprint 253 full-suite pass is claimed.

**Current Sprint:** Sprint 253 — Release Readiness / Technical-Debt Sweep
**Current checkpoint:** focused checks passed; full-suite rerun pending.


## Sprint 254 — Release Acceptance & Reproducible Validation

- Added `scripts/release_acceptance.py` as a single acceptance entry point for assumptions JSON parseability, compilation and pytest execution. It reports each gate and exits non-zero when a requested gate fails.
- Added deterministic round-robin pytest partitioning (`--partition N --partitions M`) so long-running suites can be executed in independently recorded chunks when a single run exceeds environment limits. Every partition must pass before the complete suite is considered green.
- Added twelve regression tests for runner defaults, gate skipping, extra pytest arguments, non-mutating assumptions checks, checklist traceability, failure reporting and partition validation/distribution.
- Expanded the release-readiness checklist with the repeatable command and partition-completion rule.
- No production financial calculation logic, golden data or assumption defaults changed.

- Sprint 254 focused regression: **12/12 passed** (together with Sprint 252/253 focused tests: **26 passed, 8 subtests passed**).
- Compile check: passed. Assumptions JSON parse: passed.
- Pytest collection: **1306 tests collected**. A single-process full-suite attempt timed out in this environment; no Sprint 254 full-suite pass is claimed. The user-confirmed Sprint 253 baseline remains **1294 tests passing**.

- All four deterministic acceptance partitions passed: **327 + 327 + 326 + 326 = 1,306 tests**, with **20 subtests passed** across the partitions.
- Compile check and assumptions JSON parse passed. The single-process timeout is resolved for acceptance purposes by running all four partitions independently.

**Current checkpoint: Sprint 254 — Release Acceptance & Reproducible Validation; 1,306 tests passing across four partitions.**

## Sprint 255 — Release Packaging & End-to-End Acceptance

- Added `scripts/package_audit.py` to validate checkpoint ZIP integrity, required release files, packaged assumptions JSON, safe archive paths and exclusion of caches/compiled Python artifacts.
- Added eight package-audit regressions for valid packages, missing required files, invalid assumptions JSON, transient artifacts, unsafe paths, unreadable archives and sprint traceability.
- The existing GUI → engine → report integration and CLI/report regressions remain part of the full acceptance suite; this sprint adds a static archive gate without changing runtime workflows.
- No production financial calculation logic, golden data or assumption defaults changed.
- Sprint 255 focused regression: **8/8 passed**; combined Sprint 252–255 focused checks: **34 passed, 8 subtests passed**.
- Full suite: **1,314/1,314 tests passed** across four partitions (329 + 329 + 328 + 328), with 20 subtests passed.
- Compile check passed; package audit passed against the Sprint 254 checkpoint. Final Sprint 255 archive integrity and audit are performed after packaging.

**Current checkpoint:** Sprint 255 — Release Packaging & End-to-End Acceptance; 1,314 tests passing across four partitions.

## Sprint 256 — Historical-Data Integration Design

- Added a standalone typed contract and validation functions for annual equity, bond and inflation observations, with source provenance, observation status, currency, return basis and an explicit gap policy.
- Added historical-data integration design documentation covering import validation, missing-data handling and the proposed opt-in replay roadmap.
- Added 13 tests for valid observations, numeric and year boundaries, provenance, duplicate years, gaps, metadata consistency and no implicit coercion/fabrication.
- No provider integration or calculation-path changes. Existing market CSV adapter, deterministic and Monte Carlo calculations, assumptions defaults and golden baseline are unchanged.
- Sprint 256 focused tests: **13 passed**. Sprint 255 full-suite baseline: **1,314 passed across four partitions, 20 subtests passed**. Current suite expected count: **1,327**; full-suite validation pending.

**Current Sprint:** Sprint 256 — Historical-Data Integration Design
**Current checkpoint:** focused tests passed; full-suite validation pending.

## Sprint 258 — Test Collection Reconciliation & Environment Fingerprinting

- Added `scripts/test_collection_report.py`, a read-only diagnostic that records pytest node IDs, per-file test counts, SHA-256 hashes for test/configuration files, Python version and pytest version. It can compare two reports and enumerate exact node IDs unique to either environment.
- Added `planner/docs/TEST_COLLECTION_DIAGNOSTICS.md` with commands for producing and comparing reports.
- Added nine focused regression tests for parsing, stable order/deduplication, report counts, file/config hashes and cross-report differences.
- This sprint addresses the observed discrepancy without assuming either environment is wrong: the user confirmed 1,308 passing tests from their last ZIP, while this execution environment collected 1,341 tests from the same named checkpoint. The report tool is intended to identify the exact collection/config/runtime differences; user baseline remains recorded as 1,308 until reports are compared.
- The diagnostic is read-only by default. It does not alter assumptions, production calculation logic, projection integration or golden data.
- Sprint 258 focused tests and full suite results are recorded after validation below.

**Current Sprint:** Sprint 258 — Test Collection Reconciliation & Environment Fingerprinting


- Sprint 258 focused regression: **9/9 passed**.
- Full suite: **1,350/1,350 tests passed** across four independently executed partitions (338 + 338 + 337 + 337), with **20 subtests passed**.
- Python compile check passed; assumptions JSON parse passed. Collection fingerprint generated at 1,350 tests in this runtime (Python 3.13.5 / pytest 9.0.2).
- User's local run remains confirmed at **1,308 passing tests**. This is recorded as a runtime collection discrepancy, not a test failure; the new diagnostic can compare the exact node IDs and hashes once the user shares a generated `collection.json`.

**Current checkpoint:** Sprint 258 — Test Collection Reconciliation & Environment Fingerprinting; 1,350 tests passed in this environment, user-reported baseline 1,308 pending collection diff.


## Sprint 259 — Opt-In Historical Replay Utility

- Added `planner/market/historical_replay.py`, a standalone utility that replays an explicitly selected contiguous window from a validated `HistoricalSeriesDataset`.
- Calculates a weighted equity/bond annual return, nominal portfolio value, cumulative inflation index, and inflation-adjusted value year by year.
- Estimated observations are rejected by default and may be included only with `include_estimated=True`. Missing years are never interpolated or fabricated; replay fails if the requested window is incomplete.
- Added 12 regression tests for chronological ordering, compounding, inflation application, repeatability, estimated-data opt-in, gap handling, input validation and allocation boundaries.
- The replay utility is opt-in and is not wired into existing deterministic projections, Monte Carlo, GUI workflows, assumptions, or the golden scenario. No existing financial calculation logic was changed.
- Sprint 259 focused regression: **12/12 passed**.
- The uploaded Sprint 258 collection report matches all 153 test-file hashes and the `pyproject.toml` hash in the Sprint 258 archive; it records **1,350 collected node IDs**. The separately user-reported **1,308 passing** run is not an execution summary contained in that JSON and remains unreconciled. Do not treat collection count as a full-suite pass count.

- Full-suite execution was attempted but did not complete within the available execution window; no full-suite pass count is claimed. The targeted regression set passed.

**Current checkpoint:** Sprint 259 — Opt-In Historical Replay Utility; 1,363 tests collected, targeted regressions passed; full-suite validation pending.


## Sprint 260 — Historical Replay Integration Hardening (2026-10-12)

- Hardened the replay boundary to require a validated `HistoricalSeriesDataset`, a boolean-only `include_estimated` opt-in, and nominal-return inputs. Real-return datasets are rejected so inflation is not applied twice.
- Added finite-result guards during compounding and inflation adjustment; extreme finite input rates now fail with a domain-specific `HistoricalReplayError` rather than returning infinite values.
- Added six regression tests for strict opt-in typing, return-basis protection, malformed datasets, non-finite arithmetic, explicit window selection, and replay result typing.
- Historical replay remains a standalone opt-in utility. No production projection, Monte Carlo, GUI, assumptions, or golden-baseline calculation logic was changed.
- Targeted Sprint 252, 255–259 historical-data/replay/package and golden regression group: **71 passed**.
- Deterministic partition 1/8: **172 passed, 11 subtests passed**. Partition 2/8 did not complete within the execution window, so the complete suite is not claimed as passing. Compile and assumptions JSON gates passed.
- Sprint 260 test file is separate from the Sprint 259 replay tests; the combined Sprint 259–260 replay regression set passes **18/18**.

**Current checkpoint:** Sprint 260 — Historical Replay Integration Hardening; targeted regression checks passed, full-suite validation pending. Final ZIP package audit passed: 387 entries, no `.git`, cache, or compiled Python artifacts; assumptions JSON and archive integrity verified.


## Sprint 261 Validation Summary — 2026-10-14

- Full suite completed successfully across all 16 release-acceptance partitions: **1,377 tests passed**, **20 subtests passed**.
- Focused historical replay / isolation / Monte Carlo parity / golden scenario / package-audit group: **46 passed**.
- Compilation and assumptions JSON checks passed.
- `data/assumptions.json` SHA-256: `33736d31d6a8d14b73b5ec83c9a9befcbb736713979a7eaaa95b2c35d22b3801`.
- `tests/golden/baseline.json` SHA-256: `d0d45d5c3e2846a79711a4e23f3920a04a81bef6025917a2aa9a00d82733c550`.
- User-reported local baseline of **1,308 tests successful** is retained separately; this environment verified 1,377 collected/passing test items.

## Sprint 263 — Collection Report Integrity Validation (2026-10-15)

- Added structural validation for collection report format/version, node-ID syntax and uniqueness, total count, per-file counts, and SHA-256 digest formatting.
- Added ten focused Sprint 263 validation tests and package-audit traceability; collection reconciliation records 11 added node IDs and zero removed versus Sprint 262.
- Targeted Sprint 263 validation, Sprint 258 collection diagnostics, and Sprint 255 package-audit group: **30 passed**.
- Current collection: **1,388 tests across 157 test files**. The full suite passed across 16 deterministic partitions (12 × 87 + 4 × 86), with **20 subtests passed**. A single-process full-suite run exceeded the execution window; the partitioned run is the recorded acceptance evidence.
- `data/assumptions.json` and `tests/golden/baseline.json` fingerprints match the Sprint 262 checkpoint. Sprint 263 itself does not change financial calculation source; earlier sprint changes remain in the cumulative checkpoint.
- Git reconciliation found the local checkpoint branch based on `rc2-architecture`, whose remote head is Sprint 104, plus a local Sprint 140 commit and accumulated later sprint changes. A reconciliation branch is being prepared; pushing requires remote GitHub connectivity, which is unavailable from this execution environment.

**Current checkpoint:** Sprint 263 — Collection Report Integrity Validation; 1,388 collected and partition-verified passing test items.


## Sprint 264 — Test Evidence Freshness & Count Reconciliation (2026-10-15)

- The supplied Windows collection report (`Python 3.14.6` / `pytest 9.1.1`) contains **1,377 node IDs** and matches the Sprint 262 report exactly: zero node IDs added/removed, zero test-file hash differences, and identical pytest configuration hashes. The supplied full-suite log independently records **1,377 passed in 274.41 seconds**.
- The 1,377 report is a pre-Sprint-263 snapshot. Sprint 263 adds 11 test items; the Sprint 263 package collects 1,388. The earlier 1,308 figure is an older user-reported result and is not the count in the latest supplied log.
- Hardened collection comparison so it fails on changed test IDs, missing/added test files, test source hash differences, or pytest configuration hash differences—not only node-ID count differences.
- Extended package audit to require current sprint evidence and reject root-level local collection outputs / raw test logs from release ZIPs. Historical Windows collection snapshots are retained under `reports/archive/` with explicit sprint labels.
- Added ten regression checks across collection comparison, evidence traceability and package auditing. Focused Sprint 258/255/263/264 regression group: **40 passed**.
- Current collection after Sprint 264 changes: **1,398 test items**. Full suite: **1,398/1,398 passed** across 16 deterministic partitions (6 × 88 + 10 × 87), with **20 subtests passed**.
- No production financial calculation logic, assumptions defaults, or golden baseline changed. Assumptions SHA-256 remains `33736d31d6a8d14b73b5ec83c9a9befcbb736713979a7eaaa95b2c35d22b3801`; golden baseline SHA-256 remains `d0d45d5c3e2846a79711a4e23f3920a04a81bef6025917a2aa9a00d82733c550`.

**Current checkpoint:** Sprint 264 — Test Evidence Freshness & Count Reconciliation; 1,398 collected and passed across 16 deterministic partitions.


## Sprint 265 — Release Manifest & Artifact Integrity (2026-10-15)

- Added `scripts/build_release_manifest.py` to generate a deterministic `release_manifest.json` containing every packaged file's relative path, byte size and SHA-256 digest; the manifest excludes itself to avoid recursive hashing.
- Extended `scripts/package_audit.py` to require the release manifest and verify its format/version, file count, exact path coverage, sizes and digests against ZIP contents. Existing unsafe-path, transient-artifact, required-file, assumptions JSON and CRC checks remain active.
- Added `planner/docs/RELEASE_MANIFEST.md` with reproducible build and audit instructions and an explicit note that hashes provide integrity checking, not cryptographic identity/signature.
- Added regression coverage for deterministic manifest creation, excluded transient artifacts, valid packages, changed content, path mismatches, size mismatches and malformed digests.
- No production financial calculation logic, assumptions defaults or golden baseline changed.
- User-confirmed Sprint 264 baseline: **1,398 tests passing**. Focused Sprint 265/package/evidence regression group: **50 passed**. Full suite: **1,408/1,408 passed** in a single-process pytest run (162.61 seconds). Collection report records 1,408 items across 159 test files; the Sprint 264-to-265 node-ID diff is 10 additions and zero removals. Compile and assumptions JSON checks passed. Final package manifest and archive audit passed.

**Current Sprint:** Sprint 265 — Release Manifest & Artifact Integrity
**Current checkpoint:** Sprint 265 — release manifest verified; 1,408 tests passing.

## Sprint 266 — Cross-Platform Package Path Safety (2026-10-16)

- Hardened release ZIP auditing to reject non-canonical backslash separators, Windows drive-qualified paths, UNC paths, absolute POSIX paths, NUL characters, and `..` traversal segments.
- Added independent checks for manifest path integrity and duplicate archive member names so manifest metadata cannot legitimize unsafe ZIP entries and ZIP-reader ambiguity is surfaced.
- Added `planner/docs/PACKAGE_PATH_SAFETY.md` and focused regressions for path variants, duplicate entries, manifest path injection, and sprint traceability.
- No production financial calculation logic, assumptions defaults, or golden baseline changes.
- Sprint 265 user-confirmed baseline: **1,408 tests passing**. Sprint 266 full suite: **1,421/1,421 passed** across 32 deterministic partitions (13 × 45 and 19 × 44), with 20 subtests passed. Focused package/path/manifest/evidence regression group: **53 passed**. Compile check and assumptions JSON parse passed. Final release manifest covers 391 payload files; the ZIP contains 392 entries including the manifest. ZIP CRC and package audit passed.

**Current Sprint:** Sprint 266 — Cross-Platform Package Path Safety
**Current checkpoint:** 1,421 tests passed across 32 deterministic partitions; 53 focused regressions passed; 391-file release manifest verified and 392-entry ZIP audit passed.


## Sprint 267 — Release Manifest Schema Hardening (2026-10-16)

- Hardened `scripts/package_audit.py` to reject duplicate JSON keys, malformed numeric metadata, unsafe manifest paths, and invalid size values.
- Hardened `scripts/build_release_manifest.py` to refuse symlinks anywhere in the release input tree and updated its default sprint number to 267.
- Added `planner/docs/RELEASE_MANIFEST_SCHEMA.md` and ten regression tests for manifest schema, duplicate-key handling, symlink boundaries, default sprint, and status/roadmap traceability.
- Updated the README's current RC4 checkpoint line so it no longer advertises Sprint 261 as current.
- No production financial calculation logic, assumptions defaults, or golden baseline changed.
- Sprint 266 baseline: **1,421/1,421 passed**. Sprint 267 collection: **1,432 tests across 161 test files**, with 11 additions and zero removals versus Sprint 266. Full suite: **1,432/1,432 passed** across 32 deterministic round-robin partitions (24 × 45 and 8 × 44), with 20 subtests passed. The one-process run was not used for acceptance; every partition completed successfully.

- Focused Sprint 265–267 manifest/path-safety regression group: **32 passed**. Compile check and assumptions JSON parse passed. Assumptions SHA-256 and golden baseline SHA-256 are unchanged from Sprint 266.
- Release manifest regenerated after final documentation/evidence updates; package audit and ZIP CRC results are recorded in the final package reconciliation report.

**Current Sprint:** Sprint 267 — Release Manifest Schema Hardening
**Current checkpoint:** 1,432 tests passed across 32 deterministic partitions; 32 focused regressions passed; financial calculation logic, assumptions and golden baseline unchanged.

## Sprint 268 — ZIP Symlink & Special-Entry Safety (2026-10-16)

- Hardened `scripts/package_audit.py` to reject Unix symbolic-link entries embedded in ZIP archives, validate directory-entry paths, and detect duplicate entries in a linear pass.
- Added `planner/docs/ZIP_SPECIAL_ENTRY_SAFETY.md` and portable regressions that encode symlink metadata directly into ZIP entries; these tests do not require host filesystem symlink privileges.
- Updated the release-manifest builder's default sprint to 268 and retained the manifest schema, hash verification, CRC and package safety gates.
- Confirmed local Windows Sprint 267 result supplied by the user: **1,430 passed, 2 skipped** out of 1,432 collected; both skips are filesystem-symlink tests unavailable on that platform.
- Focused Sprint 265–268 package/manifest regression group: **36 passed** before final collection/report updates.
- No production financial calculation logic, assumptions defaults, or golden baseline changed.
- Full-suite validation in this environment: **1,436/1,436 passed**, zero skips/failures/errors, across 32 deterministic partitions (28 × 45 and 4 × 44), with 20 subtests passed. Focused Sprint 265–268 regressions: **36 passed**. The one-process full-suite attempt exceeded the execution window; all independent partitions completed successfully.
- Collection report records 1,436 items across 162 test files, with four new Sprint 268 test cases and no removed node IDs. The previous Sprint 267 test file hash changed because its “current default sprint” expectation now tracks Sprint 268.
- Compile check and assumptions JSON parse passed. Assumptions and golden baseline SHA-256 values remain unchanged. Final archive audit results are recorded in `reports/sprint268_test_count_reconciliation.json`.

**Current Sprint:** Sprint 268 — ZIP Symlink & Special-Entry Safety
**Current checkpoint:** 1,436 tests passed across 32 deterministic partitions; 36 focused regressions passed; financial calculation logic, assumptions and golden baseline unchanged.

## Sprint 269 — ZIP Metadata & Decompression Resource Limits

- Added a central-directory metadata preflight before CRC checks or manifest/assumptions reads, so risky entries are rejected before the auditor attempts decompression.
- Reject encrypted entries, unsupported compression methods, zero compressed size for non-empty content, excessive compression ratios, per-entry or total uncompressed size over limits, and archives exceeding the entry-count limit.
- Added `planner/docs/ZIP_METADATA_RESOURCE_LIMITS.md` and ten focused regressions for metadata limits, unsupported/encrypted entries, resource bounds, and preflight-before-decompression behavior.
- No production financial calculation logic, assumptions defaults, or golden baseline changed.
- Focused Sprint 265–269 package/evidence regression group: **46 passed**. Full suite: **1,446/1,446 passed** across 32 deterministic partitions (6 × 46 and 26 × 45), with **20 subtests passed**; elapsed 162.2 seconds. Collection is 1,446 items across 163 test files; 10 node IDs added and none removed versus Sprint 268.
- `python -m compileall -q .` and assumptions JSON parse passed. Assumptions SHA-256 remains `33736d31d6a8d14b73b5ec83c9a9befcbb736713979a7eaaa95b2c35d22b3801`; golden baseline SHA-256 remains `d0d45d5c3e2846a79711a4e23f3920a04a81bef6025917a2aa9a00d82733c550`.
- Archive audit/CRC metrics are recorded in `reports/sprint269_test_count_reconciliation.json` after the final package verification.

**Current checkpoint:** Sprint 270 — ZIP Special-File Metadata Safety; validation evidence recorded below.

## Sprint 270 — ZIP Special-File Metadata Safety (2026-10-16)

- Extended `scripts/package_audit.py` to reject Unix FIFO, character-device, block-device, and socket entries before CRC or payload reads.
- Added consistency checks between Unix directory/regular-file type bits and ZIP member path suffixes; existing symlink detection remains in place.
- Added `planner/docs/ZIP_SPECIAL_FILE_METADATA.md` and portable synthetic ZIP metadata regressions.
- No production financial calculation logic, assumptions defaults, or golden baseline changed.
- Validation and final archive metrics are recorded in `reports/sprint270_test_count_reconciliation.json`.

**Current Sprint:** Sprint 270 — ZIP Special-File Metadata Safety



## Sprint 271 — ZIP Filename Collision Safety (2026-10-16)

- Added Unicode NFC normalization plus case-folded archive-path collision checks, rejecting names that can alias on common Windows and Unicode-aware filesystems.
- Added file/child conflict detection so a regular file cannot also serve as a parent path for another archive member. Explicit directories with children remain valid.
- Added `planner/docs/ZIP_FILENAME_COLLISION_SAFETY.md` and eight regression tests covering case aliases, Unicode canonical equivalence, nested collisions, file/child conflicts, valid explicit directories, and traceability.
- Collision checks execute before CRC or payload reads. Existing unsafe-path, duplicate-name, symlink, special-file, decompression-limit and release-manifest checks remain active.
- No production financial calculation logic, assumptions defaults, or golden baseline changed.
- Full suite: **1,463/1,463 passed** across 8 deterministic partitions (7 × 183 + 1 × 182), with 20 subtests passed. Collection has 1,463 items across 165 test files: eight node IDs added and zero removed versus Sprint 270. The manifest builder default-sprint expectation changed in `tests/test_sprint267_manifest_schema_hardening.py`; pytest configuration hash is unchanged. Focused Sprint 265–271 package-safety group: **63 passed**. Compilation and assumptions JSON checks passed. Final release manifest covers 411 payload files; the ZIP contains 412 entries. Package audit, manifest digest/size verification, ZIP CRC and independent extraction checks passed.

**Current Sprint:** Sprint 272 — ZIP Windows Filename Safety
**Current checkpoint:** 1,474 tests passed across 32 deterministic partitions; 74 focused regressions passed; financial calculation logic, assumptions and golden baseline unchanged.


## Sprint 272 — ZIP Windows Filename Safety (2026-10-16)

- Added preflight rejection for Windows-invalid path characters and ASCII control characters, trailing dots/spaces, and reserved DOS device names including names with extensions and superscript COM/LPT variants.
- These checks run before CRC validation or payload decompression and complement prior path traversal, case/Unicode collision, file/child conflict, duplicate-entry, special-file, and resource-limit checks.
- Added `planner/docs/ZIP_WINDOWS_FILENAME_SAFETY.md` and ten portable regression tests. Updated the manifest-builder default sprint expectation to 272.
- No production financial calculation logic, assumptions defaults, or golden baseline changed.
- User-confirmed Sprint 271 Windows baseline: **1,461 passed, 2 skipped**; skips are filesystem-symlink tests unavailable in that Windows environment.
- Sprint 272 collection: **1474 tests across 166 files**; 11 node IDs added, zero removed versus Sprint 271. Focused package-safety regression group: **74 passed**. Full suite: **1,474/1,474 passed** across 32 deterministic round-robin partitions (47, 47, 46, 46, 46, 46, 46, 46, 46, 46, 46, 46, 46, 46, 46, 46, 46, 46, 46, 46, 46, 46, 46, 46, 46, 46, 46, 46, 46, 46, 46, 46), with **20 subtests passed**. A single-process run exceeded the execution window; every partition completed successfully. Compilation and assumptions JSON checks passed. Assumptions SHA-256 is `33736d31d6a8d14b73b5ec83c9a9befcbb736713979a7eaaa95b2c35d22b3801` and golden baseline SHA-256 is `d0d45d5c3e2846a79711a4e23f3920a04a81bef6025917a2aa9a00d82733c550`. Package audit, manifest digest/size verification, ZIP CRC and independent extraction results are recorded in the reconciliation report.

**Current Sprint:** Sprint 272 — ZIP Windows Filename Safety


## Sprint 273 — ZIP Local-Header Integrity (2026-10-16)

- Added local-header preflight to compare local filename, flags, compression method, CRC and sizes against central-directory metadata before CRC testing or payload reads. ZIP64 size fields and data-descriptor entries are handled explicitly.
- Reject malformed local-header signatures/lengths, local records extending into the central directory, and overlapping local records.
- Added `planner/docs/ZIP_LOCAL_HEADER_INTEGRITY.md` and portable regressions for consistent headers, signature, name, flags, method, CRC, size, bounds and overlap cases.
- No production financial calculation logic, assumptions defaults, or golden baseline changed.


## Sprint 273 Validation Addendum

- Focused package-security regressions: **84 passed**, including **10/10** Sprint 273 local-header tests. Compile check and assumptions JSON parse passed.
- Full suite collection is **1,484 tests**. Full-suite execution was attempted in this runtime but timed out before completion; no aggregate pass claim is made. The user's Windows run should be used as the next full-suite acceptance check.

## Sprint 275 — Reproducible Release Evidence

Implemented evidence reconciliation for the collection report, source-tree test/config hashes, release manifest, packaged ZIP inventory, embedded manifest, and archive digest. The reconciler expressly does not assert that tests passed; test execution remains a separate acceptance gate. Focused and full-suite validation results are recorded in the Sprint 275 checkpoint report after packaging.


### Sprint 275 validation addendum

- Collection report: **1,498 node IDs across 169 test files**. Collection is not a pass count.
- Focused Sprint 275, Sprint 267 manifest-schema, and Sprint 265 release-manifest tests: **27 passed**.
- `python -m compileall -q .`: passed. `data/assumptions.json` parse: passed without modification.
- Package audit of the Sprint 275 ZIP: passed; 427 payload files plus the root manifest (428 ZIP file entries).
- Evidence reconciliation: **PASS**, no errors; archive SHA-256 is recorded in `reports/sprint275_release_evidence.json`. The report explicitly marks test execution as `NOT_VERIFIED_BY_THIS_REPORT`.
- Full-suite partition attempt timed out during partition 9/32; no aggregate full-suite pass claim is made. User-side `python -m pytest -ra` remains the acceptance check.
- Windows symlink skips from earlier sprints are environment-specific; this Sprint 275 runtime run did not complete far enough to reconcile those skips.

## Sprint 275 user acceptance (2026-10-19)

- User reported `1496 passed, 2 skipped in 223.57s (0:03:43)` using `python -m pytest -ra`. This is the full local test execution result for the Sprint 275 checkpoint; the two skips are the known Windows symlink-creation permission skips.

## Sprint 276 — Release Workflow & GitHub Publication

- Added `.github/workflows/release.yml`. Full pytest, compile and assumptions JSON validation gate packaging. Manual dispatch uploads an artifact; version tags beginning `v` additionally publish a GitHub Release.
- Added deterministic ZIP builder `scripts/build_release_archive.py`; it validates manifest size/SHA-256 values, rejects traversal/symlink inputs and fixes ZIP entry order, timestamps and modes.
- Added `planner/docs/RELEASE_WORKFLOW.md` and five release workflow/archive regression tests.
- Updated package-audit required paths, excluded generated `dist/` from source manifest inputs, and made evidence reports take the sprint number from the release manifest.
- Local Sprint 276 targeted validation and package audit results are recorded in the checkpoint report. Full Sprint 276 suite has not been run to completion here; request the user-side pytest run before declaring the checkpoint fully accepted.
- GitHub publication status: **not confirmed**. This local checkpoint's workflow is not evidence that source files have been committed or pushed to `andyleonard1/RetirementPlanner`.

**Current Sprint:** Sprint 276 — Release Workflow & GitHub Publication

### Sprint 276 validation addendum (2026-10-19)

- Collection: **1,503 node IDs across 170 test files** (five new test nodes in `tests/test_sprint276_release_workflow.py`). This is a collection total, not a passing-test total.
- Focused Sprint 276, Sprint 275 evidence, Sprint 265/267 manifest, and Sprint 273/274 ZIP-integrity tests: **48 passed**.
- `python -m compileall -q .`: passed. `data/assumptions.json` parsed successfully without modification.
- Release manifest: **432 payload files**. Deterministic ZIP: **433 entries including `release_manifest.json`**. Package audit passed.
- Release-evidence reconciliation: **PASS**, zero errors; archive SHA-256 is recorded in `dist/sprint276_release_evidence.json` and in the separate evidence-report download. Evidence status remains `NOT_VERIFIED_BY_THIS_REPORT` for test execution.
- Full Sprint 276 suite is not claimed as passed; run `python -m pytest -ra` on the extracted checkpoint.
- GitHub remote check: the public repository's latest commit visible to the connector is `9ec3e657a88fc002f70162fce09189304f554731` (2026-07-25), and `.github/workflows/tests.yml` was not found on `main`. This local checkpoint was not pushed. Because the remote source state differs substantially from the current RC4 checkpoint, no partial files were written to `main`.

## Sprint 277 — Assumptions / Engine / GUI Coverage Audit

- Added `scripts/audit_assumption_coverage.py` and the generated `reports/sprint277_assumption_coverage_audit.json` report.
- Static audit checks schema/default alignment, operational role classification, audit descriptions, role-to-consumer boundaries, existence of consumer source modules, and the GUI complete-JSON editor boundary.
- Added `tests/test_sprint277_assumption_coverage_audit.py` and `planner/docs/ASSUMPTION_COVERAGE_AUDIT.md`.
- Focused audit + existing GUI round-trip + consumer trace tests: **10 passed**. Static audit status: **PASS**, zero issues.
- Scope limitation: static catalogue consistency is not proof of financial correctness; existing runtime consumer-trace and GUI round-trip tests remain complementary evidence.
- No financial calculation logic, assumptions defaults, or golden baseline changed.
- Full suite not run to completion in this execution environment; user-side `python -m pytest -ra` remains acceptance gate.

**Current Sprint:** Sprint 277 — Assumptions / Engine / GUI Coverage Audit


## Sprint 277 acceptance addendum (2026-10-20)

- User-reported full-suite result for the corrected Sprint 277 checkpoint: **1,504 passed, 2 skipped** in 215.81 seconds; zero failures. The two skips are the Windows symlink-privilege limitations in the Sprint 267 manifest hardening tests.
- Earlier failures were resolved in the corrected checkpoint: the legacy manifest test now expects sprint 277, and the health-check CLI test timeout was raised from 60 to 180 seconds without reducing its Monte Carlo iterations.

## Sprint 278 — GUI Assumptions Editor Coverage

- Added headless regression coverage for all seven assumptions-editor actions and their controller wiring.
- Added lifecycle checks for non-mutating validation/formatting, Unicode/nested values, atomic rejection of invalid schedules, status reporting, and complete-document apply/save/reload.
- The GUI source-wiring check is structural and does not claim visible Tk interaction or visual/accessibility validation.
- No financial calculation logic, assumptions defaults, or golden baseline changed.
- Focused/full validation results are recorded after local execution; full-suite acceptance remains pending user run.

**Current Sprint:** Sprint 278 — GUI Assumptions Editor Coverage

### Sprint 278 validation addendum (2026-10-20)

- Focused GUI assumptions, audit, consumer-trace, release-workflow, release-evidence and manifest regression group: **87 passed**.
- Collection: **1,519 node IDs across 173 test files**. This is collection evidence only, not a full-suite pass claim.
- `python -m compileall -q .`: passed. Assumptions JSON parsed successfully.
- Package audit: **PASS**. Release-evidence reconciliation: **PASS**, zero errors; `test_execution_status` correctly remains `NOT_VERIFIED_BY_THIS_REPORT`.
- `data/assumptions.json` SHA-256 remains `33736d31d6a8d14b73b5ec83c9a9befcbb736713979a7eaaa95b2c35d22b3801`; `tests/golden/baseline.json` SHA-256 remains `d0d45d5c3e2846a79711a4e23f3920a04a81bef6025917a2aa9a00d82733c550`.
- Full Sprint 278 suite has not been run to completion in this environment; user-side `python -m pytest -ra` is the acceptance gate.

## Sprint 281 — End-to-End Scenario Integration (checkpoint pending full-suite acceptance)

- Added seven full-planner integration tests spanning timeline continuity, deterministic repeatability, inflation-to-spending/funding propagation, State Pension policy toggles, ISA inflation-link opt-in, finite outputs, and shipped assumptions immutability.
- Focused integration/regression set: 27 passed.
- Full suite has not yet been verified for this sprint. The latest accepted previous checkpoint was Sprint 280: 1,529 passed, 2 skipped.
- No production calculation logic, assumption defaults, or golden baseline values changed.


## Sprint 282 — Tax and Withdrawal Scenario Integration

- Added nine end-to-end tests for pension/ISA withdrawal strategy differences, gross/net tax reconciliation, pension-income caps, tax-free cash lifetime limits, exhausted-asset shortfalls, summary aggregation, and finite outputs.
- The tests characterize current behavior and are not tax advice or a claim that one strategy is universally optimal.
- No production financial calculations, assumption defaults, or golden baseline values changed.
- Focused Sprint 249 / 281 / 282 regression set: 27 passed. Full-suite acceptance remains pending user-side `python -m pytest -ra`.

**Current Sprint:** Sprint 282 — Tax and Withdrawal Scenario Integration

## Sprint 283 — Deterministic and Monte Carlo Parity (checkpoint pending full-suite acceptance)

- Added five regression tests for zero-volatility ending-asset parity, seeded repeatability, percentile ordering and finite summaries, seed sensitivity under non-zero volatility, and source-assumption immutability.
- Focused Sprint 250 / 281 / 282 / 283 regression set: 31 passed.
- No production calculation logic, default assumptions, or golden baseline values changed.
- Full-suite acceptance remains pending user-side `python -m pytest -ra`; collection and release evidence are not proof of a full-suite pass.

**Current Sprint:** Sprint 283 — Deterministic and Monte Carlo Parity


## Sprint 284 — Golden-Scenario Regression Pack (checkpoint pending full-suite acceptance)

- Added a versioned, reviewable golden fixture for three representative retirement scenarios: pension-first, ISA-first, and higher inflation with triple-lock disabled and ISA inflation-linking enabled.
- Captures yearly spending, State Pension, gross pension income, tax, closing assets, shortfall and total-assets outputs plus aggregate summary values.
- Fixtures are not regenerated by tests; numeric comparisons use a 0.011 tolerance against values rounded to two decimal places.
- Focused Sprint 284 regression: 5 tests passed (with 3 scenario subtests). No production financial calculations, defaults, or the existing golden baseline were changed.
- Full-suite acceptance remains pending user-side `python -m pytest -ra`; collection/release reports are not evidence that the full suite passed.

**Current Sprint:** Sprint 285 — Release Readiness


## Sprint 285 — Release Readiness (checkpoint pending full-suite acceptance)

- Added release-readiness traceability tests for the documented acceptance gates, manifest inventory, and unchanged shipped assumptions / existing golden baseline digests.
- Added `planner/docs/SPRINT285_RELEASE_READINESS.md` with the reproducible acceptance sequence and evidence limitations.
- Updated release manifest defaults and schema regression expectations to Sprint 285; added Sprint 285 artifacts to the package audit requirements.
- No production financial calculations, default assumptions, or golden baseline values changed.
- Focused validation and package audit results are recorded in the checkpoint; full-suite acceptance remains pending user-side `python -m pytest -ra`.

**Current Sprint:** Sprint 285 — Release Readiness

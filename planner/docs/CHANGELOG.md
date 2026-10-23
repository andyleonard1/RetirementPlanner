
## Sprint 170

- Expanded public CLI integration coverage for `compare.py`.
- Verified both canonical withdrawal strategies and comparison-report columns end to end.
- Added two regression tests; full suite reaches 911 passing tests.

# Changelog

## v0.5.0

- Modular engine architecture
- UK tax calculations
- ISA modelling
- Savings modelling
- State Pension modelling
- Strategy Engine
- Excel reporting
- Excel charts

## v0.6.0 (planned)

- Iterative tax solver
- Inflation modelling
- Dynamic tax thresholds
- Variable investment returns

Version 1.0.0-beta1
-------------------

Added
• Recommendation Engine
• Risk Engine
• Professional PDF report

Improved
• Strategy comparison
• Reporting architecture

Fixed
• Strategy Engine withdrawal logic
• Unit tests
## 2.0 RC2 architecture work

### Added
- Structural engine contracts using Python `Protocol`.
- Typed result-object boundaries.
- Architecture and engine documentation.
- Consolidated release and coding standards documentation.

### Improved
- Recommendation/report migration.
- Optimisation framework reuse.
- Logging consistency.
- Documentation now reflects the current engine-driven architecture.

## RC4 Sprint 62 — Sequence-of-Returns Risk

### Added
- `planner/simulation/sequence_risk.py` for isolated sequence-of-returns comparisons.
- Regression coverage for return-order effects, withdrawals, validation and depletion.

### Design
- The deterministic retirement model remains the reference calculation.
- Sequence-risk analysis is an independent RC4 layer and does not alter live retirement recommendations.

## RC4 Sprint 169 — Documentation & Architecture Contract Consolidation

### Added
- Practical developer architecture guide covering layer ownership, stable contracts, GUI boundaries, testing discipline and checkpoint practice.

### Improved
- README now links the developer architecture guide and reflects the current 909-test checkpoint.

### Compatibility
- No runtime behaviour or financial calculation logic changed.

### Sprint 172 — GUI Assumptions Change Tracking & Safe Discard

- Added deterministic assumption-change path reporting to the GUI controller.
- Added atomic discard of in-memory assumption edits back to the last validated persisted baseline.
- Extended the advanced assumptions editor with visible change tracking and an explicit Discard changes action.
- Preserved explicit Save semantics and the engine-driven calculation boundary.
- Added four regression tests covering nested change paths, discard restoration, atomic discard failure and post-save clean state.


### Sprint 173 — GUI Assumptions Editor Validation & Formatting Workflow
- Added non-mutating validation and canonical formatting for the complete assumptions JSON editor.
- Added Validate and Format GUI actions.
- Added regression coverage for immutability and invalid-document handling.
- No financial calculation logic changed.

## Sprint 182 — GUI Projection Result Snapshot Integrity

- Added an immutable, recursively frozen projection report snapshot at the view-model/presentation boundary.
- GUI report payload/text consumers now reuse the same published snapshot for a current projection, preventing repeated export/report calls from rebuilding divergent presentation data.
- A successful projection run or saved-assumption reload publishes a fresh snapshot; stale-result guards remain in force.
- Added three regression tests covering snapshot reuse, nested immutability and replacement after a new projection.
- No retirement, tax, State Pension, ISA, savings, withdrawal or projection calculation engine logic changed.
- Full suite: **954 tests passing** (9 subtests).

## Sprint 184 — GUI Projection Result Snapshot Consumer Contract Consolidation

- Added a public `current_result_snapshot()` accessor so GUI, report and export consumers share the exact immutable current-result snapshot.
- Kept payload/text helpers as compatibility facades over that shared snapshot; stale and closed-window guards remain enforced at the single boundary.
- Added regression coverage proving shared snapshot identity and early stale-result rejection for consumer access.
- No retirement, tax, State Pension, ISA, savings, withdrawal or projection calculation engine logic changed.
- Full suite: **958 tests passing** (9 subtests).

## Sprint 186 — GUI Projection Result Snapshot File Export Integration

- Added calculation-free JSON and text export methods for the current GUI projection result snapshot.
- Exports use the same authoritative immutable snapshot already consumed by GUI/report consumers; no projection is rebuilt for export.
- Export writes are staged through a temporary file and atomically replaced to avoid partial destination files.
- Stale and closed presentations remain blocked by the existing shared result-consumer boundary.
- Added three regression tests covering JSON parity, text parity and stale-result rejection.
- No retirement, tax, State Pension, ISA, savings, withdrawal or projection calculation engine logic changed.
- Full suite: **965 tests passing** (9 subtests).

## Sprint 187 — GUI Projection Result Snapshot Export Atomicity Hardening

- Consolidated JSON and text result exports onto a shared atomic text-write helper.
- Temporary export files now use unique names in the destination directory, avoiding collisions between concurrent/repeated exports.
- Failed publication now cleans up the temporary file and preserves any existing destination file unchanged.
- Added two regression tests covering safe overwrite and failed-publish cleanup.
- No retirement, tax, State Pension, ISA, savings, withdrawal or projection calculation engine logic changed.
- Full suite: **967 tests passing** (9 subtests).

- Sprint 211: activated the live inflation calculation boundary and wired compounded `inflation_rate` factors into the planner timeline; refreshed the golden projection baseline and related report-pagination regression coverage.

- Sprint 215: wired inflation and earnings forecasts into the State Pension triple-lock calculation and ensured the resulting State Pension values feed the existing required-pension-income calculation; added six regression tests and refreshed the golden projection baseline.

### Sprint 216 — Monte Carlo Inflation Volatility Wiring

- Activated `inflation_volatility` for annual scenario-specific Monte Carlo inflation paths.
- Propagated simulated CPI through inflation factors, inflation-linked spending/tax/ISA calculations and State Pension triple-lock growth.
- Preserved deterministic projection behaviour and seeded investment-return draw compatibility.
- Added 6 regression tests.


## Sprint 217 — Annual State Pension Earnings Forecast Schedule

- Added an opt-in `state_pension_earnings_growth_schedule` keyed by calendar year.
- Added `state_pension_earnings_growth_schedule_enabled`, defaulting to disabled so the existing forecast remains unchanged.
- Scheduled earnings growth now feeds the existing triple-lock calculation while CPI and the 2.5% floor remain authoritative competing inputs.
- Missing scheduled years fall back to the configured base `state_pension_earnings_growth`.
- Added structural validation and audit descriptions for the new schedule settings.
- Added six regression tests covering schedule activation, year-by-year progression, CPI precedence, fallback, disabled compatibility and spouse progression.
- Preserved all other financial calculation and reporting logic.
- Full suite: **1090 tests passed, 9 subtests**.
- Compile check: passed.

## Sprint 218 — Annual Spending Schedule Boundary

- Added an opt-in `annual_spending_schedule` keyed by calendar year.
- Added `annual_spending_schedule_enabled`, defaulting to disabled so the existing age-based spending phases remain unchanged by default.
- Matching annual entries override the phase amount for that year; missing years fall back to the existing phase amount.
- Kept inflation linkage separate so the configured `inflation_link_spending` behaviour continues to apply the compounded inflation factor after annual schedule selection.
- Added structural validation and audit-catalog descriptions for the new schedule settings.
- Added six regression tests.
- Preserved all other financial calculation and reporting logic.
- Full suite: **1096 tests passed, 9 subtests**.

## Sprint 219 — Annual Investment and ISA Return Schedules

- Added opt-in calendar-year investment return schedules.
- Added opt-in calendar-year ISA return schedules.
- Added schema validation and audit metadata for both schedule boundaries.
- Preserved base-return fallback and existing investment charge calculations.
- Added eight regression tests.
- Full suite: 1104 tests passed, 9 subtests.

## Sprint 220 — Assumption Consolidation and Legacy-Field Boundaries

- Added a canonical assumption resolver for duplicate legacy/current configuration fields.
- Added explicit compatibility fallback boundaries for inflation, savings interest and deterministic investment return assumptions.
- Preserved separate Monte Carlo `expected_return` semantics and legacy `pension_growth` compatibility.
- Routed live calculation consumers through the resolver without changing default outputs.
- Added eight regression tests.
- Full suite: **1112 tests passed, 9 subtests**.

## Sprint 221 — Enhanced Goals and Constraints Framework

- Added optional goal enable/disable and comparison-operator controls.
- Preserved legacy goal semantics when the new fields are omitted.
- Added schema/audit coverage and regression tests.

## Sprint 222 — Goal Constraint Report Integration

- Extended the professional Goals PDF to present each evaluated goal's comparison operator.
- Preserved compatibility with legacy goal-result mappings that predate the operator metadata.
- Kept report rendering calculation-free and non-mutating.
- Added four regression tests covering operator presentation, legacy compatibility, non-recalculation and empty goal results.
- Sprint 222 focused regression: **4 passed**.
- Full suite: **1124 tests passed, 9 subtests**.
- Compile check: passed.


## Sprint 223 — Goal Constraint Console Integration

- Extended the console Goals report to present goal comparison constraints.
- Preserved compatibility with legacy goal results without operator metadata.
- Added three regression tests.


## Sprint 224 — Goal Constraint Excel Integration

- Added optional goal-result export to the Excel report through a dedicated Goals worksheet.
- Added presentation of effective goal comparison constraints with legacy-result compatibility.
- Kept the renderer calculation-free and non-mutating; existing Excel output is unchanged when goals are omitted.
- Added five regression tests.
- Full suite: **1132 tests passed, 9 subtests**.

## Sprint 225 — Goal Constraint Audit Coverage Hardening

- Hardened audit-catalog path recognition for the enhanced goal `enabled` and `operator` fields.
- Preserved explicit descriptions for existing goal target/name/type paths and generic handling for unknown nested goal fields.
- Added four regression tests.
- No financial calculation logic changed.
- Full suite: **1136 tests passed, 9 subtests**.


## Sprint 226 — Goal Constraint Target Semantics Hardening

- Goal types that accept targets now consistently use explicitly configured targets.
- Preserved legacy target defaults for retirement age, pension-positive and spending goals when no target is supplied.
- Added five regression tests covering explicit target handling and compatibility defaults.

## Sprint 227 — Goal Constraint Evaluation Boundary Hardening

- Hardened `GoalEngine` direct-call validation for required and optional goal targets.
- Added explicit validation for unsupported goal operators at the evaluation boundary.
- Preserved disabled-goal short-circuit behaviour and all existing valid goal semantics.
- Added six focused regression tests.
- No retirement or financial calculation logic changed.

### Sprint 243 — GUI / Schema / Report Assumption Consistency
- Hardened Excel assumption export with audit descriptions and deterministic JSON serialization for nested assumptions.
- Added complete GUI/schema round-trip regression coverage.
- Preserved all financial calculation logic and assumption defaults.

## Sprint 248 — Schedule Interaction Hardening

- Added eleven regression tests covering interactions among annual spending, investment-return, ISA-return, State Pension earnings-growth and ISA-allowance schedules.
- Protected schedule independence, precedence and downstream inflation/charge/roll-forward behaviour.
- No financial calculation logic or assumption defaults changed.

### Sprint 250 — Monte Carlo / Deterministic Parity

- Added executable parity coverage for deterministic and Monte Carlo investment-return boundaries.
- Protected Monte Carlo return precedence, charge handling, seeded injection and repeatability.
- No financial calculation logic or assumption defaults changed.

## Sprint 277 — Assumptions / Engine / GUI Coverage Audit
- Hardened the health-check CLI smoke test timeout for slower Windows/Python environments; production simulation settings remain unchanged.

- Added `scripts/audit_assumption_coverage.py` to cross-check assumptions defaults against the schema, operational role catalog, consumer boundaries, audit descriptions and GUI complete-JSON editor boundary.
- Added `planner/docs/ASSUMPTION_COVERAGE_AUDIT.md` with run instructions, interpretation and explicit limitations.
- Added regression tests for zero-gap static coverage and guardrails against overstating financial correctness.
- Updated release manifest/evidence fallback defaults to Sprint 277 and package audit required entries.
- No financial calculation logic, assumptions defaults, or golden baseline changed.


## Sprint 278 — GUI Assumptions Workflow Coverage

- Added an integration-test matrix for the complete assumptions editor workflow: validate, format, apply, explicit save, reload, discard, dirty-state reporting, malformed text, and invalid-document atomicity.
- Verified active memory, persisted JSON, and the saved baseline remain separate across the documented editing actions.
- Updated release manifest/evidence defaults and package-audit traceability for Sprint 278.
- No production financial calculations, assumptions defaults, or golden baseline changed.


## Sprint 279 — Inflation-Adjusted ISA Allowance

- Changed the shipped `inflation_link_isa` setting to **false** so inflation adjustment is opt-in; users can enable it explicitly in assumptions.
- Added regression tests for default-off behavior, explicit opt-in, tax-year schedule transitions, schedule/inflation precedence, and the property-sale proceeds cap.
- Refreshed the golden projection baseline to reflect the agreed default-setting change; linked calculations remain unchanged when explicitly enabled.
- Advanced release-manifest and evidence defaults to Sprint 279 and added package-audit requirements for this sprint's artifacts.

## Sprint 281 — End-to-End Scenario Integration

- Added full-planner scenario regression coverage for deterministic repeatability, timeline integrity, inflation-to-spending/funding propagation, State Pension policy toggle effects, and the ISA inflation-link opt-in.
- Added finite-output and shipped-assumptions immutability checks.
- No production financial calculation logic, assumption defaults, or golden baseline values changed.


## Sprint 282 — Tax and Withdrawal Scenario Integration

- Added end-to-end regression tests for the strategy-to-withdrawal-to-tax pipeline across pension-first and ISA-first scenarios.
- Protected gross/net pension income reconciliation, annual pension-income caps, tax-free cash lifetime limits, exhausted-asset shortfalls, summary aggregation, and finite outputs.
- These tests characterize current engine behavior; they do not imply that a strategy is universally optimal or provide tax advice.
- No production financial calculations, assumptions defaults, or golden baseline values changed.

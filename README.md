# Retirement Planner

**Version:** 2.0 RC2
**Architecture branch:** `rc2-architecture`

**Current RC4 development checkpoint:** Sprint 275 — Reproducible Release Evidence. The release evidence reconciler cross-checks pytest collection, source hashes, manifest and ZIP inventory while explicitly distinguishing collection from test execution. See `PROJECT_STATUS.md` for validation evidence.

A UK retirement-planning application written in Python. The system projects retirement finances year-by-year, evaluates retirement-age scenarios, produces recommendations, runs sensitivity analysis, and generates professional reports.

## Current capabilities

- Pension projection and withdrawals
- State Pension projection for both spouses
- ISA and cash-savings modelling
- UK income-tax modelling
- Cash-flow and income-shortfall analysis
- Retirement-age scenario comparison and scoring
- Recommendation and risk analysis
- Monte Carlo analysis
- Sensitivity analysis
- Investment/market scenario support
- Chart generation
- PDF, Excel and console reporting
- Golden-scenario regression coverage
- Typed engine contracts using Python `Protocol`
- Optimisation policy comparison (Personal Allowance vs Basic-rate band)

## Architecture

The application is deliberately engine-driven:

```text
Application entry points
        |
        v
Scenario / Planner orchestration
        |
        v
Calculation engines
        |
        v
Analysis / decision engines
        |
        v
Report adapters and reports
```

The core rule is:

> **Planner orchestrates. Engines calculate. Reports present.**

Business rules should live in one place, configuration should come from `Assumptions`, engines should not write reports, and reports should not perform financial calculations.

See:

- `planner/docs/RELEASE_READINESS.md` — repeatable release gates and safe technical-debt policy
- `planner/docs/ARCHITECTURE.md` — architecture and dependency rules
- `planner/docs/ENGINE_CATALOG.md` — engine responsibilities and interfaces
- `planner/docs/CODING_STANDARDS.md` — implementation conventions
- `planner/docs/assumptions.md` — assumptions/configuration reference
- `planner/docs/ROADMAP.md` — release roadmap
- `planner/docs/DEVELOPER_ARCHITECTURE_GUIDE.md` — practical change, contract, testing and checkpoint guidance

## Running the planner

```powershell
python main.py
```

## Generate the PDF report

```powershell
python create_report.py
```

## Run the recommendation report

```powershell
python recommend.py
```

## Run the health check

```powershell
python health_check.py
```

## Run tests

```powershell
python -m pytest -q
```

Historical checkpoint note (superseded): Sprint 254 initially recorded the user-confirmed Sprint 253 baseline of 1,294 tests and a pending partitioned rerun. See the current Sprint 256 checkpoint summary above and `planner/docs/CHECKPOINT_RECONCILIATION.md` for the verified result.

## Development approach

This project uses incremental sprints. Each sprint should preserve the previous passing-test checkpoint, avoid unnecessary rewrites, and leave the calculation behaviour unchanged unless the sprint explicitly targets a calculation rule.

### Flexible GUI assumptions
The scenario GUI provides an advanced editor for the complete `assumptions.json` document. Validated edits can be applied in memory or explicitly saved, and the integration test suite verifies that meaningful assumption changes flow through the real projection pipeline.

### Current checkpoint — Sprint 179

The GUI flexible assumptions workflow is covered end-to-end from JSON editing through validation, persistence/reload, and real scenario projection. Multi-field edits are regression-tested across conservative, central and optimistic scenarios.

Current regression status: **944 tests passing, 9 subtests**.

No retirement, tax, State Pension, ISA, savings, withdrawal or projection calculation engine logic was changed in Sprint 179.

### Current application integration checkpoint
Sprint 180 establishes an explicit GUI projection-result freshness contract. The displayed scenario results are marked stale whenever editable projection controls or flexible assumptions change, and become current again only after a successful Run or Reload.

Current regression checkpoint: **948 passing tests, 9 subtests**.


### Current application integration checkpoint — Sprint 181

Sprint 181 adds a calculation-free result/report contract to the GUI. Report payloads and text are sourced from the displayed `ScenarioProjectionViewModel`, and report retrieval is blocked while results are stale.

Current regression checkpoint: **951 passing tests, 9 subtests**.

No retirement, tax, State Pension, ISA, savings, withdrawal or projection calculation engine logic was changed in Sprint 181.

### Current RC4 checkpoint — Sprint 182

The GUI projection layer now publishes one immutable report snapshot for each current projection result. Report/export consumers are prevented from reading stale results and repeated access reuses the same presentation snapshot. Current regression status: **954 tests passing, 9 subtests**.


### Current checkpoint
**Sprint 184 — 958 tests passing (9 subtests)**

### Current checkpoint

Sprint 186 — GUI Projection Result Snapshot File Export Integration — 965 tests passing (9 subtests). GUI/integration regression: 244 passed.

The GUI result path now supports calculation-free JSON and text exports from the same immutable current-result snapshot used by report consumers. Stale or closed results are rejected before export.

### Current application checkpoint

Sprint 188 — 969 tests passing. GUI projection results can be exported as a consistent JSON/text bundle from the same immutable current-result snapshot.

### Current checkpoint

Sprint 189 — GUI Projection Result Snapshot Export Bundle Overwrite Safety. Full regression: 972 tests passing, 9 subtests.

Result bundles are protected against accidental overwrite by default and can be intentionally replaced with transactional rollback protection.

### Custom assumptions files

The main planner and strategy comparison CLIs accept an explicit assumptions document:

```text
python main.py --assumptions path/to/assumptions.json
python compare.py --assumptions path/to/assumptions.json
```

The supplied JSON is loaded and validated through the same `Assumptions` boundary used by the GUI.


### Sprint 191 — Unified projection/report/export workflow

The scenario projection application now exposes one workflow result containing the validated inputs, immutable projection snapshot, report payload and report text. The same calculation-free JSON/text bundle export boundary is shared by the GUI and the public `scenario_report.py` CLI.

```text
python scenario_report.py
python scenario_report.py --assumptions path/to/assumptions.json --export-dir exports
python scenario_report.py --export-dir exports --export-stem scenario_latest --overwrite
python scenario_report.py --pdf exports/scenario_latest.pdf
```

The default export mode never replaces an existing companion file; `--overwrite` must be explicitly requested.

Current checkpoint: **978 tests passing, 9 subtests** (Sprint 191).

### Sprint 192 — GUI unified workflow adoption

The GUI controller now consumes the same unified projection/report workflow boundary introduced for the public scenario-report CLI. A successful GUI run publishes the validated inputs, projection view model, immutable report snapshot, report payload and report text together, and the GUI reuses that published snapshot for its result/export consumers.

A failed workflow publication restores the prior in-memory projection inputs, preserving the existing GUI transaction boundary.

Current checkpoint: **Sprint 192 — 981 tests passing, 9 subtests**.
Current development checkpoint: **Sprint 193 — 984 tests passing (9 subtests)**. The unified projection/report workflow result now enforces a recursively immutable report payload and validates payload/text consistency against its published snapshot.

### Sprint 194 — unified workflow result export boundary

The published `ScenarioProjectionWorkflowResult` now exposes the direct JSON/text export boundary. The public `scenario_report.py` CLI consumes that result directly, while the application helper remains as a compatibility wrapper.

Current checkpoint: **Sprint 194 — 987 tests passing, 9 subtests**.


### Sprint 195 — GUI-neutral projection workflow

The reusable projection/report/export workflow now lives in `planner/projection/scenario_projection_workflow.py`, independent of the desktop GUI. The existing `planner.gui.scenario_projection_application` module remains as a compatibility import surface for existing callers.

The public `scenario_report.py` CLI and GUI controller use the same canonical workflow contracts.

Current checkpoint: **Sprint 195 — 990 tests passing, 9 subtests**.

### Sprint 196 — public projection workflow API

The unified projection/report/export workflow is now exposed through the package-level `planner.projection` API. Application and presentation consumers use the same canonical workflow types without importing implementation details from the GUI package.

The existing deep implementation import remains available for compatibility, as does `planner.gui.scenario_projection_application` for older GUI callers.

Current checkpoint: **Sprint 198 — 999 tests passing, 9 subtests**.


### Sprint 197 — professional scenario projection PDF

The public scenario-report workflow can now create a calculation-free PDF directly from the immutable `ScenarioProjectionWorkflowResult`. The PDF contains projection inputs, scenario summaries, outcome ranges, scenario detail and year-by-year projection tables.

```text
python scenario_report.py --pdf exports/scenario_latest.pdf
```

### Sprint 198 — professional PDF report presentation

The scenario projection PDF now includes a vector balance-trajectory chart, consistent page headers/footers with page numbering, and verified multi-page repetition of the year-by-year table header. Structural PDF tests use `pypdf`, declared under the optional `test` dependency in `pyproject.toml`.

Current checkpoint: **Sprint 198 — 999 tests passing, 9 subtests**.

### Strategy comparison PDF report

The public `compare.py` entry point can now generate a professional comparison PDF from the already-computed strategy results:

```text
python compare.py --pdf exports/strategy_comparison.pdf
```

The PDF is presentation-only and performs no additional financial calculations.


Current development checkpoint: Sprint 200 - 1008 tests passing.

### Professional Health Check PDF

The public health-check workflow can also produce a professional PDF from the results it already computes:

```bash
python health_check.py --pdf exports/retirement_health_check.pdf
```

The PDF contains the executive health dashboard, projected position, Monte Carlo outcome-range landmarks, key findings and report provenance. It performs no second financial calculation.

### Sprint 202 — professional retirement goals PDF report

The health-check workflow can now export a dedicated retirement-goals PDF from the existing goal-evaluation results:

```text
python health_check.py --goals-pdf exports/retirement_goals.pdf
```

The goals report presents target-versus-actual status, achieved/not-achieved markers, an executive goal summary, vector status visualisation and report provenance. It performs no second financial calculation and does not mutate the supplied goal results.

Current development checkpoint: **Sprint 202 — 1014 tests passing (9 subtests).**

### Sprint 203 — GUI professional PDF report suite

The scenario projection desktop GUI now provides an **Export PDF reports…** action. Choose a destination folder and RetirementPlanner writes the complete professional report suite using the current in-memory assumptions and the current published projection workflow result:

- `retirement_scenario_projection.pdf`
- `retirement_strategy_comparison.pdf`
- `retirement_recommendation.pdf`
- `retirement_health_check.pdf`
- `retirement_goals.pdf`

The GUI scenario report reuses the currently published projection result rather than recalculating the displayed projection. The remaining reports reuse their existing calculation/report boundaries using the current in-memory assumptions. The PDF renderers themselves remain calculation-free.

Current development checkpoint: **Sprint 203 — 1017 tests passing, 9 subtests**.

### Sprint 204 report-suite publication safety

The GUI-neutral professional PDF report suite now defaults to safe publication: existing output files are rejected before report calculation. API callers can explicitly use `overwrite=True` for recoverable five-file replacement with rollback on publication failure.


### Sprint 205 — consolidated professional report pack

After exporting the five-file professional report suite, the outputs can be composed into one bookmarked PDF:

```text
python report_pack.py --directory exports --pdf exports/retirement_report_pack.pdf
python report_pack.py --directory exports --pdf exports/retirement_report_pack.pdf --overwrite
```

The resulting pack contains a cover/index page followed by the existing Scenario Projection, Strategy Comparison, Recommendation, Health Check and Retirement Goals reports. It does not recalculate the underlying retirement plan or mutate the source PDFs. Install `pypdf>=5.0` for report-pack composition (also exposed as the optional `reports` dependency).

Current checkpoint: **Sprint 205 — 1023 tests passing, 9 subtests**.

### Professional report pack GUI export

The scenario projection GUI now provides `Export PDF report pack…`. It writes the five professional PDF reports plus a consolidated bookmarked `RetirementPlanner_Report_Pack.pdf` into the selected folder. The consolidated pack uses the existing report-suite outputs and does not recalculate the displayed projection.

## Assumptions calculation coverage

The GUI and JSON schema expose a broader set of planning inputs than the live financial engines currently consume. Development is now prioritising calculation coverage before further reporting expansion. Each previously inactive or partial assumption will be either wired into the appropriate calculation engine, explicitly documented as configuration-only, or retired from the active schema.

Sprint 207 completed the first correction in this phase: `tax_free_pension_percentage` is now an operational input to the pension and tax engines, including remaining allowance tracking and range validation. The golden scenario is maintained against the corrected behaviour.


### Sprint 208 — assumptions calculation coverage: maximum pension income

`max_pension_income` is now an active annual net pension-income ceiling used by the withdrawal strategies. Where the pension ceiling cannot meet the spending requirement, available ISA funds are used and any remaining unmet amount is recorded as an income shortfall instead of silently exceeding the configured limit.

The default assumptions therefore now genuinely enforce the configured £30,000 maximum pension-income setting.

Current development checkpoint: **Sprint 208 — 1034 tests passing, 9 subtests.**

## Current RC4 checkpoint

Sprint 213 — **1063 tests passing, 9 subtests**.

The assumptions calculation-coverage programme is active. Investment return and platform/fund charge assumptions now feed the live standard projection and Monte Carlo return path.


### Assumptions calculation coverage — Sprint 210

`property_sale` is now applied as a one-off cash event at `property_sale_age`. Up to `annual_isa_allowance` of the sale proceeds is routed to the ISA, with the remaining proceeds retained in savings. Both balances continue through their existing roll-forward engines.

### Sprint 212 — inflation-linked tax calculation coverage

`inflation_link_tax` is now operational in the live tax calculation. When enabled, the configured personal allowance and basic-rate threshold are scaled using each projected year's compounded inflation factor; when disabled they remain nominal. The first projection year always uses the configured thresholds. Existing tax rates, pension tax-free cash and gross-up behaviour remain unchanged.

The golden projection baseline was refreshed because the default inflation-linked tax setting now changes later-year tax and downstream pension balances.

Current development checkpoint: **Sprint 213 — 1063 tests passing, 9 subtests**.


### Sprint 213 — inflation-linked ISA calculation coverage

`inflation_link_isa` is now operational at the property-sale/ISA allowance boundary. When enabled, the configured annual ISA allowance is scaled by the projected year's compounded inflation factor; when disabled it remains nominal. The allowance remains capped by the actual property-sale proceeds, and the first projection year retains the configured allowance.


Current RC4 checkpoint: **Sprint 213 — 1063 tests passing, 9 subtests**.


## Sprint 229
Goal constraint result-boundary hardening: malformed actual values and empty spending timelines now fail with explicit validation errors before constraint comparison.

## Sprint 230 — complete assumptions catalog and GUI coverage

The assumptions audit catalogue now includes both required and optional schema-defined fields. Regression coverage also proves that every current top-level `assumptions.json` key is described and that the GUI's **Edit all assumptions…** workflow can round-trip the complete document, including optional annual schedules, through validation, save and reload without losing fields.

The GUI therefore has complete current-document coverage; the remaining assumptions programme concerns whether individual assumptions are operational calculation inputs, compatibility aliases, configuration/goal controls, or candidates for future calculation wiring.

## Sprint 231 — assumption operational coverage and legacy boundaries

The assumptions calculation-coverage programme now has an explicit operational-role catalogue. Every schema-defined assumption is classified as a live projection input, Monte Carlo input, legacy compatibility alias, auxiliary configuration, or goal-domain configuration. This is a documentation/audit boundary only and does not change financial calculations.

In particular, `target_net_income` remains explicitly auxiliary rather than being silently promoted to the live spending target, while `inflation`, `savings_interest` and `pension_growth` remain explicit legacy aliases behind the canonical resolver.

Current RC4 checkpoint: **Sprint 231 — 1167 tests passing, 9 subtests**.

## Sprint 232 — assumption consumer boundary hardening

- Added an explicit consumer-boundary catalogue linking every operational assumption role to its application consumers.
- Added regression coverage for complete role-to-consumer coverage and consumer-module importability.
- No financial calculation semantics changed.

Current RC4 checkpoint: **Sprint 232 — 1171 tests passing, 9 subtests**.

### Sprint 233 — Legacy Assumption Access Boundary Hardening

Sprint 233 removed the remaining direct planner read of the legacy `pension_growth` field from the portfolio-statistics projection boundary. The canonical `AssumptionResolver` now governs that lookup, preserving canonical `expected_investment_return` precedence and the established legacy fallback. Four focused tests and the full **1175-test** suite pass; no financial calculation semantics were changed.

### Sprint 234

Legacy assumption access is now regression-guarded: the historical `inflation`, `savings_interest` and `pension_growth` aliases are confined to the canonical `AssumptionResolver` compatibility boundary. This is a calculation-free hardening change; financial calculation semantics are unchanged.
## Sprint 236 — Canonical Investment Return Validation Boundary Hardening

- Hardened the validation boundary so `expected_investment_return` is resolved through `AssumptionResolver` rather than read directly by `ValidationEngine`.
- Preserved canonical-over-legacy precedence and `pension_growth` fallback semantics for older callers/configurations.
- Added four focused regression tests covering canonical precedence, legacy fallback, validation rejection and direct-read exclusion.
- No retirement, tax, State Pension, ISA, savings, withdrawal, investment-return or Monte Carlo calculation semantics were intentionally changed; this is a validation/access-boundary cleanup.

- Sprint 236 focused regression: **4 passed**.
- Full-suite validation: pending.

**Current checkpoint: Sprint 236 — 1186 tests expected after full-suite validation.**


## Sprint 237 — Canonical Savings Interest Assumption Boundary Hardening

- Added regression coverage proving the Savings Engine consumes the canonical `savings_interest_rate` through `AssumptionResolver`.
- Preserved legacy `savings_interest` fallback semantics.
- Added a source-level guard preventing direct canonical or legacy savings-interest reads outside `AssumptionResolver`.
- Sprint 237 focused regression: **4 passed**.
- Compile check: passed.
- Current checkpoint: Sprint 237 — **1190 tests expected** from the 1186-test Sprint 236 baseline plus four Sprint 237 regressions.

## Current RC4 checkpoint — Sprint 238

Sprint 238 hardened the Monte Carlo expected-return validation boundary. `ValidationEngine` now resolves the Monte Carlo return through `AssumptionResolver.monte_carlo_expected_return()`, preserving the existing `expected_return` → `expected_investment_return` → `pension_growth` fallback order. No financial calculation semantics changed.

**Current RC4 checkpoint: Sprint 238 — 1194 tests passing, 9 subtests.**

## Sprint 239 — canonical assumption consumer boundary hardening

The assumptions programme now has an explicit resolver boundary for the remaining selected canonical calculation inputs covering investment volatility, inflation volatility, ISA growth and State Pension configuration. State Pension, ISA/investment-return, Monte Carlo and investment-validation consumers no longer read those canonical fields directly. Regression guards protect the boundary while preserving existing financial calculation behaviour.

Current RC4 checkpoint: **Sprint 239 — 1198 tests passing, 9 subtests**.


## Sprint 240 — assumption precedence and legacy mapping hardening

Sprint 240 centralises remaining investment-return charge and schedule access through `AssumptionResolver` and explicitly protects Monte Carlo return precedence. No financial calculation semantics changed.

Current RC4 checkpoint: **Sprint 240 — 1202 tests in suite; 84 assumption/affected-engine regression tests passed.**

## Sprint 242 — assumption validation and error-handling hardening

Sprint 242 hardens numeric assumption access at the `AssumptionResolver` boundary. Required numeric assumptions now fail explicitly when missing or invalid, non-finite and boolean values are rejected, and an invalid canonical value cannot silently fall back to a legacy alias. Existing optional defaults and Monte Carlo precedence remain unchanged.

Current RC4 checkpoint: **Sprint 242 — 1212 tests passing.**

## Test collection diagnostics

If pytest totals differ across environments, run `python scripts/test_collection_report.py --output collection-local.json`, then compare against another report with `python scripts/test_collection_report.py --compare collection-other.json`. See `planner/docs/TEST_COLLECTION_DIAGNOSTICS.md`.



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

## Current RC4 checkpoint — Sprint 276

Sprint 276 adds a gated GitHub Actions release workflow, deterministic ZIP packaging from a current SHA-256 manifest, package-audit requirements for the release workflow assets, and documentation separating workflow artifacts, GitHub Release publication and source-branch updates. The Sprint 275 checkpoint was user-validated with 1,496 passed and 2 Windows symlink-permission skips. Sprint 276 focused regressions and packaging checks are recorded in its release report; a full Sprint 276 test run remains pending. GitHub publication of this local checkpoint is not confirmed. No production financial calculations, assumptions defaults or golden baseline were intentionally changed.


## Sprint 278 GUI assumptions editor coverage

Sprint 278 adds regression coverage for the complete assumptions JSON editor workflow. See `planner/docs/GUI_ASSUMPTIONS_COVERAGE.md` for scope, limitations, and the focused test command.


## Sprint 279 — inflation-adjusted ISA allowance

The shipped `inflation_link_isa` setting is **off by default**. Enable it explicitly to inflate the allowance used when sheltering property-sale proceeds into an ISA. The configured or scheduled allowance remains capped at actual sale proceeds. ISA allowance schedules are controlled separately by `isa_allowance_schedule_enabled`; see [the ISA allowance guide](planner/docs/INFLATION_ADJUSTED_ISA_ALLOWANCE.md) for schedule boundary semantics.


Sprint 280: [Pension funding and State Pension forecast integration](planner/docs/PENSION_FUNDING_FORECAST_INTEGRATION.md).


## Sprint 282 — Tax and Withdrawal Scenario Integration

- Added nine end-to-end tests for pension/ISA withdrawal strategy differences, gross/net tax reconciliation, pension-income caps, tax-free cash lifetime limits, exhausted-asset shortfalls, summary aggregation, and finite outputs.
- The tests characterize current behavior and are not tax advice or a claim that one strategy is universally optimal.
- No production financial calculations, assumption defaults, or golden baseline values changed.
- Focused Sprint 249 / 281 / 282 regression set: 27 passed. Full-suite acceptance remains pending user-side `python -m pytest -ra`.

**Current Sprint:** Sprint 282 — Tax and Withdrawal Scenario Integration

### Current checkpoint: Sprint 285

Sprint 285 consolidates release-readiness traceability and adds checks for the required release gates, current manifest inventory, and unchanged shipped assumptions and reviewed golden baseline. It does not change production financial calculations or default assumptions. Full-suite acceptance is pending the target-environment `python -m pytest -ra` run. See `planner/docs/SPRINT285_RELEASE_READINESS.md`.

# RC4 Roadmap

## Sprint 63 — Tax-Free Cash Strategy Infrastructure

- Track a finite tax-free pension cash allowance.
- Support annual/partial use of the allowance.
- Separate tax-free cash from taxable pension withdrawals.
- Preserve remaining allowance between years.
- Keep the strategy layer isolated from existing tax engines pending integration.

## Sprint 64 — Tax-Free Cash Integration Adapter

- Provide a stable integration contract between the tax-free cash strategy and the existing withdrawal/tax pipeline.
- Preserve the deterministic engines unchanged while the integration contract is tested.
- Track progressive consumption of the remaining tax-free allowance.

## Sprint 65 — Real Planner Strategy Comparison

- Compare outputs from the existing tax/withdrawal engines.
- Identify the lowest-tax strategy.
- Identify the highest-net-income strategy.
- Report potential tax saving between strategies.
- Keep UK tax calculation inside the existing tax engine.

## Sprint 66 — Lifetime Strategy Aggregation

- Aggregate yearly withdrawal strategy results across the retirement horizon.
- Compare cumulative tax, net income and tax-free cash usage.
- Preserve existing tax-engine calculations.

## Sprint 67 — Actual Pension Fund Data Model

- Represent real pension funds by provider, fund name and optional identifier.
- Support multiple fund allocations.
- Track annual fund charges.
- Validate portfolio allocations total 100%.
- Prepare the assumptions model for future GUI input and historical-performance analysis.

## Sprint 68 — Historical Fund Performance

- Store annual historical fund returns.
- Calculate arithmetic mean and compounded annualised return.
- Identify best and worst historical years.
- Provide clean inputs for future risk/Monte Carlo modelling.
- Treat historical performance as evidence, not a guaranteed future return.

\n## Sprint 69 — Fund Risk Metrics

- Calculate historical volatility.
- Count negative-return years and their frequency.
- Calculate maximum historical drawdown.
- Calculate downside deviation.
- Keep all metrics as internally derived data, not user assumptions.

## Sprint 70 — Portfolio Risk Model

- Combine multiple actual funds using their portfolio allocations.
- Calculate year-by-year weighted portfolio returns.
- Calculate portfolio volatility, negative-year frequency, drawdown and downside deviation.
- Keep portfolio risk metrics as internally derived data.
- Do not treat historical portfolio performance as a guaranteed future return.

## Sprint 71 — Fund-Informed Projection

- Introduce a fund-informed projection scenario derived from portfolio characteristics.
- Preserve the existing baseline projection separately.
- Use portfolio historical return and volatility as descriptive projection inputs.
- Do not treat historical performance as a guaranteed forecast.
- Keep derived projection characteristics outside `assumptions.json`.

## Sprint 72 — Fund Data Import

- Add a provider-neutral internal fund-return import format.
- Support validated record imports.
- Support CSV import using the same internal representation.
- Keep external data separate from `assumptions.json`.
- Leave provider/API/factsheet adapters for later.

## Sprint 73 — Fund Source / Adapter Layer

- Introduce a provider-neutral adapter boundary for external fund data.
- Preserve source name/version metadata internally.
- Provide an in-memory adapter for tests and manual workflows.
- Keep providers/API integrations outside the core planner.
- Continue keeping imported/derived fund data separate from `assumptions.json`.

## Sprint 74 — Fund Source Validation

- Validate imported fund source records before risk/projection use.
- Detect duplicate fund/year observations.
- Report source coverage and record counts.
- Keep validation/provenance data internal.

## Sprint 75 — Fund Data Quality & Coverage

- Identify gaps in annual historical fund series.
- Calculate historical coverage percentage.
- Distinguish missing observations from zero returns.
- Apply a configurable minimum-history rule before risk calculations.
- Keep quality/provenance information internal and separate from `assumptions.json`.

## Sprint 76 — Fund History Suitability

- Distinguish data availability from modelling suitability.
- Apply separate minimum-history rules for risk metrics and projections.
- Block incomplete historical series from suitability.
- Keep suitability decisions internal and explainable.

## Sprint 77 — Fund Suitability Decision

- Convert history suitability into an explicit decision contract.
- Distinguish risk-only, risk-and-projection, and unsuitable histories.
- Preserve an explainable reason for every decision.
- Keep the decision layer independent from GUI and projection engines.

## Sprint 78 — Fund Risk Eligibility

- Connect fund suitability decisions to risk-analysis eligibility.
- Explicitly exclude unsuitable histories from risk analysis.
- Preserve exclusion reasons for reporting and future GUI use.
- Keep projection eligibility separate from risk eligibility.

## Sprint 79 — Portfolio Risk Eligibility Integration

- Integrate fund risk eligibility at portfolio level.
- Ensure ineligible funds cannot influence portfolio-risk inputs.
- Preserve excluded-fund identifiers and reasons.
- Keep the integration auditable and independent of the GUI.

## Sprint 80 — Portfolio Risk Calculation Integration

- Apply fund risk eligibility before portfolio risk calculation.
- Block calculation when any portfolio fund is ineligible.
- Never silently re-weight or substitute an excluded fund.
- Preserve included/excluded funds and reasons in the result.
- Reuse the existing PortfolioRiskAnalyzer for the actual calculation.

## Sprint 81 — Portfolio Risk Metrics

- Calculate weighted portfolio return from eligible funds.
- Calculate a transparent portfolio-volatility measure.
- Preserve included/excluded fund information and reasons.
- Refuse to produce misleading metrics when no eligible fund has a positive allocation.
- Keep the calculation auditable and separate from the GUI.

## Sprint 82 — Fund Portfolio Allocation

- Add a dedicated user-allocation validation layer.
- Preserve entered allocations without silently normalising them.
- Require allocations to total 100%.
- Reject negative allocations and empty portfolios.
- Support the current 75% Aviva / 25% Sky test portfolio.
- Keep user allocation data separate from internal fund characteristics.

## Sprint 83 — Fund Value Calculation

- Calculate monetary fund values from `starting_pension` and validated allocations.
- Keep fund values derived rather than duplicated in user assumptions.
- Use decimal arithmetic and penny rounding.
- Reconcile rounding so calculated fund values always preserve the starting pension total.
- Support the current 75% Aviva / 25% Sky test portfolio.

## Sprint 84 — Fund Investment Profiles

- Establish an internal provider-neutral investment-profile model.
- Keep fund characteristics separate from user assumptions and allocations.
- Represent target-retirement and lifestyle/glide-path strategies.
- Capture identifiers, provider, currency, charges, target year, underlying investments, data source and data quality.
- Seed the Aviva and Sky test investment profiles agreed for RC4.

## Sprint 85 — Fund Data to Projection Inputs

- Translate internal investment profiles into explicit projection inputs.
- Report historical return, volatility, charges and asset-allocation availability.
- Preserve glide-path and target-retirement characteristics.
- Expose data limitations and confidence rather than fabricating missing values.
- Keep projection-input construction separate from the projection engine and GUI.

## Sprint 86 — Historical Fund Returns

- Add structured annual historical fund-return observations.
- Preserve fund identifier, year, return and data provenance.
- Distinguish actual historical observations from estimates.
- Reject duplicate fund/year observations.
- Provide fund-specific historical retrieval in chronological order.
- Keep historical return storage separate from projection calculations.

## Sprint 87 — Historical Performance Statistics

- Calculate cumulative and annualised historical return.
- Calculate minimum and maximum annual return.
- Calculate sample volatility when sufficient observations exist.
- Track actual versus estimated observations.
- Support actual-only calculations.
- Preserve source observations and provenance.
- Return explicit insufficient-data results instead of fabricating statistics.

## Sprint 88 — Portfolio Historical Statistics

- Calculate portfolio-level historical return from fund allocations and aligned annual returns.
- Calculate cumulative and annualised portfolio return.
- Calculate minimum/maximum portfolio-year return and sample volatility.
- Report negative-year count/rate.
- Preserve the 75% Aviva / 25% Sky allocation model through the statistics layer.
- Track actual versus estimated observation counts without inventing data.
- Validate allocation totals, matching fund sets, and equal history lengths.

## Sprint 89 — Portfolio Risk & Return Scenarios

- Build conservative, central and optimistic descriptive scenarios from validated portfolio statistics.
- Use historical annualised return as the central descriptive input.
- Use observed volatility for a transparent one-volatility-unit range.
- Produce only a central scenario when volatility is unavailable.
- Mark scenarios as descriptive rather than guaranteed forecasts.
- Keep all derived scenario data outside `assumptions.json`.

## Sprint 90 — Fund-Informed Projection Inputs

- Bridge validated portfolio scenarios into a dedicated projection-input object.
- Preserve `starting_pension`, selected scenario and fund allocation.
- Validate allocation totals 100%.
- Keep derived fund information outside `assumptions.json`.
- Provide an explicit disabled path for the existing projection behaviour.
- Do not modify the pension engine in this sprint.


## Sprint 91 — Projection Engine Integration

- Add a controlled return-selection boundary between portfolio scenarios and the projection engine.
- Preserve the legacy projection return when fund-informed mode is absent or disabled.
- Use the selected fund-informed scenario only when explicitly enabled.
- Keep the existing pension engine implementation unchanged in this sprint.
- Preserve scenario provenance and immutability.
- Add regression coverage for legacy and fund-informed paths.

## Sprint 92 — Apply Fund-Informed Returns

- Add investment-growth calculation at the projection boundary.
- Apply legacy or explicitly selected fund-informed returns.
- Preserve provenance and starting balance.
- Support positive, zero and negative scenario returns.
- Do not change withdrawal, tax, State Pension, ISA or Savings logic.

## Sprint 93 — Projection Flow Integration

- Connect the validated projection-return decision to the existing PensionEngine.
- Preserve legacy growth behaviour when fund-informed mode is absent or disabled.
- When enabled, apply the selected fund-informed scenario return to pension growth.
- Keep withdrawal, tax, State Pension, ISA and Savings calculations unchanged.
- Preserve timeline-level market returns for the legacy path.
- Add regression coverage for single-year and multi-year projection behaviour.


## Sprint 94 — Portfolio Scenario Selection

- Add explicit conservative/central/optimistic scenario selection.
- Select only scenarios supported by the available portfolio statistics.
- Preserve `starting_pension` from the caller.
- Preserve the 75/25 fund allocation supplied by the portfolio boundary.
- Keep scenario selection separate from `assumptions.json`.
- Do not silently manufacture optimistic/conservative scenarios when volatility is unavailable.
- Keep tax, withdrawals and other retirement engines unchanged.

## Sprint 95 — End-to-End Projection Scenario Integration

- Use `PortfolioHistoricalStatistics` as the typed portfolio-statistics boundary.
- Select central, conservative or optimistic scenarios directly from typed statistics.
- Preserve the legacy projection path as an explicit fallback.
- Preserve starting pension, portfolio allocation and scenario provenance.
- Verify one-year growth and multi-year compounding at the projection boundary.
- Do not modify `assumptions.json` to store calculated fund statistics.
- Keep tax, withdrawals, State Pension, ISA, Savings, inflation and GUI work outside this sprint.

## Sprint 96 — Portfolio to Full Retirement Projection

- Add an explicit RetirementPlanner application boundary for typed portfolio statistics.
- Run the complete retirement timeline using the selected portfolio scenario.
- Preserve the ordinary legacy `run()` path and regression behaviour.
- Verify central, conservative and optimistic scenarios reach the full pension timeline.
- Verify multi-year pension growth compounds through the existing timeline.
- Preserve starting pension from assumptions and leave portfolio statistics immutable.
- Keep tax, withdrawals, State Pension, ISA and Savings calculations on their existing engines.


## Sprint 97 — Structured Projection Results

- Add immutable, GUI-ready projection result models.
- Preserve scenario and provenance metadata.
- Preserve starting pension and annual return.
- Expose year-by-year starting balance, investment growth, withdrawals and ending balance.
- Expose aggregate ending balance, investment growth and withdrawals without recalculating finances.
- Keep financial engines unchanged.

## Sprint 98 — Scenario Projection Comparison

- Run the supported fund-informed scenarios through the complete retirement projection.
- Expose conservative, central and optimistic projections as one immutable comparison result.
- Preserve year-by-year balances, investment growth and withdrawals for each scenario.
- Preserve scenario return and provenance metadata.
- Expose ending-balance comparison and spread without recalculating finances.
- Allow a controlled subset of scenarios for future UI use.
- Keep the existing retirement, tax, State Pension, ISA and Savings engines unchanged.

## Sprint 99 — Projection Result Adapter

- Add a reporting adapter for structured projection results.
- Expose scenario metadata and complete year-by-year projection rows.
- Preserve ending-balance comparison and aggregate totals.
- Keep the adapter calculation-free: it only reshapes existing domain results.
- Keep financial engines and existing report calculations unchanged.

## Sprint 100 — Scenario Projection Report Output

- Add a stable presentation/report layer over scenario projection results.
- Preserve all existing scenario calculations and provenance.
- Provide compact scenario summaries and flattened year rows.
- Provide deterministic human-readable comparison text.
- Keep report generation calculation-free and GUI-ready.

## Sprint 101 — GUI Scenario View Model

- Add a GUI-neutral, immutable view-model contract for scenario comparison.
- Expose scenario-card summaries without recalculating financial results.
- Expose flattened year-level rows for future tables and charts.
- Preserve scenario ordering, provenance, balances, returns and aggregate totals.
- Preserve the existing report and projection layers as the source of truth.
- Keep PySide6/GUI framework code out of the core planner in this sprint.
- Keep all retirement, tax, State Pension, ISA, Savings and withdrawal calculations unchanged.

## Sprint 102 — Desktop Scenario Comparison GUI

- Add an optional desktop presentation for the scenario projection view model.
- Display conservative, central and optimistic scenario cards.
- Display ending-balance summary and year-by-year projection rows.
- Keep all display formatting outside the financial engines.
- Consume `ScenarioProjectionViewModel` as the GUI boundary; do not recalculate projection results in the GUI.
- Keep the GUI optional so headless/core planner workflows remain usable without a display.
- Keep retirement, tax, State Pension, ISA, Savings and withdrawal calculations unchanged.

## Sprint 103 — GUI Input Binding & Scenario Selection

- Bind desktop presentation to validated retirement-planner inputs without moving calculations into the GUI.
- Provide an immutable input contract for starting pension, retirement age, projection end age and selected scenarios.
- Apply GUI edits to the in-memory assumptions model only; persistence remains explicit through the existing assumptions save boundary.
- Allow the GUI/application layer to request a selected subset of conservative, central and optimistic scenarios.
- Reuse the existing portfolio statistics calculator and scenario comparison runner as calculation boundaries.
- Preserve the `ScenarioProjectionViewModel` as the presentation contract.
- Keep all retirement, tax, State Pension, ISA, savings and withdrawal calculations unchanged.

## Sprint 104 — Interactive GUI Editing & Re-run

- Wire the existing `ScenarioProjectionApplication` into the desktop scenario GUI.
- Add editable starting pension, retirement age and projection end age controls.
- Add conservative, central and optimistic scenario selection controls.
- Validate GUI input before applying it to the in-memory assumptions model.
- Rebuild the selected scenario view model through the existing application/calculation boundaries.
- Refresh scenario cards and year-level results without moving financial calculations into the GUI.
- Keep persistence explicit through a separate Save assumptions action.
- Preserve the existing deterministic Aviva/Sky demo data until fund-return import wiring is separately planned.
- Keep retirement, tax, State Pension, ISA, savings and withdrawal calculations unchanged.

## Sprint 105 — GUI Controller Separation & State Synchronization

- Extract GUI event orchestration into a calculation-free `ScenarioProjectionGuiController`.
- Keep widget construction and formatting in the desktop window while controller code owns run/save event coordination.
- Return an immutable run result containing validated inputs and the refreshed GUI view model.
- Preserve selected scenario state across interactive re-runs.
- Keep allocations and fund-return inputs copied at the controller boundary to prevent accidental caller mutation.
- Preserve explicit assumptions persistence through the existing Save assumptions boundary.
- Keep all retirement, tax, State Pension, ISA, savings and withdrawal calculations unchanged.

## Sprint 106 — GUI Usability & Presentation Polish

- Improve desktop GUI layout, spacing, labels and result readability without moving calculations into the presentation layer.
- Show an explicit saved/unsaved assumptions status using the existing change-tracking boundary.
- Show the currently selected scenarios clearly after edits and re-runs.
- Add Reset inputs and Reload saved controls while keeping persistence explicit.
- Reuse existing `ScenarioProjectionGuiController`, `ScenarioProjectionApplication` and `ScenarioProjectionViewModel` boundaries.
- Keep headless/core planner workflows safe and free of new external dependencies.
- Keep all retirement, tax, State Pension, ISA, savings and withdrawal calculations unchanged.

## Sprint 107 — GUI Robustness & Edge-Case Handling

- Harden GUI input parsing against non-finite monetary values before they reach the calculation boundary.
- Exercise one-, two- and three-scenario selections through the controller boundary.
- Make projection runs rollback to the previous in-memory inputs if rebuilding the view model fails, avoiding partially applied GUI state.
- Preserve explicit Save assumptions semantics and existing controller/application/view-model boundaries.
- Keep headless/core planner workflows safe and avoid new external dependencies.
- Keep all retirement, tax, State Pension, ISA, savings and withdrawal calculations unchanged.

## Sprint 108 — GUI Pending-State & Persistence Refinement

- Distinguish last-applied projection state from GUI edits that have not yet been run.
- Show pending scenario selection immediately without treating it as silently applied financial state.
- Detect pending changes across pension/age controls and scenario checkboxes, including invalid temporary input.
- Keep Reset inputs tied to the last applied in-memory assumptions and preserve explicit Save assumptions semantics.
- Keep headless/core planner workflows safe and avoid new external dependencies.
- Keep all retirement, tax, State Pension, ISA, savings and withdrawal calculations unchanged.

## Sprint 109 — GUI Interaction Polish

- Refresh GUI state immediately after keyboard edits as well as scenario checkbox changes.
- Keep Run projection enabled only when controls differ from the last applied state.
- Keep Save assumptions disabled while pending edits exist, preventing accidental persistence of an older applied state.
- Add simple Enter-to-run and Escape-to-reset keyboard shortcuts.
- Focus the primary pension input when the desktop window becomes interactive.
- Preserve the pending/applied/saved state model introduced in Sprint 108.
- Keep headless/core planner workflows safe and avoid new external dependencies.
- Keep all retirement, tax, State Pension, ISA, savings and withdrawal calculations unchanged.

## Sprint 110 — GUI Validation Feedback

- Provide immediate, actionable validation feedback for incomplete or invalid editable projection controls.
- Keep invalid pending inputs from enabling Run projection while preserving the controller/application validation boundary as authoritative.
- Surface pension, age-range and empty-scenario errors directly in the GUI input area.
- Preserve pending/applied/saved state semantics, Reset inputs and Reload saved behaviour.
- Keep headless/core planner workflows safe and avoid new external dependencies.
- Keep all retirement, tax, State Pension, ISA, savings and withdrawal calculations unchanged.

## Sprint 111 — GUI Accessibility & Keyboard Usability

- Improve keyboard-only operation with explicit focusable controls and predictable action shortcuts.
- Route invalid projection input focus to the first actionable control requiring attention.
- Keep validation feedback accessible even when a concrete input widget is unavailable.
- Preserve pending/applied/saved state semantics and the existing controller/application/view-model boundaries.
- Keep headless/core planner workflows safe and avoid new external dependencies.
- Keep all retirement, tax, State Pension, ISA, savings and withdrawal calculations unchanged.

## Sprint 112 — GUI Presentation & Data-Density Refinement

- Refined the scenario summary for one-, two- and three-scenario result sets with an explicit scenario count.
- Improved the projection table layout with responsive column stretching, minimum widths and both vertical and horizontal scrolling for wider/larger result sets.
- Preserved calculation-free presentation: the GUI continues to consume the existing immutable `ScenarioProjectionViewModel`.
- Kept existing keyboard, validation and pending/applied/saved state behaviour unchanged.
- Added 5 GUI presentation/data-density regression tests.
- Financial engines and retirement/tax/State Pension/ISA/savings/withdrawal calculations remain unchanged.

## Sprint 113 — GUI Scenario Comparison Visualisation

- Add a compact ending-pension comparison visualisation using the existing immutable `ScenarioProjectionViewModel` data contract.
- Support one-, two- and three-scenario result sets without moving calculations into the GUI.
- Scale the visualisation to the available window width and retain readable labels/values.
- Provide an explicit empty-state presentation when no scenario data is available.
- Preserve existing keyboard, validation and pending/applied/saved state behaviour.
- Keep headless/core planner workflows safe and avoid new external dependencies.
- Keep all retirement, tax, State Pension, ISA, savings and withdrawal calculations unchanged.

## Sprint 114 — GUI Chart Accessibility & Interaction

- Add an accessible textual description of the ending-pension comparison chart.
- Support keyboard navigation across one-, two- and three-scenario chart data.
- Surface the scenario under the pointer through the same accessible summary without recalculation.
- Keep chart presentation calculation-free and avoid new charting dependencies.
- Preserve existing keyboard, validation and pending/applied/saved state behaviour.
- Keep headless/core planner workflows safe and keep all retirement, tax, State Pension, ISA, savings and withdrawal calculations unchanged.

## Sprint 115 — GUI Final Integration Hardening

- Make desktop window construction idempotent and prevent duplicate control trees or keyboard bindings.
- Add safe, idempotent window close/lifecycle handling including the standard window-manager close action.
- Ensure projection, save, reload and refresh callbacks safely no-op after closure.
- Preserve validation, accessibility, chart and pending/applied/saved GUI state boundaries.
- Keep headless/core planner workflows safe and avoid new external dependencies.
- Keep all retirement, tax, State Pension, ISA, savings and withdrawal calculations unchanged.

## Sprint 116 — GUI Testability Infrastructure

- Introduce small injectable presentation seams for GUI dialogs so interactive error/success paths remain headless-testable.
- Provide a minimal dialog contract and recording test double without adding external dependencies.
- Preserve the controller/application/view-model boundaries and all pending/applied/saved state semantics.
- Keep financial calculations unchanged.

## Sprint 117 — GUI Event/State Abstraction

- Introduce a small injectable GUI event service for keyboard bindings and deferred idle callbacks.
- Keep Tkinter as the desktop adapter while allowing lifecycle/event behaviour to be exercised headlessly.
- Make deferred focus callbacks safe when the window has already closed.
- Preserve validation, accessibility, chart and pending/applied/saved state semantics.
- Keep financial calculations unchanged and avoid external dependencies.

## Sprint 121 — GUI Validation-Aware Workflow State

- Refined the immutable GUI workflow-state model so invalid pending edits are explicitly reported as requiring attention rather than appearing ready to run.
- Kept action availability unchanged: invalid pending edits still disable Run while retaining Reset and Reload.
- Added regression coverage for invalid-to-valid recovery, reset preservation and the desktop adapter's validation-aware status.
- Harden keyboard shortcut dispatch so disabled Run/Save/Reset actions cannot be bypassed by event callbacks.
- Add headless regression coverage for shortcut/action-state consistency while retaining the existing direct action validation behaviour.
- Preserved the existing controller/application/view-model and event/dialog seams.
- Financial engines and retirement/tax/State Pension/ISA/savings/withdrawal calculations remain unchanged.

## Sprint 120 — GUI Workflow-State Action Integration

- Route Run, Save, Reset and Reload button enabled/disabled states through the immutable workflow-state model.
- Ensure clean, pending-valid, pending-invalid and closed states expose consistent action availability in the desktop adapter.
- Preserve the existing validation, keyboard, event, dialog, persistence and pending/applied/saved semantics.
- Add headless regression coverage for GUI action-state integration without requiring a live Tk desktop.
- Keep financial engines and retirement/tax/State Pension/ISA/savings/withdrawal calculations unchanged and avoid external dependencies.

## Sprint 119 — GUI Workflow-State Model

- Formalise Run/Save/Reset/Reload state transitions independently of Tk widgets.
- Introduce a small immutable workflow-state model for pending, valid, dirty and closed conditions.
- Keep the desktop window as a presentation adapter consuming the workflow state.
- Add headless regression coverage for valid/invalid edits and reset/save/reload/close transitions.
- Preserve existing validation, accessibility, chart, event and persistence semantics.
- Keep financial calculations unchanged and avoid external dependencies.

## Sprint 118 — GUI Integration Regression Coverage

- Exercise the complete keyboard/event workflow through the injectable `GuiEventService` seam without requiring a live Tk desktop.
- Cover keyboard-driven run, validation failure, save, reset, reload and post-close no-op behaviour.
- Ensure injected dialogs are used consistently by reload/error paths so lifecycle tests remain headless.
- Keep event orchestration calculation-free and preserve controller/application/view-model boundaries.
- Keep financial calculations unchanged and avoid external dependencies.
## Sprint 126 — GUI Workflow-State Action Outcome Hardening

- Make the shared presentation action dispatcher authoritative for both action permission and post-action workflow-state synchronisation.
- Return a deterministic dispatch result so headless button/event adapters can distinguish blocked and executed actions without inspecting handlers.
- Recompute status and action availability after every permitted handler, including lightweight/test adapters that do not perform their own refresh.
- Preserve unknown-action rejection, validation, accessibility, persistence and lifecycle semantics.
- Keep all retirement, tax, State Pension, ISA, savings and withdrawal calculations unchanged and avoid external dependencies.
- Regression subset: **104 tests passing**.
- Full suite: **818 tests passing** (9 subtests).

## Sprint 125 — GUI Workflow-State Action Dispatch Hardening

- Centralise Run, Save, Reset and Reload presentation triggers behind one workflow-state action dispatcher.
- Expose a small named action-permission lookup on the immutable GUI workflow-state model to prevent button/event gating drift.
- Verify button and keyboard dispatch parity and reject unknown presentation actions deterministically.
- Preserve validation, accessibility, event, persistence and lifecycle semantics.
- Keep all retirement, tax, State Pension, ISA, savings and withdrawal calculations unchanged and avoid external dependencies.

## Sprint 124 — GUI Workflow-State Action Boundary Hardening

- Route Run, Save, Reset and Reload desktop button commands through explicit workflow-state gates before invoking their existing action handlers.
- Keep keyboard/event action gates aligned with button-driven actions so disabled workflow actions cannot be triggered through the presentation boundary.
- Preserve the existing direct action handlers and validation/error semantics for headless tests and internal orchestration.
- Add headless regression coverage for button action gating, clean/pending states and post-close no-op behaviour.
- Preserve the existing controller/application/view-model, validation, event and dialog seams.
- Keep all retirement, tax, State Pension, ISA, savings and withdrawal calculations unchanged and avoid external dependencies.
- Regression subset: **109 tests passing**.
- Full suite: **811 tests passing** (9 subtests).

## Sprint 123 — GUI Workflow-State Lifecycle Presentation Hardening

- Make window close a complete terminal workflow-state transition at the presentation layer.
- Explicitly resynchronise status text and Run/Save/Reset/Reload action availability when the window closes.
- Add headless regression coverage for terminal-state presentation synchronisation.
- Preserve the existing controller/application/view-model, validation, event and dialog seams.
- Keep all retirement, tax, State Pension, ISA, savings and withdrawal calculations unchanged and avoid external dependencies.
- Regression subset: **93 tests passing**.
- Full suite: **805 tests passing** (9 subtests).

## Sprint 122 — GUI Workflow-State Transition Hardening

- Keep Reset inputs as a complete workflow-state transition rather than only a control-value update.
- Explicitly resynchronise status text and Run/Save/Reset/Reload action availability after reset.
- Cover valid and invalid pending reset paths plus keyboard-driven reset state synchronisation with headless regression tests.
- Preserve the existing controller/application/view-model, validation, event and dialog seams.
- Keep all retirement, tax, State Pension, ISA, savings and withdrawal calculations unchanged and avoid external dependencies.
- Regression subset: **107 tests passing**.
- Full suite: **804 tests passing** (9 subtests).



## Sprint 127 — GUI Workflow-State Exception-Safe Action Dispatch Hardening

- Keep the shared presentation action dispatcher synchronised when an injected or unexpected action handler raises.
- Refresh workflow status/action availability in a `finally` boundary while preserving the original handler exception.
- Add headless regression coverage proving failed presentation handlers cannot leave stale workflow state behind.
- Preserve existing action permission, button/keyboard parity, validation, accessibility, persistence and lifecycle semantics.
- Keep all retirement, tax, State Pension, ISA, savings and withdrawal calculations unchanged and avoid external dependencies.
- Regression subset: **105 tests passing**.
- Full suite: **819 tests passing** (9 subtests).


## Sprint 128 — GUI Workflow-State Canonical Action Handler Hardening

- Centralise the canonical Run/Save/Reset/Reload presentation handler mapping so action gates cannot drift from their handlers.
- Route button and keyboard entry points through the action name only, removing duplicated action-to-handler pairings.
- Preserve the explicit handler injection seam used by headless boundary tests and retain exception-safe final workflow synchronisation.
- Add regression coverage for canonical handler mapping and button/event dispatch resolution.
- Keep all retirement, tax, State Pension, ISA, savings and withdrawal calculations unchanged and avoid external dependencies.


## Sprint 129 — GUI Workflow-State Canonical Action Vocabulary Hardening

- Define one canonical Run/Save/Reset/Reload action vocabulary shared by the immutable workflow state and presentation handler mapping.
- Expose the stable action vocabulary for headless integration tests without introducing Tk dependencies.
- Reject unknown actions deterministically without mutating workflow state.
- Preserve validation, accessibility, event, persistence and lifecycle semantics.
- Keep all retirement, tax, State Pension, ISA, savings and withdrawal calculations unchanged and avoid external dependencies.

## Sprint 130 — GUI Workflow-State Action Presentation Contract Hardening

- Expose an immutable action/permission snapshot from the Tk-free workflow-state model so presentation code can consume one canonical action contract.
- Derive the Run/Save/Reset/Reload button mapping from the shared `WORKFLOW_ACTIONS` vocabulary and render button states from the workflow-state action snapshot rather than duplicating per-action property references.
- Add headless regression coverage for canonical action-state ordering, button mapping and presentation rendering across the workflow contract.
- Preserve validation, accessibility, event, persistence and lifecycle semantics.
- Keep all retirement, tax, State Pension, ISA, savings and withdrawal calculations unchanged and avoid external dependencies.
- Regression subset: **125 tests passing**.
- Full suite: **827 tests passing** (9 subtests).


## Sprint 131 — GUI Workflow-State Canonical Permission Contract Hardening

- Make the immutable `action_states` snapshot the authoritative permission source for named workflow actions, removing duplicated action-to-property lookup logic.
- Preserve the shared `WORKFLOW_ACTIONS` vocabulary and stable action-state ordering consumed by the presentation adapter.
- Add headless regression coverage for snapshot/lookup parity and immutability.
- Preserve validation, accessibility, event, persistence and lifecycle semantics.
- Keep all retirement, tax, State Pension, ISA, savings and withdrawal calculations unchanged and avoid external dependencies.
- Regression subset: **127 tests passing**.
- Full suite: **829 tests passing** (9 subtests).

## Sprint 132 — GUI Workflow-State Canonical Action Descriptor Hardening

- Define one canonical presentation descriptor for Run, Save, Reset and Reload, pairing each workflow action with its existing handler and button attribute.
- Derive both the presentation handler map and button map from that shared descriptor so action wiring cannot drift between dispatch and control rendering.
- Add headless regression coverage for descriptor ordering and handler/button mapping parity.
- Preserve validation, accessibility, event, persistence and lifecycle semantics.
- Keep all retirement, tax, State Pension, ISA, savings and withdrawal calculations unchanged and avoid external dependencies.
- Regression subset: **129 tests passing**.
- Full suite: **831 tests passing** (9 subtests).

## Sprint 133 — GUI Workflow-State Immutable Action Descriptor Hardening

- Replace positional presentation action tuples with an immutable named descriptor so action, handler and button bindings cannot be confused by tuple position.
- Keep one canonical descriptor sequence aligned with the shared `WORKFLOW_ACTIONS` vocabulary and derive presentation mappings from it.
- Add headless regression coverage for descriptor immutability, named fields and canonical action uniqueness/order.
- Preserve validation, accessibility, event, persistence and lifecycle semantics.
- Keep all retirement, tax, State Pension, ISA, savings and withdrawal calculations unchanged and avoid external dependencies.


## Sprint 134 — GUI Workflow-State Action Descriptor Consistency Hardening

- Validate the immutable presentation action descriptor sequence against the canonical `WORKFLOW_ACTIONS` vocabulary before resolving live GUI bindings.
- Reject descriptor ordering or membership drift deterministically so presentation wiring cannot silently diverge from workflow-state permissions.
- Add headless regression coverage for descriptor-contract drift detection and canonical ordering preservation.
- Preserve validation, accessibility, event, persistence and lifecycle semantics.
- Keep all retirement, tax, State Pension, ISA, savings and withdrawal calculations unchanged and avoid external dependencies.
- Regression subset: **133 tests passing**.
- Full suite: **835 tests passing** (9 subtests).

## Sprint 135 — GUI Workflow-State Action Binding Consistency Hardening

- Validate immutable presentation descriptor handler and button bindings for uniqueness before resolving live GUI bindings.
- Reject missing or non-callable presentation bindings deterministically so descriptor edits cannot silently miswire workflow actions.
- Add headless regression coverage for duplicate handler/button bindings and missing binding detection.
- Preserve validation, accessibility, event, persistence and lifecycle semantics.
- Keep all retirement, tax, State Pension, ISA, savings and withdrawal calculations unchanged and avoid external dependencies.


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

- Represent resolved Run, Save, Reset and Reload presentation bindings as immutable named records rather than positional tuples.
- Derive button and handler lookup maps from the named runtime binding contract so presentation consumers cannot confuse binding positions.
- Add headless regression coverage for runtime binding immutability, named fields and canonical binding order.
- Preserve validation, accessibility, event, persistence and lifecycle semantics.
- Keep all retirement, tax, State Pension, ISA, savings and withdrawal calculations unchanged and avoid external dependencies.
- Regression subset: **142 tests passing**.
- Full suite: **844 tests passing** (9 subtests).

## Sprint 138 — GUI Workflow-State Immutable Action Binding Map Hardening

- Expose resolved workflow-action button and handler maps as immutable mapping views so presentation consumers cannot mutate canonical action wiring at runtime.
- Preserve the shared resolved `WorkflowActionBinding` contract as the sole source for both maps.
- Add headless regression coverage for immutability of the resolved button and handler maps.
- Preserve validation, accessibility, event, persistence and lifecycle semantics.
- Keep all retirement, tax, State Pension, ISA, savings and withdrawal calculations unchanged and avoid external dependencies.
- Regression subset: **144 tests passing**.
- Full suite: **846 tests passing** (9 subtests).


## Sprint 139 — GUI Workflow-State Canonical Action Binding Registry Hardening

- Centralize resolved Run, Save, Reset and Reload presentation bindings in one immutable action-keyed registry.
- Derive button rendering and handler dispatch maps from the shared resolved registry so each action is resolved from one runtime contract.
- Keep the registry aligned with the canonical `WORKFLOW_ACTIONS` vocabulary and preserve existing explicit-handler injection for boundary tests.
- Add headless regression coverage for registry immutability, map derivation and single-registry action-state rendering.
- Preserve validation, accessibility, event, persistence and lifecycle semantics.
- Keep all retirement, tax, State Pension, ISA, savings and withdrawal calculations unchanged and avoid external dependencies.
- Regression subset: **130 tests passing**.
- Full suite: **849 tests passing** (9 subtests).


## Sprint 140 — GUI Workflow-State Canonical Action Binding Registry Reuse Hardening

- Cache the resolved immutable Run, Save, Reset and Reload action-binding registry so presentation rendering and dispatch reuse one runtime contract rather than reconstructing bindings independently.
- Invalidate the registry when live GUI action controls are created, preserving the headless optional-button seam and preventing stale pre-build bindings.
- Add headless regression coverage for registry identity/reuse and shared cached consumption by button and handler maps.
- Preserve validation, accessibility, event, persistence and lifecycle semantics.
- Keep all retirement, tax, State Pension, ISA, savings and withdrawal calculations unchanged and avoid external dependencies.
- Regression subset: **132 tests passing**.
- Full suite: **851 tests passing** (9 subtests).

## Sprint 141 — GUI Workflow-State Cached Action Map Reuse Hardening

- Cache the immutable action button and handler maps derived from the shared resolved action-binding registry so repeated rendering and dispatch calls reuse the same map objects.
- Invalidate the derived maps alongside the binding registry when live GUI action controls are created, preventing stale pre-build presentation bindings.
- Add headless regression coverage for button-map and handler-map identity/reuse.
- Preserve validation, accessibility, event, persistence and lifecycle semantics.
- Keep all retirement, tax, State Pension, ISA, savings and withdrawal calculations unchanged and avoid external dependencies.
- GUI regression subset: **151 tests passing**.
- Full suite: **853 tests passing** (9 subtests).

## Sprint 142 — GUI Workflow-State Action Binding Cache Lifecycle Hardening

- Centralize invalidation of the cached workflow action-binding registry and its derived button and handler maps in one dedicated lifecycle helper.
- Use the helper when live GUI action controls are created so all cached presentation views are cleared together and cannot drift.
- Add headless regression coverage for atomic cache clearing, rebuild identity, consistency and idempotent invalidation.
- Preserve validation, accessibility, event, persistence and lifecycle semantics.
- Keep all retirement, tax, State Pension, ISA, savings and withdrawal calculations unchanged and avoid external dependencies.
- GUI regression subset: **154 tests passing**.
- Full suite: **856 tests passing** (9 subtests).

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
- Add headless regression coverage for closed-state refresh and dispatch non-rehydration.
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

- Harden the dependency between the cached workflow action registry and its derived button and handler maps so derived views cannot outlive an invalidated registry.
- Rebuild derived maps from the current live binding registry after registry invalidation while preserving immutable map semantics.
- Add headless regression coverage for button-map and handler-map rebuild after registry invalidation.
- Preserve validation, accessibility, event, persistence and lifecycle semantics.
- Keep all retirement, tax, State Pension, ISA, savings and withdrawal calculations unchanged and avoid external dependencies.
- GUI regression subset: **162 tests passing**.
- Full suite: **864 tests passing** (9 subtests).


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

- Harden the cached workflow action-binding registry against canonical key-set and binding-action drift before it can feed derived presentation maps.
- Automatically invalidate and rebuild the complete workflow-action cache when cached registry content is incoherent.
- Add headless regression coverage for registry key drift and binding-action drift.
- Preserve validation, accessibility, event, persistence and lifecycle semantics.
- Keep all retirement, tax, State Pension, ISA, savings and withdrawal calculations unchanged and avoid external dependencies.
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


## Sprint 152 — GUI Workflow-State Action Binding Derived Map Ordering Integrity Hardening

- Harden cached button and handler maps against canonical action-order drift while preserving their existing content/source coherence checks.
- Rebuild derived maps when their cached key order no longer matches `WORKFLOW_ACTIONS`.
- Add headless regression coverage for button-map and handler-map key-order drift.
- Preserve validation, accessibility, event, persistence and lifecycle semantics.
- Keep all retirement, tax, State Pension, ISA, savings and withdrawal calculations unchanged and avoid external dependencies.
- GUI regression subset: **175 tests passing**.
- Full suite: **877 tests passing** (9 subtests).


## Sprint 153 — GUI Workflow-State Action Binding Cache Dependency Invalidation Coverage Hardening

- Harden cache lifecycle coverage so rebuilding an incoherent workflow-action registry clears all dependent derived button and handler maps before they can be reused.
- Add headless regression coverage proving registry drift clears both derived caches and their source references before the derived views are rebuilt.
- Preserve validation, accessibility, event, persistence and lifecycle semantics.
- Keep all retirement, tax, State Pension, ISA, savings and withdrawal calculations unchanged and avoid external dependencies.
- GUI regression subset: **177 tests passing**.
- Full suite: **879 tests passing** (9 subtests).
## Sprint 154 - GUI Workflow-State Action Binding Derived Map Source Integrity Hardening

- Centralize the derived button/handler map coherence invariant so both cached views require an exact reference to the current resolved workflow-action registry, canonical action ordering, and matching entries.
- Add headless regression coverage for tampered derived-map source references and verify both maps rebuild against the live registry.
- Preserve validation, accessibility, event, persistence and lifecycle semantics.
- Keep all retirement, tax, State Pension, ISA, savings and withdrawal calculations unchanged and avoid external dependencies.
- GUI regression subset: **179 tests passing**.
- Full suite: **881 tests passing** (9 subtests).


## Sprint 155 — GUI Workflow-State Action Binding Cache Validation Defensive Hardening

- Harden cached workflow-action registry validation against mapping implementations that raise during key or value inspection, rebuilding from the canonical live presentation contract instead of leaking cache-validation failures.
- Harden derived button/handler map validation against malformed mapping implementations that raise during coherence checks.
- Add headless regression coverage for defensive cache validation and preserve the existing immutable cache lifecycle.
- Preserve validation, accessibility, event, persistence and lifecycle semantics.
- Keep all retirement, tax, State Pension, ISA, savings and withdrawal calculations unchanged and avoid external dependencies.
- GUI regression subset: **181 tests passing**.
- Full suite: **883 tests passing** (9 subtests).



## Sprint 156 — GUI Workflow-State Action Binding Derived Map Value Identity Hardening

- Harden cached button and handler maps so each derived entry must be the exact object supplied by the resolved immutable workflow-action registry, rather than merely comparing equal values.
- Add headless regression coverage for equal-but-distinct cached button and handler entries.
- Preserve validation, accessibility, event, persistence and lifecycle semantics.
- Keep all retirement, tax, State Pension, ISA, savings and withdrawal calculations unchanged and avoid external dependencies.
- GUI regression subset: **183 tests passing**.
- Full suite: **885 tests passing** (9 subtests).

## Sprint 157 — GUI Workflow-State Action Binding Registry Immutability Hardening

- Harden the cached workflow-action registry so only the immutable `MappingProxyType` representation is accepted as a valid cache.
- Rebuild the registry when a private cache replacement uses a mutable mapping, preventing post-validation mutation from crossing the cache boundary.
- Add headless regression coverage for mutable dictionary and mutable mapping registry replacements.
- Preserve validation, accessibility, event, persistence and lifecycle semantics.
- Keep all retirement, tax, State Pension, ISA, savings and withdrawal calculations unchanged and avoid external dependencies.
- GUI regression subset: **185 tests passing**.
- Full suite: **887 tests passing** (9 subtests).


## Sprint 158 — GUI Workflow-State Action Binding Cache Publication Integrity Hardening

- Harden workflow-action cache publication so immutable registry and derived maps are fully constructed before their cache fields are published.
- Clear the affected derived cache and source reference before reconstruction, preventing failed publication from leaving a partially rebuilt cache pair.
- Add two headless regression tests covering failed registry publication and failed button-map publication.
- Preserve validation, accessibility, event, persistence and lifecycle semantics.
- Keep all retirement, tax, State Pension, ISA, savings and withdrawal calculations unchanged and avoid external dependencies.
- GUI regression subset: **187 tests passing**.
- Full suite: **889 tests passing** (9 subtests).


## Sprint 159 — GUI Workflow-State Action Dispatch Boundary Hardening

- Harden the workflow-action dispatch boundary so only canonical string actions are accepted before presentation refresh or handler execution.
- Reject non-callable explicitly injected handlers before any workflow-state refresh, preserving deterministic dispatch behavior for isolated integration tests.
- Add headless regression coverage for invalid action types and invalid injected handlers.
- Preserve validation, accessibility, event, persistence and lifecycle semantics.
- Keep all retirement, tax, State Pension, ISA, savings and withdrawal calculations unchanged and avoid external dependencies.
- GUI regression subset: **189 tests passing**.
- Full suite: **891 tests passing** (9 subtests).


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

- Hardened the public button and keyboard entry points so handler exceptions propagate unchanged while the shared dispatch boundary still resynchronises workflow state.
- Added headless regression coverage for Run through both button and keyboard entry points when a presentation handler raises after changing an input.
- Preserved workflow-state gating, validation, accessibility, persistence and terminal lifecycle semantics.
- Kept all retirement, tax, State Pension, ISA, savings and withdrawal calculations unchanged and introduced no external dependencies.
- GUI regression subset: **197 tests passing**.
- Full suite: **899 tests passing** (9 subtests).

## Sprint 165 — GUI Workflow-State Keyboard Binding Idempotency Hardening

- Harden keyboard shortcut wiring so repeated binding attempts against the same event service are idempotent and cannot accumulate duplicate Tk callbacks.
- Preserve independent wiring when the event service instance changes, including injected headless adapters.
- Add headless regression coverage for same-service idempotency and service replacement rebinding.
- Preserve validation, accessibility, event, persistence and lifecycle semantics.
- Keep all retirement, tax, State Pension, ISA, savings and withdrawal calculations unchanged and avoid external dependencies.

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

- Add a single canonical keyboard-binding contract resolver so shortcut wiring validates event shape, canonical action membership, handler callability, duplicate event/action pairs and complete Run/Save/Reset/Reload action coverage before binding.
- Keep keyboard shortcut publication atomic by completing contract validation before any event-service binding is performed.
- Add headless regression coverage for complete workflow-action coverage and duplicate event/action contract rejection.
- Preserve keyboard binding idempotency, workflow-state gating, validation, accessibility, persistence and terminal lifecycle semantics.
- Keep all retirement, tax, State Pension, ISA, savings and withdrawal calculations unchanged and introduce no external dependencies.
- GUI regression subset: **205 tests passing**.
- Full suite: **907 tests passing** (9 subtests).

## Sprint 168 — GUI Workflow-State Integration Gardening Close-Out

- Finalised the GUI workflow/action integration hardening phase from the stable Sprint 167 checkpoint.
- Hardened keyboard shortcut publication so malformed canonical contracts fail before any event callback is published, covering unknown actions and non-callable handlers.
- Added two headless regression tests proving atomic keyboard-binding publication on invalid action and invalid-handler contracts.
- Confirmed canonical Run/Save/Reset/Reload button and keyboard paths remain aligned through the shared workflow-state dispatch boundary and terminal lifecycle protections.
- Preserved validation, accessibility, event, persistence and lifecycle semantics.
- Kept all retirement, tax, State Pension, ISA, savings and withdrawal calculations unchanged and introduced no external dependencies.
- GUI regression subset: **207 tests passing**.
- Full suite: **909 tests passing** (9 subtests).
- **GUI workflow/action integration gardening phase closed out at Sprint 168.**


## Sprint 169 — Documentation & Architecture Contract Consolidation

- Expand the practical architecture documentation after GUI workflow/action gardening closes out.
- Document change placement, stable contracts, GUI boundary rules, testing discipline and checkpoint/release practice.
- Keep documentation aligned with the engine-driven architecture without changing financial calculation behaviour.
- Add the developer architecture guide and link it from the project README.
- Preserve all retirement, tax, State Pension, ISA, savings and withdrawal calculations unchanged.
- Full suite checkpoint: **909 tests passing** (9 subtests).


## Sprint 170 — Public CLI Integration Coverage Consolidation

- Expanded end-to-end coverage for the public `compare.py` entry point using a clean project copy and the real ScenarioEngine/ComparisonReport pipeline.
- Verified successful completion, both canonical withdrawal strategies, and the published comparison-report columns.
- Added two headless integration tests covering the public CLI output contract.
- Preserved the engine-driven architecture and existing calculation behaviour; no retirement, tax, State Pension, ISA, savings or withdrawal calculations changed.
- GUI regression subset: **207 tests passing**.
- Full suite: **911 tests passing** (9 subtests).

## Sprint 171 — Flexible GUI Assumption Editing

The GUI now supports complete `assumptions.json` editing through a validation-aware advanced editor, while retaining the simplified primary projection fields. Changes are applied atomically in memory and may be explicitly persisted with Apply & Save. No calculation engine changes were made.

## Sprint 172 — GUI Assumptions Change Tracking & Safe Discard

- Extended the flexible assumptions editor with deterministic change-path reporting and visible unsaved-change feedback.
- Added an explicit Discard changes action that restores the last persisted validated baseline atomically.
- Preserved explicit Save semantics and the engine-driven financial calculation boundary.
- Added four regression tests covering nested change paths, discard restoration, atomic failure handling and post-save clean state.
- GUI/controller targeted regression: **216 tests passing** (3 subtests).
- Full suite: **919 tests passing** (9 subtests).
- Kept all retirement, tax, State Pension, ISA, savings and withdrawal calculations unchanged.


## Sprint 173 — GUI Assumptions Editor Validation & Formatting Workflow

- Added a non-mutating assumptions-document validation path for the advanced GUI editor.
- Added canonical JSON formatting that validates before replacing the editor text.
- Added Validate and Format editor actions while retaining explicit Apply, Apply & Save, Reload and Discard controls.
- Added three regression tests covering validation immutability, canonical formatting and invalid-document rejection.
- Preserved explicit persistence semantics and all retirement, tax, State Pension, ISA, savings and withdrawal calculations unchanged.
- GUI/controller targeted regression: **218 tests passing**.
- Full suite: **922 tests passing** (9 subtests).

## Sprint 174 — GUI Assumptions Saved-File Reload Safety

- Hardened the flexible assumptions editor's saved-file reload boundary so invalid or unvalidated on-disk assumptions cannot partially replace the active in-memory configuration.
- Preserved both the active assumptions document and the persisted baseline when JSON parsing or domain validation fails during reload.
- Added two regression tests covering invalid JSON and validation-failing saved documents.
- Preserved explicit Apply/Save/Discard semantics and all retirement, tax, State Pension, ISA, savings and withdrawal calculations unchanged.
- GUI/controller targeted regression: **238 tests passing** (3 subtests).
- Full suite: **924 tests passing** (9 subtests).

## Sprint 175 — GUI Assumptions Editor Safe-Close Hardening

- Protect unapplied assumptions-editor text from silent loss when the advanced editor is closed.
- Treat malformed editor text as pending work and require explicit confirmation before discarding it.
- Keep the flexible assumptions JSON workflow atomic and preserve explicit Apply/Save semantics.
- Add headless regression coverage for clean, changed and invalid editor-text close states.
- Preserve all retirement, tax, State Pension, ISA, savings and withdrawal calculations unchanged.
- GUI regression subset: **207 tests passing**.
- Full suite: **928 tests passing** (9 subtests).

## Sprint 176 — GUI Assumptions Editor Dirty-State Synchronisation

- Distinguish unapplied editor text from active in-memory changes and persisted state.
- Refresh editor dirty-state presentation automatically after user edits while keeping programmatic document replacement clean.
- Preserve close protection and explicit Apply/Save/Discard semantics.
- Add regression coverage for the dirty-state contract.
- Preserve all retirement, tax, State Pension, ISA, savings and withdrawal calculations unchanged.
- GUI regression checkpoint: **230 tests passing** (3 subtests).
- Full suite checkpoint: **934 tests passing** (9 subtests).

## Sprint 177 - GUI Flexible Assumptions to Projection End-to-End Integration
- Proved that assumptions edited through the flexible GUI document are consumed by the real scenario projection pipeline.
- Added regression coverage for primary `starting_pension`, non-primary `starting_savings`, and nested goal round-trip behaviour.
- Confirmed nested assumption edits remain calculation-neutral when the edited value is presentation/audit configuration only.
- No financial calculation engine logic changed.

## Sprint 178 - GUI Flexible Assumptions Projection Coverage Consolidation

Consolidate end-to-end proof that broader GUI-editable assumptions reach the real projection pipeline and survive persistence/reload without calculation-engine changes.

- Withdrawal strategy propagation covered.
- Starting ISA propagation covered.
- Spending/inflation linkage propagation covered.
- Save/reload projection equivalence covered.

## Sprint 178 - GUI Flexible Assumptions Projection Coverage Consolidation

Extend end-to-end coverage so broader GUI-editable assumptions demonstrably reach the real projection pipeline and survive persistence/reload unchanged.

- Covered withdrawal strategy propagation.
- Covered starting ISA propagation at the real timeline level.
- Covered spending-phase and inflation-linkage propagation.
- Covered save/reload projection equivalence.
- No financial calculation engine changes.

## Sprint 179 — GUI Flexible Assumptions Scenario Integrity

- Extend the GUI flexible-assumptions proof from individual fields to coherent multi-field scenario edits.
- Verify a single edited assumptions document can drive all three scenarios without cross-field state drift.
- Verify Save/Reload preserves the complete edited document and reproduces the projection result.
- Add regression coverage while preserving the engine-driven calculation boundary.
- Full suite checkpoint: **944 tests passing** (9 subtests).

## Sprint 180 — GUI Projection Result Freshness Contract

- Added a calculation-free GUI freshness contract that distinguishes current projection results from stale results after editable input or assumption changes.
- Result freshness now includes the applied scenario selection and complete assumptions document, preventing stale scenario cards/charts from being presented as current.
- Successful Run and Reload operations publish a new result signature; pending control changes and flexible assumptions edits mark the displayed projection stale until re-run.
- Added four regression tests covering initial current state, stale projection controls, assumption-driven staleness and successful re-run freshness restoration.
- Preserved the existing projection calculation engine and all retirement, tax, State Pension, ISA, savings and withdrawal calculations unchanged.
- GUI/controller integration regression: **220 tests passing**.
- Full suite: **948 tests passing** (9 subtests).


## Sprint 181 — GUI Projection Result Export Contract Consolidation

- Added a calculation-free report snapshot contract to `ScenarioProjectionViewModel` for GUI/report consumers.
- Added GUI result-report accessors that refuse export/report retrieval while projection results are stale.
- Added regression coverage proving report payload/text match the displayed view model and stale results cannot be exported.
- Preserved the existing projection calculation engine and all retirement, tax, State Pension, ISA, savings and withdrawal calculations unchanged.
- GUI/integration regression: **207 tests passing**.
- Full suite: **951 tests passing** (9 subtests).

## Sprint 182 — GUI Projection Result Snapshot Integrity

- Consolidate the current-result presentation contract around one immutable published snapshot.
- Reuse the exact snapshot for repeated report/export access.
- Prevent nested mutation of report data from affecting future consumers.
- Publish a new snapshot only after a successful projection/reload result is established.
- Preserve the calculation-free GUI/report boundary and all financial calculation logic.
- Full suite checkpoint: **954 tests passing** (9 subtests).


## Sprint 183 - GUI Projection Result Snapshot Lifecycle Hardening

Finalised the lifecycle boundary around the immutable projection-result snapshot. A closed GUI instance now releases its retained snapshot and refuses report/export access, preventing terminal presentations from retaining or exposing stale result data. Two regression tests were added. No financial calculation logic changed. Validation: 235 targeted tests passed; 956 full-suite tests passed with 9 subtests.


## Sprint 184 — GUI Projection Result Snapshot Consumer Contract Consolidation

- Expose one public immutable current-result snapshot contract for downstream GUI, report and export consumers.
- Keep legacy payload/text accessors as compatibility projections of the same snapshot.
- Preserve stale/closed result guards at the shared consumer boundary.
- Add regression coverage without changing any financial calculation engine.
- Full suite checkpoint: **958 tests passing** (9 subtests).

## Sprint 185 — GUI Projection Result Snapshot → Report Contract Integration

- Integrate the immutable GUI result snapshot with the existing report layer without recalculating or reconstructing the projection.
- Add snapshot-backed report payload, text and year-row consumers with structural validation.
- Preserve stale/closed result protections at the GUI boundary.
- Add regression coverage without changing financial calculation engines.
- Full suite checkpoint: **962 tests passing** (9 subtests).

## Sprint 186 — GUI Projection Result Snapshot File Export Integration

- Extend the immutable current-result snapshot into calculation-free JSON and text file exports.
- Keep stale/closed result protections at the shared consumer boundary.
- Stage export writes through a temporary file before replacement so exports cannot publish partial content.
- Add regression coverage without changing financial calculation engines.
- Full suite checkpoint: **965 tests passing** (9 subtests).

## Sprint 187 — GUI Projection Result Snapshot Export Atomicity Hardening

- Harden the shared JSON/text export boundary against temporary-file collisions and failed publication.
- Ensure failed export publication cannot leave stale temporary files or replace an existing destination.
- Add regression coverage while preserving the immutable current-result snapshot and calculation engines.
- Full suite checkpoint: **967 tests passing** (9 subtests).

## Sprint 188 — GUI Projection Result Snapshot Export Bundle Contract

- Extend the current-result snapshot export surface with one bundle operation for JSON and text companions.
- Resolve the immutable snapshot once and ensure both outputs represent exactly the same projection result.
- Validate bundle filename stems before any output is created.
- Reuse the existing atomic publication boundary and preserve all financial calculation logic.
- Full suite checkpoint: **969 tests passing** (9 subtests).

## Sprint 189 — GUI Projection Result Snapshot Export Bundle Overwrite Safety

- Add explicit overwrite protection to the JSON/text export bundle.
- Support intentional replacement through `overwrite=True` using recoverable two-file publication with rollback.
- Ensure failed publication leaves existing destinations unchanged and removes all temporary/backup artefacts.
- Add regression coverage without changing financial calculation engines.
- Full suite checkpoint: **972 tests passing** (9 subtests).


## Sprint 190 — Public CLI Flexible Assumptions Integration

- Extend the flexible assumptions architecture beyond the GUI into supported public CLI entry points.
- Add `--assumptions PATH` support to the main planner and strategy comparison workflows.
- Preserve a supplied validated assumptions document as the scenario baseline before applying scenario-specific overrides.
- Add end-to-end regression coverage without changing financial calculation logic.
- Full suite checkpoint: **975 tests passing** (9 subtests).

## Sprint 191 — Unified Projection → Report → Export Workflow

- Consolidate the projection/report/export hand-off into one reusable application workflow result.
- Ensure one projection run publishes one immutable report snapshot that can feed all report/export consumers without recalculation.
- Reuse one shared calculation-free JSON/text bundle publication boundary across GUI and public CLI surfaces.
- Add a public scenario-report CLI with validated assumptions-file support and explicit export/overwrite controls.
- Add end-to-end regression coverage while preserving all financial calculation engines unchanged.
- Full suite checkpoint: **978 tests passing** (9 subtests).

## Sprint 192 — GUI Adoption of the Unified Projection → Report Workflow

- Extend the Sprint 191 application workflow boundary into the GUI controller so GUI runs publish the same `ScenarioProjectionWorkflowResult` used by public reporting consumers.
- Carry the validated GUI inputs, view model, immutable report snapshot, report payload and report text together in the controller run result.
- Update GUI Run and Reload paths to consume the already-published workflow snapshot rather than constructing a second presentation snapshot.
- Preserve failed-run rollback of in-memory assumptions and all existing GUI workflow-state behaviour.
- Add regression coverage for shared workflow-result identity/content and failed-workflow restoration.
- Preserve all retirement, tax, State Pension, ISA, savings, withdrawal and projection calculation logic unchanged.
- Focused Sprint 192 regression: **247 passed, 3 subtests**.
- Full suite: **981 passed, 9 subtests**.
- Compile check: passed.

**Current checkpoint: Sprint 192 — 981 tests passing.**

## Sprint 193 — Unified Workflow Result Integrity

- Hardened `ScenarioProjectionWorkflowResult` so its report payload is recursively immutable while preserving the existing dict/list public shape.
- Added construction-time consistency checks ensuring the published report payload and report text exactly match the immutable report snapshot.
- Prevented consumer mutation from changing a retained workflow result, without introducing recalculation or changing the projection/report data contract.
- Added three regression tests covering recursive immutability, payload/text drift rejection and repeated snapshot parity.
- Preserved all retirement, tax, State Pension, ISA, savings, withdrawal and projection calculation logic unchanged.
- Focused Sprint 193 regression: **281 passed, 3 subtests**.
- Full suite: **984 passed, 9 subtests**.
- Compile check: passed.

**Current checkpoint: Sprint 193 — 984 tests passing.**

## Sprint 194 — Unified Workflow Result Export Boundary

- Promote the published `ScenarioProjectionWorkflowResult` to the sole report/export consumer boundary.
- Add direct JSON/text bundle export from the published result without recalculation or snapshot reconstruction.
- Keep the application-level export helper as a compatibility delegation layer.
- Update the public scenario-report CLI to consume the result boundary directly.
- Add regression coverage for direct export and preserve transactional conflict/overwrite behaviour.
- Preserve all retirement, tax, State Pension, ISA, savings, withdrawal and projection calculation logic unchanged.
- Full suite checkpoint: **987 tests passing** (9 subtests).

**Current checkpoint: Sprint 194 — 987 tests passing.**

## Sprint 195 — GUI-Neutral Projection Workflow Boundary

- Move the reusable `ScenarioProjectionApplication`, `ScenarioProjectionInputs` and `ScenarioProjectionWorkflowResult` contracts from the GUI package into `planner/projection/scenario_projection_workflow.py`.
- Keep `planner.gui.scenario_projection_application` as a compatibility import surface so existing GUI callers and tests do not break.
- Update the public scenario-report CLI and GUI controller/window to depend on the GUI-neutral workflow module rather than importing orchestration from the presentation package.
- Preserve the immutable workflow-result, report and export contracts introduced in Sprints 191–194.
- Add three regression tests proving the neutral module owns the canonical types and that compatibility imports resolve to the exact same classes.
- Preserve all retirement, tax, State Pension, ISA, savings, withdrawal and projection calculation logic unchanged.
- Full suite: **990 passed, 9 subtests**.

**Current checkpoint: Sprint 195 — 990 tests passing.**

## Sprint 196 — Public Projection Workflow API Surface

- Added the package-level `planner.projection` public API for `ScenarioProjectionApplication`, `ScenarioProjectionInputs` and `ScenarioProjectionWorkflowResult`.
- Updated first-party CLI and GUI surfaces to import the canonical workflow contracts from the package-level API rather than the implementation module.
- Preserved `planner.projection.scenario_projection_workflow` as the canonical implementation module and `planner.gui.scenario_projection_application` as a compatibility import surface.
- Added three regression tests covering package exports, GUI-independent type ownership and first-party consumer adoption.
- Preserved all retirement, tax, State Pension, ISA, savings, withdrawal and projection calculation logic unchanged.
- Public workflow/API regression: **12 passed** across Sprints 193–196.
- GUI/application/report/export regression: **298 passed, 3 subtests**.
- Full suite: **993 passed, 9 subtests**.
- Compile check: passed.

**Current checkpoint: Sprint 196 — 993 tests passing.**

## Sprint 197 — Professional Scenario Projection PDF Report

- Added `ScenarioProjectionPDFReport` as a calculation-free PDF presentation of the unified `ScenarioProjectionWorkflowResult`.
- The report includes published inputs, scenario summary, outcome range, existing report text, scenario detail and year-by-year projection rows from the same immutable workflow payload.
- Extended the public `scenario_report.py` CLI with `--pdf PATH`, using the already-published workflow result and performing no recalculation.
- Added three regression tests covering PDF creation, published-content parity and type validation.
- Preserved all retirement, tax, State Pension, ISA, savings, withdrawal and projection calculation logic unchanged.
- Focused Sprint 197 regression: **18 passed**.
- Full suite: **996 passed, 9 subtests**.
- Compile check: passed.

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

- Add a calculation-free PDF presentation for the existing `ScenarioEngine.compare_strategies()` results.
- Render the already-computed pension-first and ISA-first strategy results without recalculating or mutating them.
- Add `compare.py --pdf PATH` using the same precomputed result objects already used by the console comparison report.
- Include summary/detail tables, ending-assets and lifetime-tax vector charts, page chrome and report provenance.
- Preserve the existing console comparison output and public assumptions-file support.
- Add regression tests for PDF content parity, no-recalculation result preservation, CLI PDF export and invalid-input rejection.
- Preserve all retirement, tax, State Pension, ISA, savings, withdrawal and projection calculation logic unchanged.

- Sprint 199 focused regression: **4 passed**.
- Strategy comparison CLI regression: **3 passed**.
- Full suite checkpoint: **1003 tests passing** (9 subtests).


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

- Add a calculation-free PDF presentation for the existing retirement health dashboard, using the already-computed health, recommendation, Monte Carlo and projection-summary objects.
- Add an executive dashboard showing health score/rating, success probability, recommended strategy and confidence.
- Add projected-position and Monte Carlo outcome-range tables plus vector visualisations of the health score and ending-assets percentile landmarks.
- Extend `health_check.py` with `--pdf PATH`; the PDF export consumes the same results already computed for the console health check and performs no second calculation.
- Add three regression tests covering PDF content, non-mutation of supplied data and CLI PDF export.
- Preserve all retirement, tax, State Pension, ISA, savings, withdrawal and projection calculation logic unchanged.
- Focused Sprint 201 regression: **18 passed** across the health report and recent professional PDF report suite.
- Full collected suite: **1011 tests**; the aggregate runner remains intermittently timeout-prone around subprocess-heavy CLI tests, so the accepted checkpoint uses completed partitioned validation.

**Current checkpoint: Sprint 201 — 1011 tests passing.**

## Sprint 202 — Professional Retirement Goals PDF Report

- Extend the professional PDF reporting programme to the existing retirement-goal evaluation output.
- Present goal achievement status, target versus actual values and an executive achieved-goals summary without recalculation.
- Add vector status visualisation, page chrome and provenance consistent with the scenario, comparison, recommendation and health PDF reports.
- Expose goal-report PDF export from the existing `health_check.py` workflow while reusing the already-evaluated goal objects.
- Add regression coverage for content parity, source-data preservation and CLI PDF export.
- Preserve all retirement, tax, State Pension, ISA, savings, withdrawal and projection calculation logic unchanged.
- Full suite checkpoint: **1014 tests passing** (9 subtests).

**Current checkpoint: Sprint 202 — 1014 tests passing.**

## Sprint 203 — GUI Professional PDF Report Suite Integration

- Added `planner.reporting.report_suite.export_report_suite()` as the GUI-neutral orchestration boundary for the five professional PDF reports.
- Added `ReportSuiteExportResult` with predictable output paths for scenario projection, strategy comparison, recommendation, health check and retirement goals PDFs.
- Added an `Export PDF reports…` action to the scenario projection GUI that exports the complete professional report suite to a user-selected folder.
- The GUI action reuses the current published `ScenarioProjectionWorkflowResult` without recalculating the displayed projection; recommendation, comparison, health-check and goal reports reuse their existing domain/report boundaries against the current in-memory assumptions.
- Added injectable directory-selection and report-export seams for headless GUI testing and stale-result protection before export.
- Added three regression tests covering reuse of the current workflow result, stale-result blocking and report-button state.
- Preserved all retirement, tax, State Pension, ISA, savings, withdrawal and projection calculation logic unchanged.
- Full suite: **1017 passed, 9 subtests**.
- Compile check: passed.
- Real report-suite smoke export: all five PDFs created successfully.

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

- Added `reports.professional_report_pack.ProfessionalReportPackPDFReport` to compose the five already-generated professional PDFs into one navigable document.
- Added a cover/index page showing the five included report sections and their page counts.
- Added PDF outline/bookmarks for Scenario Projection, Strategy Comparison, Recommendation, Health Check and Retirement Goals.
- Added `planner.reporting.report_pack.export_report_pack()` and `report_pack.py --directory PATH --pdf PATH` for calculation-free pack composition from an existing report suite.
- The pack preserves every source PDF byte-for-byte and performs no retirement-financial recalculation.
- Added safe default collision protection and atomic temporary-file publication with explicit `--overwrite` support.
- Declared `pypdf` under the optional `reports` dependency because the pack composer merges PDF files at runtime.
- Added three regression tests covering bookmarks/page composition, source preservation and safe overwrite behaviour.
- Preserved all retirement, tax, State Pension, ISA, savings, withdrawal and projection calculation logic unchanged.
- Sprint 205 focused regression: **9 passed** including prior report-suite/GUI publication safety.
- Full suite: **1023 passed, 9 subtests**.
- Compile check: passed.
- Real consolidated-pack CLI smoke test: passed; 16-page bookmarked PDF created.

**Current checkpoint: Sprint 205 — 1023 tests passing.**

## Sprint 206 — GUI Consolidated Professional Report Pack Integration

- Add an `Export PDF report pack…` action to the scenario projection GUI.
- Reuse the current published projection workflow result for the scenario report without recalculation.
- Export the five professional PDFs and compose a consolidated `RetirementPlanner_Report_Pack.pdf` from the same GUI-selected destination.
- Protect an existing consolidated pack before generating the underlying suite so the GUI action remains safe by default.
- Keep suite/pack exporters injectable for headless regression tests.
- Add three regression tests for workflow-result reuse, collision preflight and action-state behaviour.
- Preserve all retirement, tax, State Pension, ISA, savings, withdrawal and projection calculation logic unchanged.
- Sprint 206 focused regression: **9 passed**.
- Full suite checkpoint: **1026 tests passing** (9 subtests).

**Current checkpoint: Sprint 206 — 1026 tests passing.**

## Sprint 207 — Tax-Free Pension Percentage Calculation Wiring

- Make the schema-defined `tax_free_pension_percentage` assumption drive the live pension tax-free cash allowance instead of relying on an implicit 25% constant.
- Wire the same configured percentage into `TaxEngine`'s gross-up calculation and track the remaining tax-free allowance during the live tax pass.
- Preserve the legacy `tax_free_cash_percentage` lookup as a compatibility fallback for older callers.
- Add validation requiring `tax_free_pension_percentage` to remain between 0 and 1.
- Add regression coverage proving the assumption changes the actual tax-free allowance, the tax engine, and the end-to-end projection result.
- Refresh the golden baseline because the corrected assumption is now financially operative; this is an intentional behavioural correction, not a cosmetic test update.
- Leave all other assumptions and the reporting layer unchanged for this sprint.

- Sprint 207 focused regression: **37 passed**.
- Full suite: **1030 passed, 9 subtests**.
- Compile check: passed.

**Current checkpoint: Sprint 207 — 1030 tests passing.**

## Sprint 208 — Maximum Pension Income Calculation Wiring

- Make the schema-defined `max_pension_income` assumption an operational annual net pension-income ceiling in `StrategyEngine`.
- Bound both tax-efficient and additional pension allocations by the configured ceiling for `PENSION_FIRST`, `ISA_FIRST`, and their existing fallback strategies.
- Route any spending need above the pension ceiling to ISA, then record any remaining unmet amount as `income_shortfall` so the completed plan can report failure rather than silently exceeding the configured pension limit.
- Validate `max_pension_income` as a non-negative financial assumption.
- Add regression coverage for pension capping, ISA spillover, exhausted-asset shortfall, end-to-end projection impact and invalid values.
- Refresh the golden scenario because the default £30,000 ceiling is now financially operative; this is an intentional behavioural correction, not a cosmetic test update.
- Keep the reporting layer unchanged and continue the assumptions-calculation coverage programme.

- Sprint 208 focused regression: **24 passed**.
- Full collected suite: **1034 tests passed, 9 subtests**, validated in completed partitions (811 non-GUI/CLI + 214 GUI + 9 CLI).
- Compile check: passed.

**Current checkpoint: Sprint 208 — 1034 tests passing.**

## Sprint 209 — Investment Return and Charges Calculation Wiring

- Added `planner.investment_return.InvestmentReturnResolver` as the calculation boundary for gross investment return and configured platform/fund charges.
- `expected_investment_return` is now the canonical gross deterministic projection return; `expected_return` remains the Monte Carlo mean-return assumption.
- Normal pension projection growth now uses net deterministic return: `expected_investment_return - platform_charge - fund_charge`.
- Monte Carlo draws now use net `expected_return` after the same configured charges, while preserving the existing seeded random-draw behaviour.
- `pension_growth` remains a legacy fallback for older callers and sensitivity cases; the sensitivity runner now translates its net growth cases into the canonical gross return assumption while preserving historical sensitivity semantics.
- Added validation for non-negative platform/fund charges, individual charges below 100%, and combined charges below 100%.
- Added seven regression tests proving the configured gross return and each charge affect the real projection, Monte Carlo net mean is resolved correctly, and invalid charges are rejected.
- Regenerated the golden projection baseline because the previously ignored investment return/charge assumptions now change live calculation outputs.
- Restored the top-level `reports/` package and legacy `create_report.py` entry point into the checkpoint source tree so the Sprint 209 archive is self-contained for the complete test suite.
- Preserved all reporting presentation logic; no unrelated calculation domains were changed.
- Sprint 209 focused regression: **7 passed**.
- Full suite: **1041 passed, 9 subtests**.
- Compile check: passed.

**Current checkpoint: Sprint 209 — 1041 tests passing.**


## Sprint 210 — Property Sale and Annual ISA Allowance Calculation Wiring

- Activate `property_sale` as a one-off asset event at `property_sale_age`.
- Apply `annual_isa_allowance` to the share of property proceeds sheltered into the ISA.
- Preserve overflow proceeds in savings so the existing asset roll-forward remains internally consistent.
- Add assumption-impact regression coverage and validation.
- Keep reporting frozen while assumptions calculation coverage is prioritised.

## Sprint 211 — Inflation Calculation Wiring

- Activate `InflationEngine` in the live `RetirementPlanner` engine sequence before property-sale, savings, ISA and cash-flow calculations.
- Make the schema-defined `inflation_rate` assumption operational for every projected retirement year by materialising compounded `inflation_factor` values on the live timeline.
- This makes the existing `inflation_link_spending` behaviour use real compounded inflation rather than the previous default factor of `1.0` throughout the planner path.
- Preserve the standalone `InflationEngine` contract and all retirement, tax, State Pension, ISA, savings, withdrawal, investment-return/charge and property-sale calculation logic outside this newly activated engine boundary.
- Add five regression tests covering compounded factors, live planner integration, enabled/disabled spending linkage and end-to-end projection impact.
- Refresh the golden projection baseline because the previously dormant live inflation boundary now changes projection outputs; this is an intentional behavioural correction, not a cosmetic test update.
- Update the recommendation PDF pagination regression to reflect the changed live projection/recommendation content while retaining the three-page presentation contract.

- Sprint 211 focused regression: **5 passed**.
- Full suite: **1050 passed, 9 subtests**.
- Compile check: passed.

**Current checkpoint: Sprint 211 — 1050 tests passing.**

## Sprint 212 — Inflation-Linked Tax Calculation Wiring

- Activate `inflation_link_tax` in the live `TaxEngine` calculation boundary.
- Scale `personal_allowance` and `basic_rate_limit` by the already-materialised per-year `inflation_factor` when the setting is enabled.
- Preserve configured nominal tax thresholds when the setting is disabled, with the first projection year remaining unchanged under either mode.
- Add regression coverage for direct tax-engine behaviour and end-to-end projection impact.
- Refresh the golden projection baseline because the default inflation-linked tax behaviour changes later-year outputs.
- Preserve all other financial calculation and reporting logic unchanged.

- Sprint 212 focused regression: **7 passed**.
- Full suite: **1057 passed, 9 subtests**.
- Compile check: passed.

**Current checkpoint: Sprint 212 — 1057 tests passing.**


## Sprint 213 — Inflation-Linked ISA Calculation Wiring

- Activate `inflation_link_isa` in the live property-sale/ISA allowance calculation boundary.
- Scale the configured `annual_isa_allowance` by the already-materialised per-year `inflation_factor` when the setting is enabled.
- Preserve the configured nominal ISA allowance when the setting is disabled, with the first projection year remaining unchanged under either mode.
- Cap the inflation-adjusted allowance at the actual property-sale proceeds so the one-off sale event remains internally consistent.
- Add regression coverage for direct property-sale behaviour and end-to-end projection impact.
- Refresh the golden projection baseline because the default inflation-linked ISA behaviour changes the property-sale split and later-year ISA/savings balances.
- Preserve all other financial calculation and reporting logic unchanged.

- Sprint 213 focused regression: **6 passed**.
- Full suite: **1063 passed, 9 subtests**.
- Compile check: passed.

**Current checkpoint: Sprint 213 — 1063 tests passing.**

## Sprint 214 — ISA Allowance Schedule Boundary

- Add an explicit tax-year-based `isa_allowance_schedule` for future statutory ISA allowance changes without changing the existing nominal default.
- Add `isa_allowance_schedule_enabled` as the explicit activation control; the default remains disabled so the current configured `annual_isa_allowance` behaviour is preserved.
- Resolve the latest scheduled allowance at or before the projection calendar year, with the configured annual allowance used before the first scheduled tax year.
- Keep `inflation_link_isa` as a separate planning layer: when both features are enabled, inflation is applied to the scheduled allowance rather than replacing the schedule.
- Add schema/domain validation for `YYYY/YY` tax-year keys and non-negative finite allowances.
- Add regression coverage for schedule activation, future transition timing, disabled behaviour, inflation interaction and invalid schedules.
- Preserve all pension, tax, State Pension, savings, withdrawal, investment-return/charge, property-sale and reporting logic outside this ISA allowance boundary.

- Sprint 214 focused regression: **9 passed**.
- Full suite: **1072 tests passed, 9 subtests**.
- Compile check: passed.

**Current checkpoint: Sprint 214 — 1072 tests passing.**

## Sprint 215 — Inflation Forecast and State Pension Triple-Lock Wiring

- Wire the existing inflation forecast into the State Pension growth boundary alongside a configurable earnings-growth forecast and 2.5% floor.
- Add an explicit `state_pension_triple_lock_enabled` control while retaining the existing fixed `state_pension_growth` path when disabled.
- Ensure the resulting State Pension values flow into the existing `required_pension_income` calculation while inflation-linked spending remains driven by the compounded `inflation_factor`.
- Add direct and end-to-end regression coverage for the three triple-lock branches, compatibility mode, spouse progression and pension income required.
- Refresh the golden projection baseline because the newly active State Pension calculation intentionally changes projection outputs.
- Preserve all other financial calculation and reporting logic.

- Sprint 215 focused regression: **6 passed**.
- Full suite: **1078 passed, 9 subtests**.
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

- Add an opt-in `annual_spending_schedule` keyed by calendar year so future spending can be modelled explicitly year by year without replacing the existing age-based spending phases.
- Add `annual_spending_schedule_enabled`, defaulting to disabled so the existing `spending_phase_1/2/3` behaviour remains unchanged.
- When enabled, a matching calendar-year schedule value overrides the age-based phase amount for that year; missing schedule years fall back to the existing phase logic.
- Keep `inflation_link_spending` as a separate layer so scheduled values are nominal planning amounts before the existing compounded inflation factor is applied.
- Add schema/domain validation and audit-catalog coverage for the new schedule settings.
- Add six focused regression tests covering schedule activation, annual transitions, phase fallback, disabled compatibility, inflation interaction and invalid schedules.
- Preserve all other financial calculation and reporting logic.
- Sprint 218 focused regression: **6 passed**.
- Full suite: **1096 passed, 9 subtests**.
- Compile check: passed.

**Current checkpoint: Sprint 218 — 1096 tests passing.**

## Sprint 219 — Annual Investment and ISA Return Schedules

- Added opt-in `investment_return_schedule` keyed by calendar year, overriding the canonical gross deterministic investment return for matching years while preserving the existing charge boundary.
- Added opt-in `isa_return_schedule` keyed by calendar year, overriding the ISA growth assumption for matching years.
- Added `investment_return_schedule_enabled` and `isa_return_schedule_enabled`, both disabled by default for compatibility.
- Missing schedule years fall back to the existing base assumptions.
- Added structural validation for annual return schedules and audit-catalog coverage.
- Added eight focused Sprint 219 regression tests covering investment schedule activation, fallback and disabled compatibility; ISA schedule activation, annual transitions, fallback and disabled compatibility; and invalid schedule rejection.
- Preserved all existing retirement, State Pension, spending, inflation, tax, ISA allowance, savings, withdrawal, property-sale, Monte Carlo and reporting calculation boundaries.
- Sprint 219 focused regression: **8 passed**.
- Full suite: **1104 tests passed, 9 subtests** (executed in four parallel test batches; all batches passed).
- Compile check: passed.

**Current checkpoint: Sprint 219 — 1104 tests passing.**

## Sprint 220 — Assumption Consolidation and Legacy-Field Boundaries

- Added `AssumptionResolver` as the central compatibility boundary for duplicate/legacy assumption names.
- Canonical `inflation_rate` now has an explicit `inflation` fallback; canonical `savings_interest_rate` has an explicit `savings_interest` fallback; canonical `expected_investment_return` has an explicit `pension_growth` fallback.
- Canonical values take precedence when both canonical and legacy values are present; legacy fallback/override conditions are logged at debug level so normal planner output remains quiet.
- Kept `expected_return` as a distinct Monte Carlo mean-return assumption rather than incorrectly merging deterministic and stochastic return semantics.
- Preserved `pension_growth` as a compatibility fallback for older callers and sensitivity workflows.
- Routed the live Inflation and Savings engines, plus the Investment Return resolver, through the canonical assumption boundary.
- Added eight focused regression tests covering canonical precedence, legacy fallback and preservation of distinct Monte Carlo return semantics.
- No default assumptions were changed and no golden baseline regeneration was required.
- Preserved all financial calculation logic and reporting behaviour outside the assumption-access boundary.

- Sprint 220 focused regression: **8 passed**.
- Full suite: **1112 tests passed, 9 subtests** (executed in validated partitions; all partitions passed).
- Compile check: passed.

**Current checkpoint: Sprint 220 — 1112 tests passing.**

## Sprint 221 — Enhanced Goals and Constraints Framework

- Added optional per-goal `enabled` and `operator` controls while preserving legacy defaults for all existing goal types.
- Supported comparison operators `>=`, `>`, `<=`, `<`, `==` and `!=` at the goal-evaluation boundary.
- Disabled goals are omitted from evaluation without affecting other goals.
- Goal results now expose the effective comparison operator and enabled state for downstream reporting/audit consumers.
- Added schema validation and audit-catalog coverage for the new goal controls.
- Added eight focused Sprint 221 regression tests covering legacy defaults, custom operators, disabled/enabled goals and invalid configuration rejection.
- Preserved all retirement, tax, State Pension, ISA, savings, withdrawal, inflation, Monte Carlo and reporting calculation logic.

- Sprint 221 focused regression: **8 passed**.
- Full suite: **1120 tests passed, 9 subtests**.
- Compile check: passed.

**Current checkpoint: Sprint 221 — 1120 tests passing.**

## Sprint 222 — Goal Constraint Report Integration

- Extended the calculation-free professional Goals PDF to present the effective comparison operator alongside each goal.
- Preserved backward compatibility for legacy goal-result consumers that do not provide an operator field.
- Kept the report renderer presentation-only: it displays supplied goal results and does not re-evaluate constraints or mutate source data.
- Preserved the existing disabled-goal semantics from Sprint 221; disabled goals remain omitted from evaluated results.
- Added four focused regression tests covering operator presentation, legacy result compatibility, non-recalculation/non-mutation and empty-result rendering.
- Preserved all retirement, tax, State Pension, ISA, savings, withdrawal, inflation, Monte Carlo and goal calculation logic.

- Sprint 222 focused regression: **4 passed**.
- Full suite: **1124 tests passed, 9 subtests**.
- Compile check: passed.

**Current checkpoint: Sprint 222 — 1124 tests passing.**

## Sprint 223 — Goal Constraint Console Integration

- Extended the console Goals report to present the effective comparison constraint alongside each evaluated goal.
- Preserved compatibility with legacy goal-result mappings that do not contain an operator field.
- Kept the console renderer presentation-only: it displays supplied goal results without re-evaluating or mutating them.
- Added three focused regression tests covering explicit operators, the full custom operator vocabulary and legacy result compatibility.
- Preserved all retirement, tax, State Pension, ISA, savings, withdrawal, inflation, Monte Carlo and goal calculation logic.



## Sprint 224 — Goal Constraint Excel Integration

- Extended the legacy Excel report with an optional `Goals` worksheet that consumes already-evaluated goal results.
- The worksheet presents status, goal name, effective comparison constraint, target and actual values.
- Preserved backward compatibility: existing `ExcelReport.generate(timeline, assumptions)` calls produce the existing workbook shape unchanged.
- Preserved legacy goal-result compatibility when operator metadata is absent.
- Protected Excel literal rendering for the `==` operator without turning the constraint into an executable formula.
- Kept the Excel integration presentation-only: it does not re-evaluate goals or mutate supplied results.
- Added five focused Sprint 224 regression tests.
- Preserved all retirement, tax, State Pension, ISA, savings, withdrawal, inflation, Monte Carlo and goal calculation logic.

- Sprint 224 focused regression: **5 passed**.
- Full suite: **1132 tests passed, 9 subtests** (executed in four validated partitions; all partitions passed).
- Compile check: passed.

**Current checkpoint: Sprint 224 — 1132 tests passing.**

## Sprint 225 — Goal Constraint Audit Coverage Hardening

- Harden the central audit-catalog coverage check for the enhanced goal fields introduced in Sprint 221.
- Ensure nested `goals[].enabled` and `goals[].operator` paths are recognised as explicitly described audit paths, rather than falling through the generic goal-configuration coverage check.
- Preserve the existing descriptions for goal target, name and type paths and the generic fallback for genuinely unknown nested goal fields.
- Keep the change entirely within configuration audit metadata; no retirement or financial calculation logic is changed.
- Added four focused regression tests covering explicit enabled/operator descriptions, legacy goal-field coverage and generic unknown-field fallback.
- Sprint 225 focused regression: **4 passed**.
- Full suite: **1136 tests passed, 9 subtests** (executed in validated partitions; all partitions passed).
- Compile check: passed.

**Current checkpoint: Sprint 225 — 1136 tests passing.**


## Sprint 226 — Goal Constraint Target Semantics Hardening

- Hardened `GoalEngine` so all target-capable goal types consistently honour an explicitly configured `target`.
- `retirement_age` goals now use an explicit target when supplied, while preserving the existing planned-retirement-age fallback when omitted.
- `pension_positive` goals now honour an explicit target while retaining zero as the legacy default.
- `spending` goals now honour an explicit target while retaining `spending_phase_3` as the legacy default.
- Existing goal operators and enabled/disabled semantics are unchanged.
- Added five focused regression tests covering explicit targets and legacy defaults.
- No retirement, tax, State Pension, ISA, savings, withdrawal, investment-return or inflation calculation logic changed.

- Sprint 226 focused regression: **5 passed**.
- Combined goal-constraint regression: **29 passed**.
- Full suite: **1141 tests passed, 9 subtests** (executed in four validated partitions; all partitions passed).
- Compile check: passed.

**Current checkpoint: Sprint 226 — 1141 tests passing.**

## Sprint 227 — Goal Constraint Evaluation Boundary Hardening

- Hardened `GoalEngine` validation for direct callers that bypass the assumptions schema.
- Required `target` values for `estate` and `monte_carlo` goals now produce a clear `ValueError` instead of a later key lookup failure.
- Optional targets for `pension_positive`, `retirement_age` and `spending` are validated when supplied, while their legacy defaults remain unchanged.
- Invalid operators now produce a clear `ValueError` at the goal-evaluation boundary.
- Disabled goals continue to be skipped before constraint validation, preserving existing disabled-goal semantics.
- Added six focused Sprint 227 regression tests.
- Preserved all retirement, tax, State Pension, ISA, savings, withdrawal, investment-return, inflation and Monte Carlo calculation logic.


**Current checkpoint: Sprint 227 — 1147 tests passing.**

## Sprint 228 — Goal Constraint Definition Boundary Hardening

- Hardened `GoalEngine` validation for direct callers that bypass the assumptions schema.
- Goal entries must now be mapping objects with a non-empty `name` and `type`, and any supplied `enabled` value must be boolean.
- Preserved the existing handling of valid unknown goal types: they remain safely skipped for future-compatible goal extensions.
- Preserved disabled-goal semantics after structural validation; disabled well-formed goals remain omitted from evaluated results.
- Added seven focused Sprint 228 regression tests covering malformed goal definitions, invalid enabled metadata and unknown-goal compatibility.
- Preserved all retirement, tax, State Pension, ISA, savings, withdrawal, investment-return, inflation, Monte Carlo and goal calculation semantics.

- Sprint 228 focused regression: **7 passed**.
- Full suite: **1154 tests passed, 9 subtests** (executed in four validated partitions: 285 + 247 + 212 + 410).
- Compile check: passed.

**Current checkpoint: Sprint 228 — 1154 tests passing.**


## Sprint 229 — Goal Constraint Result Boundary Hardening

- Hardened `GoalEngine` direct-call result validation so evaluated goal actual values must be finite numeric values.
- Spending goals now reject an empty projection timeline with a clear boundary error instead of an incidental `min()` failure.
- Boolean, non-numeric and non-finite actual values are rejected before comparison.
- Valid numeric goal results and all existing operator/default-target semantics remain unchanged.
- Preserved all retirement, tax, State Pension, ISA, savings, withdrawal, investment-return, inflation, Monte Carlo and goal calculation semantics.
- Added six focused regression tests.

- Sprint 229 focused regression: **6 passed**.

**Current checkpoint: Sprint 229 — 1160 tests expected after full-suite validation.**

## Sprint 230 — Complete Assumption Catalog and GUI Coverage Hardening

- Extended `audit_catalog.schema_paths()` to include both required and optional schema-defined assumption fields, so the catalog now represents the complete top-level assumptions contract.
- Added regression coverage proving every schema-defined assumption field has explicit audit metadata.
- Added regression coverage against the shipped `data/assumptions.json` document so no current top-level assumption can silently lack an audit description.
- Added GUI end-to-end coverage proving the complete assumptions document, including all optional schedule fields, can be edited, validated, saved and reloaded without key loss or cross-field drift.
- Confirmed the GUI's `Edit all assumptions…` boundary therefore covers the complete current assumptions document rather than only the primary projection controls.
- No retirement, tax, State Pension, ISA, savings, withdrawal, investment-return, inflation, Monte Carlo or goal calculation semantics changed.

- Sprint 230 focused regression: **3 passed**.

**Current checkpoint: Sprint 230 — 1163 tests expected after full-suite validation.**

## Sprint 231 — Assumption Operational Coverage and Legacy Boundary Catalogue

- Added `planner.assumption_usage_catalog` as a calculation-free catalogue of the operational role of every schema-defined top-level assumption.
- Classified assumptions explicitly as live projection inputs, Monte Carlo inputs, legacy compatibility aliases, auxiliary configuration, or goal-domain configuration.
- Added a regression guard proving every schema-defined assumption has an explicit role, preventing future GUI-visible assumptions from becoming operationally ambiguous.
- Explicitly classified `inflation`, `savings_interest` and `pension_growth` as legacy compatibility aliases, preserving the canonical `AssumptionResolver` boundary.
- Explicitly classified `target_net_income` as auxiliary rather than silently treating it as the live spending target; the existing age/schedule spending model remains unchanged.
- Explicitly classified stochastic return/inflation assumptions and goals at their existing domain boundaries.
- No financial calculation semantics changed.

- Sprint 231 focused regression: **4 tests**.

## Sprint 232 — Assumption Consumer Boundary Hardening

- Added `planner.assumption_consumer_catalog` as a calculation-free catalogue of the application boundary that consumes each operational assumption role.
- Linked projection, Monte Carlo, legacy compatibility, auxiliary and goal-domain roles to explicit importable consumer modules.
- Added regression coverage proving every schema-defined assumption resolves to a non-empty consumer boundary and every declared consumer module remains importable.
- Preserved the distinction between legacy aliases and auxiliary `target_net_income`; no assumption was silently promoted into the live spending model.
- No retirement, tax, State Pension, ISA, savings, withdrawal, investment-return, inflation, Monte Carlo or goal calculation semantics changed.

- Sprint 232 focused regression: **4 passed**.
- Full suite: **1171 tests passed, 9 subtests** (293 + 293 + 293 + 292 across four validated partitions).
- Compile check: passed.

**Current checkpoint: Sprint 232 — 1171 tests passing.**

## Sprint 233 — Legacy Assumption Access Boundary Hardening

- Hardened the portfolio-statistics projection boundary so the planner no longer reads the legacy `pension_growth` assumption directly.
- `run_with_portfolio_statistics()` now resolves the projection return through `AssumptionResolver`, preserving canonical `expected_investment_return` precedence and legacy `pension_growth` fallback semantics.
- Added four focused regression tests covering canonical precedence, legacy fallback, removal of direct legacy access and preservation of zero/negative explicit values.
- No retirement, tax, State Pension, ISA, savings, withdrawal, investment-return, inflation, Monte Carlo or goal calculation semantics were intentionally changed; this is a compatibility-boundary cleanup.

- Sprint 233 focused regression: **4 passed**.
- Full suite: **1175 tests passed, 9 subtests** (294 + 294 + 294 + 293 across four validated partitions; all partitions passed).
- Compile check: passed.

**Current checkpoint: Sprint 233 — 1175 tests passing.**

## Sprint 234 — Legacy Assumption Access Guard Hardening

- Added a source-level regression guard proving the historical duplicate assumption keys `inflation`, `savings_interest` and `pension_growth` are not read directly by planner modules outside `AssumptionResolver`.
- Added coverage proving those legacy aliases remain explicitly declared at the resolver boundary.
- Added protection against direct dictionary-index access to the same legacy aliases.
- This closes the remaining direct-access regression surface after Sprint 233 without changing any financial calculation behaviour.
- No retirement, tax, State Pension, ISA, savings, withdrawal, investment-return, inflation, Monte Carlo or goal calculation semantics changed.

- Sprint 234 focused regression: **3 passed**.
- Full suite: **1178 tests passed, 9 subtests** (242 + 547 + 182 + 207 across four validated partitions; all partitions passed).
- Compile check: passed.

**Current checkpoint: Sprint 234 — 1178 tests passing.**

## Sprint 235 — Canonical Inflation Assumption Boundary Hardening

- Hardened the remaining direct `inflation_rate` consumers at the State Pension and Monte Carlo boundaries to resolve through `AssumptionResolver` rather than reading the canonical key directly.
- Preserved existing fallback/default semantics: State Pension direct callers may still omit inflation when triple-lock CPI is not required, while Monte Carlo continues to default a missing inflation mean to `0.0`.
- Added four focused regression tests covering canonical-over-legacy precedence, legacy fallback, direct-read exclusion and resolver adoption.
- No retirement, tax, State Pension, ISA, savings, withdrawal, investment-return or Monte Carlo calculation semantics were intentionally changed.

- Sprint 235 focused regression: **4 passed**.
- Full-suite baseline from Sprint 234: **1178 tests passing**; Sprint 235 adds 4 regression tests. Re-validation of the complete suite was not completed within the available execution window; impacted Monte Carlo/State Pension regression coverage and compile checks passed.

**Current checkpoint: Sprint 235 — 1182 tests expected after full-suite validation.**
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

- Hardened the validation boundary so the Monte Carlo `expected_return` assumption is resolved through `AssumptionResolver.monte_carlo_expected_return()` rather than read directly by `ValidationEngine`.
- Preserved the existing precedence chain: explicit `expected_return`, canonical `expected_investment_return` fallback, then legacy `pension_growth` fallback.
- Added four focused regression tests covering precedence, canonical fallback, legacy fallback and direct-read exclusion.
- No financial calculation semantics changed.

- Sprint 238 focused regression: **4 passed**.
- Full suite: **1194 tests passed, 9 subtests** (262 + 412 + 253 + 267; all partitions passed).
- Compile check: passed.

**Current checkpoint: Sprint 238 — 1194 tests passing.**

## Sprint 239 — Canonical Assumption Consumer Boundary Audit Hardening

- Extended `AssumptionResolver` with explicit calculation-boundary accessors for investment volatility, inflation volatility, ISA growth, and State Pension configuration inputs.
- Routed the remaining selected canonical consumers through the resolver at the State Pension, ISA/investment-return, Monte Carlo and investment-validation boundaries.
- Added a source-level regression guard preventing those selected canonical assumptions from being read directly by planner calculation modules outside the resolver boundary.
- Preserved existing canonical values, defaults and legacy alias precedence; no retirement, tax, State Pension, ISA, savings, withdrawal, investment-return or Monte Carlo calculation semantics were intentionally changed.
- Added four focused Sprint 239 regression tests.
- Sprint 239 focused regression: **4 passed**.
- Compile check: passed.
- Full regression: **1198 tests passed** across validated test groups; zero-test legacy modules remain non-contributing.

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
- Extended the projection consumer boundary to include validation, timeline, strategy and investment-return consumers that directly operationalise schema-defined assumptions.
- Extended the Monte Carlo boundary to include its validation-side expected-return consumer.
- Added executable traceability regression coverage proving every schema-defined assumption has evidence in its declared consumer boundary.
- Preserved the distinction between deterministic projection and stochastic Monte Carlo roles, and retained the resolver-only boundary for historical aliases.
- No financial calculation logic was changed.

## Sprint 242 — Assumption Validation and Error-Handling Hardening

- Hardened `AssumptionResolver` numeric accessors with a shared finite-number boundary, rejecting booleans, non-numeric values and non-finite values with explicit `ValueError` messages.
- Required numeric accessors now distinguish missing assumptions from invalid supplied values instead of surfacing incidental `TypeError`/conversion failures.
- Preserved canonical-over-legacy precedence: an explicitly supplied but invalid canonical value fails validation rather than silently falling back to its legacy alias.
- Preserved Monte Carlo precedence and validates the selected value at the point of use.
- Preserved optional numeric defaults for charges, volatility and ISA growth when those assumptions are absent.
- Added six focused Sprint 242 regression tests covering missing, invalid, non-finite, boolean, precedence and default cases.
- No financial calculation logic or established default semantics were intentionally changed.

- Sprint 242 focused regression: **6 passed**.
- Consolidated Sprint 239–242 assumption boundary regression: **45 passed**.
- Full suite: **1212/1212 tests passed** across four validated partitions (268 + 271 + 257 + 416).
- Compile check: passed.

**Current checkpoint: Sprint 242 — 1212 tests passing.**

## Sprint 243 — GUI / Schema / Report Assumption Consistency

- Hardened the Excel assumptions report to consume the same audit-description catalogue as the GUI assumption-change boundary.
- Nested assumption structures (goals and annual schedules) are exported as deterministic JSON strings so every schema-defined value remains representable and lossless in Excel.
- Added regression coverage proving the GUI editor validates and round-trips every schema-defined top-level assumption and preserves nested configuration.
- Added report regression coverage proving every schema-defined assumption appears in the Excel assumptions sheet with its matching audit description.
- No financial calculation logic or assumption defaults changed.

- Sprint 243 focused regression: **4 passed**.

**Current checkpoint: Sprint 243 — full-suite validation pending.**

- Full suite: **1216/1216 passed** across four independently validated partitions (275 + 256 + 243 + 442).
- Compile check: passed.

**Current checkpoint: Sprint 243 — 1216 tests passing.**

## Sprint 244 — Assumptions Boundary Freeze

- Added executable freeze guards covering the resolver-only legacy alias boundary and the canonical assumption mapping contract.
- Regression-protected canonical-over-legacy precedence for inflation, savings interest and deterministic investment return.
- Regression-protected the distinct Monte Carlo return precedence: `expected_return` → `expected_investment_return` → `pension_growth`.
- Completed the final cross-layer assumptions regression sweep; no unresolved legacy alias consumers remain outside `AssumptionResolver`.
- No financial calculation logic or assumption defaults changed.

- Sprint 244 focused regression: **4 passed**.
- Full suite: **1220/1220 tests passed** across four independently validated partitions (301 + 263 + 228 + 428).
- Compile check: passed.

**Current checkpoint: Sprint 244 — assumptions boundary frozen; 1220 tests passing.**
## Sprint 245 — Assumption Boundary Documentation and Release Traceability

- Added `planner/docs/ASSUMPTION_BOUNDARY.md` as the durable developer-facing contract for canonical assumption access, legacy compatibility and Monte Carlo precedence.
- Documented the numeric validation boundary and the required change/checkpoint protocol without changing calculation behaviour.
- Added four documentation/traceability regression tests so the frozen assumption contract remains visible and the roadmap/status checkpoint cannot silently drift.
- No retirement, tax, State Pension, ISA, savings, withdrawal, investment-return, inflation, Monte Carlo or goal calculation semantics changed.

- Sprint 245 focused regression: **4 passed**.
- Sprint 244 protected baseline: **1220 tests passing**.

**Current checkpoint: Sprint 245 — assumption boundary documentation and release traceability; 1224 tests after full-suite validation.**

## Sprint 246 — Cross-Engine Integration Coverage

- Added `tests/test_sprint246_cross_engine_integration.py` with eight end-to-end regression tests over the shared retirement projection timeline.
- Protected cross-engine flow from inflation → spending/tax, State Pension → cash/strategy, property sale → ISA/savings, scheduled investment/ISA returns → asset roll-forwards, strategy → withdrawal → tax → pension, and completed projection → summary.
- Added deterministic repeat-run coverage for the complete planner path.
- No retirement, tax, State Pension, ISA, savings, withdrawal, investment-return, inflation, Monte Carlo or goal calculation semantics were changed.

- Sprint 246 focused regression: **8/8 passed**.
- Affected integration regression: **80/80 passed**.
- Full suite: **1232/1232 passed** across four independently validated partitions (308 + 309 + 308 + 307).
- Compile check: passed.

**Current checkpoint: Sprint 246 — cross-engine integration coverage; 1232 tests passing.**


## Sprint 247 — Scenario / Edge-Case Matrix Expansion

- Added `tests/test_sprint247_scenario_edge_case_matrix.py` with eight boundary-focused regression tests covering projection-horizon, property-sale, spending-phase and scheduled-return edge cases.
- Protected a one-row projection when the projection horizon equals the current age.
- Protected property-sale behaviour at the first projected age and after the projection horizon.
- Protected spending-phase transitions at the configured phase boundaries while preserving inflation-linked spending.
- Protected scheduled investment and ISA returns both outside the projection horizon and on the final projected year.
- No retirement, tax, State Pension, ISA, savings, withdrawal, investment-return, inflation, Monte Carlo or goal calculation semantics were changed.

- Sprint 247 focused regression: **8/8 passed**.
- Full suite: **1240/1240 tests passed** across four independently validated partitions (310 + 310 + 310 + 310).
- Compile check: passed.

**Current checkpoint: Sprint 247 — scenario / edge-case matrix expansion; 1240 tests passing.**

## Sprint 248 — Schedule Interaction Hardening

- Added eleven end-to-end and engine-boundary regression tests covering simultaneous annual spending, investment-return, ISA-return, State Pension earnings-growth and ISA-allowance schedules.
- Protected schedule precedence and independence: a matching schedule entry overrides only its own base assumption, while downstream inflation, investment charges and asset roll-forward layers remain intact.
- Protected ISA allowance tax-year selection and inflation linking during property-sale allocation.
- Protected ISA return ordering so scheduled growth applies to the opening ISA balance before same-year contributions are added.
- Protected State Pension triple-lock interaction between scheduled earnings growth, projected CPI and the 2.5% floor, including first-payable-year behaviour.
- Protected deterministic repeatability and independent schedule enable/disable behaviour.
- No financial calculation logic or assumption defaults changed.

- Sprint 248 focused regression: **11/11 passed**.
- Compile check: passed.
- Full suite: **1251/1251 tests passed** across four independently validated partitions (313 + 313 + 313 + 312).

**Current Sprint: Sprint 248 — Schedule Interaction Hardening**
**Current checkpoint: Sprint 248 — 1251 tests passing.**
## Sprint 249 — Tax / Withdrawal Integration

- Added eleven end-to-end regression tests covering the strategy → withdrawal → tax → pension boundary.
- Protected pension-income caps, ISA fallback and explicit income-shortfall behaviour before tax gross-up.
- Protected net-to-gross tax calculation, State Pension interaction, lifetime tax-free cash consumption and the `use_tax_free_cash` boundary.
- Protected final pension roll-forward and summary aggregation from the tax/withdrawal pipeline.
- Protected deterministic repeat-run behaviour.
- No financial calculation logic or assumption defaults changed.

- Sprint 249 focused regression: **11/11 passed**.
- Compile check: passed.
- Full suite: **1262/1262 tests passed** across four independently validated partitions (316 + 316 + 315 + 315).

**Current Sprint: Sprint 249 — Tax / Withdrawal Integration**


## Sprint 250 — Monte Carlo / Deterministic Parity

- Added `tests/test_sprint250_monte_carlo_deterministic_parity.py` with ten regression tests protecting the explicit deterministic versus Monte Carlo return boundary.
- Protected deterministic projections using `expected_investment_return` independently of the Monte Carlo mean `expected_return`.
- Protected Monte Carlo precedence `expected_return` → `expected_investment_return` → `pension_growth` and the single application of platform/fund charges.
- Protected seeded Monte Carlo return injection, repeatability and independence from deterministic projection-return changes.
- No financial calculation logic or assumption defaults changed.

- Sprint 250 focused regression: **10/10 passed**.
- Full suite: **1272/1272 tests passed** across four independently validated partitions (318 + 318 + 318 + 318).
- Compile check: passed.

**Current checkpoint: Sprint 250 — Monte Carlo / Deterministic Parity; 1272 tests passing.**

## Sprint 251 — GUI → Engine → Report Traceability

- Added `tests/test_sprint251_gui_engine_report_traceability.py` with eight executable integration regressions across the GUI assumptions editor, application inputs, scenario workflow snapshot and report payload/text.
- Protected propagation of edited starting pension and retirement/projection ages from GUI JSON into workflow inputs.
- Protected report provenance: payload and rendered text are built from the published snapshot, scenario identity remains consistent, and repeat runs publish identical results.
- Protected invalid-edit rollback, nested schedule round-trip and immutable report payload publication.
- No financial calculation logic or assumption defaults changed.

- Sprint 251 focused regression: **8/8 passed**.
- Full suite: **1280/1280 tests passed** across four independently validated balanced partitions (320 + 320 + 320 + 320).
- Compile check: passed.

**Current checkpoint: Sprint 251 — GUI → Engine → Report Traceability; 1280 tests passing.**

## Sprint 252 — Regression / Golden Scenario Pack

- Added `tests/test_sprint252_golden_scenario_pack.py` with eight regressions around the existing committed golden baseline.
- Protected complete baseline schema, projection horizon row count, every stored golden field, finite baseline values, deterministic repeat runs, and prevention of tests silently regenerating the baseline.
- Kept the existing baseline file and all financial calculation logic unchanged.
- Sprint 252 focused regression: **8/8 passed**.
- Compile check: passed.
- Full suite: **1288/1288 tests passed** across four balanced partitions (322 + 322 + 322 + 322), as confirmed at the Sprint 252 handoff.

**Checkpoint: Sprint 252 — Golden Scenario Pack; 1288 tests passing.**


## Sprint 253 — Release Readiness / Technical-Debt Sweep

- Added `planner/docs/RELEASE_READINESS.md` with explicit regression, compile, golden-baseline, financial-boundary, configuration, entry-point/report, packaging and traceability gates.
- Added six regression tests for release-checklist completeness, calculation-safety policy, project test configuration, assumptions JSON integrity and sprint traceability.
- Updated the README to point to the release checklist and the current RC4 checkpoint, replacing the stale Sprint 170 / 911-test status line.
- Audited obvious TODO/FIXME markers in maintained Python source; no matches were found in the scanned planner, test and root Python files. No broad or speculative cleanup was performed.
- No production financial calculation logic or assumption defaults changed.

- Sprint 253 focused regression: **6/6 passed**.
- User-confirmed Sprint 252 baseline: **1288 tests passing**. Sprint 253 adds six tests (1,294 pytest tests collected); the full-suite rerun timed out in this environment, so no Sprint 253 full-suite pass is claimed.

**Current checkpoint: Sprint 253 — Release Readiness / Technical-Debt Sweep; focused checks passed, full-suite rerun pending.**


## Sprint 254 — Release Acceptance & Reproducible Validation

- Added `scripts/release_acceptance.py` as a single acceptance entry point for assumptions JSON parseability, compilation and pytest execution. It reports each gate and exits non-zero when a requested gate fails.
- Added deterministic round-robin pytest partitioning (`--partition N --partitions M`) so long-running suites can be executed in independently recorded chunks when a single run exceeds environment limits. Every partition must pass before the complete suite is considered green.
- Added twelve regression tests for runner defaults, gate skipping, extra pytest arguments, non-mutating assumptions checks, checklist traceability, failure reporting and partition validation/distribution.
- Expanded the release-readiness checklist with the repeatable command and partition-completion rule.
- No production financial calculation logic, golden data or assumption defaults changed.

- Sprint 254 focused regression: **12/12 passed** (together with Sprint 252/253 focused tests: **26 passed, 8 subtests passed**).
- Compile check: passed. Assumptions JSON parse: passed.
- Pytest collection: **1306 tests collected**. A single-process full-suite attempt timed out in this environment; no Sprint 254 full-suite pass is claimed. The user-confirmed Sprint 253 baseline remains **1294 tests passing**.

**Current checkpoint: Sprint 254 — Release Acceptance & Reproducible Validation; focused checks passed, full-suite partitions remain to be run.**


## Sprint 255 — Release Packaging & End-to-End Acceptance

- Added a read-only checkpoint ZIP audit command (`python scripts/package_audit.py <checkpoint.zip>`) for archive integrity, required source/docs/tests/configuration, parseable packaged assumptions, safe paths and exclusion of transient caches/bytecode.
- Added eight regression tests for positive and negative package-audit cases and release traceability.
- Sprint 254 acceptance suite is now fully validated: all 1,306 collected tests passed across four partitions (327, 327, 326, 326), with 20 subtests passed. Compile and assumptions JSON gates passed.
- No production financial calculation logic, golden baseline or assumption defaults changed.

- Sprint 255 focused regression: **8/8 passed**; combined Sprint 252–255 focused checks: **34 passed, 8 subtests passed**.
- Full suite: **1,314/1,314 tests passed** across four partitions (329 + 329 + 328 + 328), with 20 subtests passed.
- Compile check passed; final archive verification is run after packaging.

**Current checkpoint:** Sprint 255 — Release Packaging & End-to-End Acceptance; 1,314 tests passing across four partitions.

## Sprint 256 — Historical-Data Integration Design

- Added `planner/market/historical_data_contract.py` as a typed, validation-only boundary for annual equity returns, bond returns and inflation observations, with explicit provenance, actual/estimated status, currency and nominal/real basis.
- Added `planner/docs/HISTORICAL_DATA_INTEGRATION.md` documenting units, missing-year policy, source provenance, validation rules and a staged opt-in replay integration plan.
- Added thirteen contract regressions covering invalid numeric values, years, provenance, series consistency, duplicates, missing years and explicit gap allowance without interpolation or fabricated observations.
- The new contract is not wired into `MarketData`, deterministic projections or Monte Carlo. Existing market CSVs, calculation logic, assumptions defaults and golden data remain unchanged.
- Sprint 256 focused regression: **13/13 passed**.
- The Sprint 255 baseline was fully validated across four partitions: **1,314/1,314 passed**, with 20 subtests passed. Sprint 256 adds 13 tests; full-suite validation for the 1,327-test suite is pending.

**Current checkpoint:** Sprint 256 — Historical-Data Integration Design; focused tests passed, full-suite validation pending.


## Sprint 256 — Checkpoint Reconciliation / Acceptance Evidence (2026-10-11)

- Reconciled the uploaded working tree against the sprint test files and the documented Sprint 253 baseline. The 1,294 count belongs to Sprint 253; Sprint 254–256 add 12 + 8 + 13 tests, producing 1,327 collected tests.
- Verified the complete current suite by deterministic partition: 332 + 332 + 332 + 331 = **1,327 passed**, with 20 subtests passed across partitions.
- Verified `python -m compileall -q .` and the focused Sprint 252–256 group (**47 passed, 8 subtests passed**).
- Found packaging hygiene failure in the user-uploaded ZIP: it included `.git`, pytest caches, `__pycache__` and `.pyc` files and used a wrapper directory. The reconciled release ZIP is assembled at repository root without these transient artifacts and is audited before handoff.
- Git HEAD is still labelled Sprint 140 although the worktree contains later sprint files. No commit history rewrite was attempted; this mismatch is documented rather than concealed.
- No financial calculation logic, assumptions or golden baseline were changed during this reconciliation.


## Sprint 257 — Historical Data Adapter Interface & Versioned Fixture Format

- Added a provider-neutral `HistoricalDataSourceAdapter` protocol and immutable `HistoricalSeriesDataset` result.
- Added strict JSON fixture format `retirement-planner-historical-series`, integer version 1, with exact key sets and contract validation.
- Added a synthetic sample fixture and 14 regression tests covering versioning, metadata, provenance/status retention, malformed JSON, unknown fields, gap rejection and no rate coercion.
- No live provider, projection integration, or financial calculation changes. Focused Sprint 257 tests: 14/14 passed. Full suite: **1,341/1,341 passed** across four partitions (336 + 335 + 335 + 335), with 20 subtests passed; compilation passed.

## Sprint 258 — Test Collection Reconciliation & Environment Fingerprinting

- Added a reproducible collection report including pytest node IDs, per-file counts, runtime versions and SHA-256 fingerprints of test/configuration files.
- Added a report comparison mode that lists test IDs present only in either environment and detects changed test-file/config hashes.
- Added nine diagnostic unit tests. This resolves the *method* for reconciling the discrepancy; it does not assume that 1,308 or 1,341 is universally authoritative. The user-confirmed count remains 1,308 pending a comparison report from the user's runtime.
- No financial calculations, assumptions, live data connections or golden baseline changed.


## Sprint 258 — Test Collection Reconciliation & Environment Fingerprinting

- Added a read-only pytest collection report with runtime versions, exact node IDs, per-file counts and SHA-256 hashes for test/configuration files.
- Added comparison mode that reports exact node IDs present only in either environment and changed test/configuration hashes.
- Added nine focused tests for parsing, de-duplication, report generation and comparison.
- Validation in this environment: **1,350/1,350 passed** across four partitions (338 + 338 + 337 + 337), with 20 subtests passed; compile and assumptions JSON checks passed.
- User-confirmed local test count remains **1,308 passing**. These counts are not conflated: a report from the user's runtime is needed to determine why the node-ID sets differ.
- No production financial calculation logic, assumptions defaults, or golden baseline changed.


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

- Harden replay input validation and make estimated-data inclusion a strict boolean opt-in.
- Reject real-return series at the replay boundary to prevent applying inflation adjustment twice.
- Detect non-finite compounded and inflation-adjusted values and raise a clear replay error.
- Add regression coverage for malformed datasets, configuration flags, numeric overflow, and replay window isolation.
- Keep replay separate from production deterministic projections, Monte Carlo, GUI workflows, assumptions, and golden scenario calculations.
- Targeted validation: **71 passed** including the golden scenario regression group; the Sprint 259–260 replay tests pass **18/18**. Partition 1/8 passed **172 tests plus 11 subtests**; partition 2/8 timed out in this environment, so full-suite validation remains pending. Compile and assumptions JSON checks passed. Final archive audit passed: 387 entries, ZIP integrity and required files verified, transient artifacts excluded.


## Sprint 261 — Historical Replay Regression Isolation (2026-10-14)

- Added seven regressions protecting the historical replay isolation boundary: production source files must not import the replay utility; the replay module must not depend on deterministic planner or Monte Carlo engines; repeated calls must be deterministic and free of cross-call state; successful and failed calls must not mutate the supplied dataset, assumptions JSON, or golden baseline.
- Extended the release package audit to require the Sprint 261 regression module and added Sprint 261 status/roadmap traceability coverage.
- No production financial calculation logic, assumptions defaults, or golden baseline changed.
- User-reported test baseline remains **1,308 successful** and is kept distinct from this environment's execution results.
- Focused replay/isolation/Monte Carlo parity/golden/package-audit regression group: **46 passed**.
- Full suite: **1,377/1,377 passed** across 16 deterministic partitions (87 + 15 × 86), with **20 subtests passed**.
- Compilation and assumptions JSON checks passed. The assumptions JSON and golden baseline SHA-256 values are unchanged from the uploaded Sprint 260 checkpoint.
- The user-reported local baseline of **1,308 successful** remains separately recorded; the current archive collected and passed 1,377 test items.


## Sprint 262 — Test-Count Reconciliation & Release Acceptance (2026-10-14)

- Re-ran pytest collection against the actual Sprint 260 and Sprint 261 checkpoint ZIPs under one Python/pytest environment. Sprint 260 collected 1,369 node IDs; Sprint 261 collected 1,377. The exact node-ID diff is eight additions and zero removals.
- Added the reproducible Sprint 262 collection snapshot at `reports/sprint262_collection_report.json`, containing exact node IDs, per-file counts, interpreter/pytest versions and test/configuration SHA-256 hashes.
- Executed all 16 deterministic partitions from the Sprint 261 archive: 87 + 15 × 86 = **1,377 passed**, with **20 subtests passed**. The one-process run timed out, so acceptance relies on the successful independent partition runs.
- Reconfirmed compilation and assumptions JSON parsing. SHA-256 values for `data/assumptions.json` and `tests/golden/baseline.json` match between Sprint 260 and Sprint 261.
- Reconciled the count discrepancy: the user's reported 1,308 remains a distinct, unverified local result; this archive has 1,377 collected and passing test items. The historical 1,308 result predates the later 1,377-item Windows report; the supplied 1,377-item report matches Sprint 262 exactly.
- No financial calculation logic, assumptions defaults, or golden baseline changed. No tests were added solely to inflate the headline count.


## Sprint 263 — Collection Report Integrity Validation (2026-10-15)

- Validate collection-report format/version, node-ID structure and uniqueness, total counts, per-file counts, and SHA-256 digest formatting.
- Record exact node-ID reconciliation in `reports/sprint263_test_count_reconciliation.json`: 11 additions and 0 removals compared with Sprint 262.
- Reject malformed comparison reports before producing collection diffs, so inconsistent local reports cannot be mistaken for valid reconciliation evidence.
- Add focused regression coverage and package-audit traceability for Sprint 263.
- Keep all financial calculation logic, assumptions defaults, and the golden scenario baseline unchanged.
- Current collection: **1,388 test items across 157 test files**. Targeted diagnostics/validation/package-audit tests: **30 passed**. Full suite: **1,388/1,388 passed** across 16 deterministic partitions (12 × 87 + 4 × 86), with **20 subtests passed**; the single-process run exceeded the execution window.


## Sprint 264 — Test Evidence Freshness & Count Reconciliation

- Tighten report comparison: a report is considered reconciled only when node IDs, test-file sets, test-file hashes, and pytest configuration hashes all match.
- Keep the user's 1,377-item Windows report as a labeled Sprint 262 historical snapshot. It matches the Sprint 262 report exactly, including node IDs and source/config hashes; it predates Sprint 263's 11 additional tests.
- Remove ambiguous root-level `local-collection.json`, `collection-local.json`, and `full_test.txt` artifacts from release packages. Retain the two collection JSON files under `reports/archive/` with explicit historical labels.
- Require Sprint 263/264 collection reports and reconciliation evidence in package audit.
- No production calculation, assumptions, or golden baseline changes.


## Sprint 265 — Release Manifest & Artifact Integrity

- Create a reproducible SHA-256 release manifest covering every archive member except the manifest itself. Record relative path, byte size, digest, manifest version and sprint number.
- Extend package audit to reject missing/malformed manifests, path-set mismatches, size mismatches and digest mismatches. Retain all existing package-safety gates.
- Document the build/verify commands and the boundary that an unsigned checksum manifest is not a digital signature.
- Add regression tests for deterministic output, exclusion rules, valid archives and tamper detection.
- Preserve production financial calculation logic, assumptions defaults and the golden baseline.

**Current checkpoint:** Sprint 265 — Release Manifest & Artifact Integrity; 1,408 tests passing, full-suite run completed in 162.61 seconds, manifest and package audit passed.

## Sprint 266 — Cross-Platform Package Path Safety

- Reject Windows-style path traversal, drive-qualified paths, UNC paths, absolute paths, NUL characters, and non-canonical backslash separators in release ZIPs.
- Reject duplicate archive member names to prevent inconsistent interpretations across ZIP readers.
- Validate manifest entries alongside archive members; manifest metadata must not permit unsafe paths.
- Document package path safety and add regression coverage for accepted canonical relative paths and rejected unsafe paths.
- Preserve all financial calculation logic, assumptions defaults, and the golden baseline.
- Sprint 265 baseline: **1,408 tests passing**. Sprint 266 full suite: **1,421/1,421 passed** across 32 deterministic partitions (13 × 45 and 19 × 44), with 20 subtests passed. Focused regression group: **53 passed**; compile and assumptions JSON checks passed. Final release manifest covers 391 payload files; the 392-entry ZIP passed CRC and package audit.

## Sprint 267 — Release Manifest Schema Hardening

- Reject duplicate JSON object keys in `release_manifest.json` instead of allowing parser last-value-wins ambiguity.
- Require `sprint` to be a positive integer, `file_count` to be a non-negative integer, and each `size_bytes` value to be a non-negative integer; booleans are not accepted as integers.
- Apply canonical archive-path checks to every manifest path as well as every ZIP member.
- Refuse symlinks in release input trees so the manifest builder cannot hash external targets or produce platform-dependent packages.
- Refresh the README's current-checkpoint summary and add focused regression coverage for schema edge cases and symlink inputs.
- Preserve all production financial calculation logic, assumptions defaults, and the golden baseline.

## Sprint 268 — ZIP Symlink & Special-Entry Safety

- Reject Unix symlink entries encoded in ZIP metadata before a release package is accepted, including links masquerading as required files.
- Apply unsafe-path validation to directory entries as well as file entries.
- Change duplicate ZIP-entry detection to a linear pass to avoid quadratic work on large or hostile archives.
- Add portable regressions that construct symlink metadata directly in ZIP entries, without requiring filesystem symlink support.
- Preserve all financial calculation logic, assumptions defaults and the golden baseline.

- Sprint 268 validation: **1,436/1,436 passed** across 32 deterministic partitions (28 × 45 and 4 × 44), with 20 subtests passed. Focused Sprint 265–268 regression group: **36 passed**. Compilation and assumptions JSON checks passed; package audit/ZIP CRC are recorded in the release reconciliation report.
- Current checkpoint: **Sprint 268 — ZIP Symlink & Special-Entry Safety**.

## Sprint 269 — ZIP Metadata & Decompression Resource Limits

- Preflight ZIP central-directory metadata before CRC verification or payload reads.
- Reject encrypted entries, unsupported compression, impossible non-empty/zero-compressed-size entries, excessive compression ratios, excessive uncompressed per-entry/total sizes, and excessive entry counts.
- Keep the checks bounded and documented; retain CRC, manifest SHA-256/size, canonical-path, duplicate-entry, and symlink checks.
- Add focused adversarial archive regressions and update release evidence.
- Preserve all financial calculation logic, assumptions defaults, and the golden baseline.

## Sprint 270 — ZIP Special-File Metadata Safety

- Reject Unix FIFO, character-device, block-device, and socket entries in release ZIPs; the release format supports only ordinary files and directories.
- Require Unix directory/file metadata to agree with whether a ZIP member name ends in a directory separator.
- Run special-file type checks before CRC verification and payload decompression. Preserve the existing symlink, path, manifest, duplicate-entry, and resource-limit checks.
- Add portable synthetic ZIP regressions and package audit traceability.
- Preserve all financial calculation logic, assumptions defaults, and the golden baseline.



## Sprint 271 — ZIP Filename Collision Safety

- Reject distinct archive member names that collide after Unicode NFC normalization and case folding, preventing cross-platform extraction overwrites and ambiguous path resolution.
- Reject a regular-file entry when another member uses that path as a parent directory (for example, `assets` alongside `assets/logo.png`).
- Permit explicit directory entries with child members and unrelated paths that differ only in leaf names in separate directories.
- Run path collision checks before CRC validation and payload decompression. Retain exact duplicate, canonical path, special-file, resource-limit, and manifest checks.
- Preserve all financial calculation logic, assumptions defaults, and the golden baseline.
- Validation: **1,463/1,463 passed** across 8 deterministic partitions (7 × 183 + 1 × 182), with 20 subtests passed; focused package-safety group **63 passed**. Manifest covers 411 payload files; final 412-entry ZIP passed CRC and package audit.


## Sprint 272 — ZIP Windows Filename Safety (2026-10-16)

- Reject Windows-invalid filename punctuation and ASCII control characters in ZIP path components.
- Reject trailing dots/spaces and reserved DOS device names, including extensions and superscript COM/LPT variants.
- Perform filename portability checks before CRC checks or payload reads.
- Add portable regression coverage and release-evidence traceability.
- Preserve all financial calculation logic, assumptions defaults and the golden scenario baseline.

- Sprint 272 validation: **1,474/1,474 passed** across 32 deterministic partitions, with **20 subtests passed**; focused Sprint 265–272 package-safety regression group: **74 passed**. Collection is 1474 items across 166 test files; 11 node IDs added and zero removed. The single-process run exceeded the execution window, so every deterministic partition was run independently and passed.
- Compilation and assumptions JSON checks passed. Assumptions SHA-256 `33736d31d6a8d14b73b5ec83c9a9befcbb736713979a7eaaa95b2c35d22b3801` and golden baseline SHA-256 `d0d45d5c3e2846a79711a4e23f3920a04a81bef6025917a2aa9a00d82733c550` are unchanged. Package audit and ZIP CRC are verified after manifest regeneration.


## Sprint 273 — ZIP Local-Header Integrity

- Validate ZIP local headers against central-directory metadata before CRC verification or decompression.
- Reject filename/flag/compression-method disagreements and CRC/size mismatches; support ZIP64 sizes and data descriptors.
- Reject invalid local-header signatures, header/data bounds that reach the central directory, and overlapping local records.
- Preserve all existing path portability, collision, special-file, resource-limit, manifest, and financial-calculation safeguards.

## Sprint 274 — ZIP Security Review & Data-Descriptor Integrity

- Review the combined ZIP safeguards from Sprints 266–273 for a concrete parser-disagreement gap rather than adding redundant checks.
- Close the gap where local-header validation accounted for data-descriptor length but did not compare descriptor CRC-32 and compressed/uncompressed sizes against central-directory values.
- Validate both signed and unsigned data descriptors, including ZIP64 widths, and reject truncated or inconsistent descriptors before payload decompression.
- Add portable regression coverage and document the review scope and validation boundaries.
- Preserve all financial calculation logic, assumptions defaults, and the golden baseline.

## Proposed follow-on roadmap (scope to be confirmed per sprint)

### Sprint 275 — Reproducible Release Evidence

- Reconcile test collection reports, node-ID diffs, test-file/configuration hashes, manifest entries, and packaged file inventory from a single final checkpoint.
- Add regression coverage for stale or internally inconsistent release evidence; do not infer a full-suite pass from collection alone.
- Preserve all financial calculation logic, assumptions defaults, and the golden baseline.

### Sprint 276 — Release Workflow & GitHub Publication

- Document and validate a repeatable release workflow from verified checkpoint ZIP through remote publication.
- Record remote repository, branch, commit and verification evidence only after a successful push or equivalent confirmed remote update.
- Keep local ZIP verification distinct from GitHub publication status.
- Preserve all financial calculation logic, assumptions defaults, and the golden baseline.

### Sprint 274 validation addendum

- Full suite: **1,490/1,490 passed** across 32 deterministic partitions (18 × 47 and 14 × 46), with 20 subtests passed. Focused Sprint 265–274 package-security regression group: **90 passed**; Sprint 274 tests: **6 passed**.
- Collection: **1,490 tests across 168 files**; six node IDs added and none removed versus Sprint 273.
- `python -m compileall -q .` and assumptions JSON parse passed. Assumptions and golden-baseline hashes remain unchanged.
- Sprint 275 and Sprint 276 are proposed follow-on scope, to be refined against Sprint 275 findings.


## Sprint 275 — Reproducible Release Evidence

- Added `scripts/release_evidence.py` to reconcile collection report structure and counts, test/config hashes, current source-tree manifest hashes and sizes, archive inventory, embedded manifest, and archive SHA-256.
- The report explicitly distinguishes collection from execution with `test_execution_status: NOT_VERIFIED_BY_THIS_REPORT`; collection alone is never treated as a test pass.
- Added regression coverage for stale test hashes, missing test files, inconsistent counts, stale manifest hashes, missing/extra manifest paths, unmanifested ZIP entries, embedded-manifest mismatch, and non-claiming execution status.
- Added `planner/docs/REPRODUCIBLE_RELEASE_EVIDENCE.md` with a repeatable sequence and invalidation rules when source files change.
- Updated release-manifest default sprint to 275. No production financial calculations, assumptions defaults, or golden baseline were intentionally changed.


### Sprint 275 validation addendum

- Collection: **1,498 node IDs / 169 test files**; collection is not evidence of test execution.
- Focused Sprint 275 and related manifest regression tests: **27 passed**. Compile check and assumptions JSON parse passed.
- Package audit and source/collection/manifest/archive reconciliation passed. Package contains 427 payload files plus `release_manifest.json`; archive SHA-256 is recorded in `reports/sprint275_release_evidence.json`.
- Full-suite partition run timed out at partition 9 of 32. No full-suite pass total is claimed; request user-side full run.

## Sprint 276 — Release Workflow & GitHub Publication

- Added `.github/workflows/release.yml`: full pytest execution, compilation and assumptions JSON validation must succeed before the packaging job can run.
- Added `scripts/build_release_archive.py` to build deterministic ZIPs from a current release manifest, using sorted paths, fixed timestamps/modes, SHA-256 and size preflight, and traversal/symlink rejection.
- Added `planner/docs/RELEASE_WORKFLOW.md` describing local verification, evidence capture, GitHub Actions artifact behavior, version-tag release publication and the required publication record.
- Added Sprint 276 regression tests for workflow gating, tag-only GitHub Release publication, deterministic archive output, stale-manifest rejection and unsafe manifest paths. Updated package audit required entries and excluded generated `dist/` files from source manifests.
- Made release-evidence reports derive their sprint number from the manifest; the default manifest sprint is now 276.
- No production financial calculations, assumptions defaults, or golden baseline were intentionally changed.

## Sprint 277 — Assumptions / Engine / GUI Coverage Audit

- Implemented a static audit across `data/assumptions.json`, `AssumptionsSchema`, `ROLES`, `CONSUMERS`, audit descriptions and the GUI complete-document JSON editor boundary.
- Audit emits machine-readable JSON and a non-zero exit code when consistency gaps exist.
- Added regression tests and usage/interpretation documentation. Explicitly distinguishes static metadata coverage from proof of runtime calculation correctness.
- No financial calculations, assumptions defaults, or golden baseline changed.


## Sprint 278 — GUI Assumptions Workflow Coverage

- Cover the full assumptions editor action matrix from text validation and formatting through apply, explicit save, reload and discard.
- Verify the three distinct states (editor text, active in-memory assumptions, and persisted baseline) remain consistent and invalid edits cannot partially mutate them.
- Preserve all financial calculation logic, assumptions defaults, and the golden baseline.

## Sprint 279 — Inflation-Adjusted ISA Allowance

- Verify the ISA allowance inflation-adjustment option remains opt-in by default and is applied only when enabled.
- Cover tax-year boundaries, allowance schedules, and precedence between explicit schedules and inflation adjustment.
- Preserve current behaviour when the option is disabled; change financial calculations only with focused evidence and regression coverage.

## Sprint 280 — Pension Funding and State Pension Forecasts

- Trace pension funding requirements through inflation forecasts and the State Pension triple-lock assumptions.
- Add scenario-based regression tests for the interaction of inflation, pension funding, and State Pension increases.
- Keep assumption/UI wiring distinct from the underlying forecast calculations and document any unsupported assumptions explicitly.


## Sprint 278 — GUI Assumptions Editor Coverage

- Add regression coverage for the GUI editor's documented actions and callback wiring.
- Verify validation and formatting are non-mutating; malformed nested schedules are rejected atomically.
- Exercise complete-document apply/save/reload with optional schedules and Unicode content.
- Explicitly distinguish headless controller/wiring tests from visible Tk UI and financial-calculation correctness.
- Preserve financial calculation logic, assumptions defaults, and the golden baseline.

## Sprint 279 — Inflation-Adjusted ISA Allowance (planned)

- Verify opt-in behavior and tax-year transition semantics before changing the implementation.
- Add boundary tests for tax-year-labelled allowance schedules and preserve existing behavior when disabled.
- Do not infer an allowance uprating rule where the assumptions or requirements do not define one.


### Sprint 279 — implementation addendum

- Set the shipped `inflation_link_isa` default to false, matching the opt-in requirement. Explicitly enabled behavior is preserved.
- Added regression coverage for default-off behavior, opt-in inflation, schedule start-year transitions, schedule/inflation composition, and proceeds capping.
- Documented the calendar-year limitation: the current projection timeline cannot model an intra-year 6 April tax-year transition.
- Updated the golden baseline only because the shipped default change intentionally affects the ISA/savings split and downstream balances.


### Sprint 280 — implementation addendum

- Added scenario regression coverage tracing projected-year CPI and scheduled earnings growth through State Pension increases and required pension income.
- Protected legacy fixed-growth behavior when triple lock is disabled, spouse eligibility timing, year-by-year compounding, and the zero floor for required pension income.
- Documented forecast semantics and limitations, including that the configured CPI/earnings forecasts are scenarios rather than predictions of future UK policy and that intra-year uprating/tax-year transitions are not modeled.
- No production financial calculation logic, assumption defaults, or golden baseline changed.

### Sprint 281 — End-to-End Scenario Integration

Status: implemented locally; awaiting full-suite acceptance.

- Validate full-planner scenario composition across inflation, State Pension policy and ISA inflation-link settings.
- Preserve deterministic behavior, timeline continuity, finite outputs, and shipped assumption-file immutability.
- No production financial calculations or defaults changed.


## Sprint 282 — Tax and Withdrawal Scenario Integration

- Added nine end-to-end tests for pension/ISA withdrawal strategy differences, gross/net tax reconciliation, pension-income caps, tax-free cash lifetime limits, exhausted-asset shortfalls, summary aggregation, and finite outputs.
- The tests characterize current behavior and are not tax advice or a claim that one strategy is universally optimal.
- No production financial calculations, assumption defaults, or golden baseline values changed.
- Focused Sprint 249 / 281 / 282 regression set: 27 passed. Full-suite acceptance remains pending user-side `python -m pytest -ra`.

**Current Sprint:** Sprint 282 — Tax and Withdrawal Scenario Integration

## Sprint 283 — Deterministic and Monte Carlo Parity

- Prove deterministic ending-assets parity with a single Monte Carlo iteration when investment and inflation volatility are zero and return assumptions are aligned.
- Protect seeded repeatability, percentile ordering, finite summary values, and different-seed variation when volatility is non-zero.
- Verify Monte Carlo does not mutate caller-owned assumptions.
- Keep deterministic and Monte Carlo return boundaries distinct; no financial formula or default changes.
- Focused Sprint 250 / 281 / 282 / 283 regression set: 31 passed; full-suite acceptance pending.

**Current Sprint:** Sprint 283 — Deterministic and Monte Carlo Parity


## Sprint 284 — Golden-Scenario Regression Pack

- Add reviewed golden snapshots for pension-first, ISA-first, and higher-inflation / State Pension triple-lock-off scenarios.
- Protect yearly projection fields and aggregate summaries with explicit schema, finite-value, contiguous-year, scenario-distinction, and fixture-immutability checks.
- Keep fixture regeneration out of test execution; require explicit review for intentional output changes.
- No production calculation logic, assumption defaults, or existing baseline values changed.
- Focused tests: 5 passed (3 scenario subtests); full-suite acceptance pending.

**Current Sprint:** Sprint 285 — Release Readiness


## Sprint 285 — Release Readiness (checkpoint pending full-suite acceptance)

- Added release-readiness traceability tests for the documented acceptance gates, manifest inventory, and unchanged shipped assumptions / existing golden baseline digests.
- Added `planner/docs/SPRINT285_RELEASE_READINESS.md` with the reproducible acceptance sequence and evidence limitations.
- Updated release manifest defaults and schema regression expectations to Sprint 285; added Sprint 285 artifacts to the package audit requirements.
- No production financial calculations, default assumptions, or golden baseline values changed.
- Focused validation and package audit results are recorded in the checkpoint; full-suite acceptance remains pending user-side `python -m pytest -ra`.

**Current Sprint:** Sprint 285 — Release Readiness

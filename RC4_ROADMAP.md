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

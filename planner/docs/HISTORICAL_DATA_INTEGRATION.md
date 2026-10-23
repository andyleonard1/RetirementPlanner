# Historical Market and Inflation Data — Integration Design (Sprint 256)

## Purpose and scope

This document defines the boundary for a future historical-replay feature. Sprint 256 adds a validation contract only: it does **not** connect a provider, replace `data/market_returns.csv`, invoke historical data from the planner, or change any projection calculation.

## Observation contract

Each annual record contains:

- `year`: calendar year as an integer.
- `equity_return`, `bond_return`, `inflation_rate`: finite decimal rates (`0.052` = 5.2%). Rates must be greater than `-1.0`; no implicit percent conversion is performed.
- `source_id` and `source_name`: non-empty provenance identifiers.
- `status`: `actual` or `estimated`; estimated observations must never be silently presented as actual.
- `currency`: three-character code, default `GBP`.
- `return_basis`: `nominal` or `real`; the series and its observations must agree.
- `source_url`: optional source reference, retained as provenance when supplied.

The `HistoricalSeriesContract` additionally requires a stable `series_id`, a human-readable description, and an explicit missing-year policy (`reject` or `allow_gaps`).

## Validation and import rules

1. Validate source metadata and raw values before conversion into engine-specific models.
2. Reject booleans, non-numeric values, NaN/infinity and rates at or below -100%.
3. Reject duplicate calendar years.
4. Under `reject`, any missing year between the earliest and latest supplied years is an error. `allow_gaps` preserves gaps as gaps; it does not interpolate, repeat, or fabricate data.
5. Keep source status and provenance attached to each observation. Do not blend actual and estimated records without an explicit downstream choice.
6. Never infer nominal/real basis, currency, units, or missing-year treatment from a file name.
7. Historical replay must be opt-in and separate from the existing deterministic and Monte Carlo paths until a later sprint defines and tests the engine integration.

## Proposed integration sequence

- **Sprint 256 (this sprint):** typed data contract, validation, and documentation.
- **Sprint 257 (implemented):** provider-neutral source adapter protocol and strict version-1 JSON fixture loader; no default provider or calculation path.
- **Sprint 258 (implemented):** test collection diagnostics and environment fingerprinting. This was a validation/packaging sprint and did not add replay behaviour.
- **Sprint 259 (implemented):** standalone, opt-in historical replay utility over an explicit contiguous year window, with weighted equity/bond returns, cumulative inflation adjustment, and explicit opt-in for estimated observations. It is not connected to production projection or Monte Carlo paths.

## Versioned fixture format (Sprint 257)

The fixture format identifier is `retirement-planner-historical-series` with an integer `format_version` of `1`. The root object contains exactly `format`, `format_version`, `contract`, and `observations`; contract and observation objects reject unknown fields. The sample `tests/fixtures/historical_returns_v1.json` is explicitly synthetic and must not be used as investment data. `HistoricalDataSourceAdapter` is a provider-neutral protocol only; no live provider is implemented or selected.

## Acceptance boundary

Contract tests cover valid records, provenance/status, numeric validity, duplicate years, missing years, currency/basis consistency, and the no-coercion/no-fabrication rule. Existing market CSV loading and all financial calculation logic remain unchanged.

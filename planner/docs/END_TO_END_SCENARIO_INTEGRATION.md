# Sprint 281 — End-to-End Scenario Integration

## Scope

This sprint adds full-planner regression coverage for the interaction of the existing assumptions and calculation engines. It exercises the normal `RetirementPlanner.run()` boundary and compares independently constructed scenarios.

## Coverage

- Complete, contiguous calendar-year timelines.
- Repeatability of the deterministic default projection.
- Higher inflation flowing into future spending and required pension funding.
- State Pension triple-lock policy changing the full projection when the toggle changes.
- The ISA inflation-link opt-in affecting the full projection without changing the default setting.
- Finite financial outputs across the projection horizon.
- Scenario execution not mutating the shipped `data/assumptions.json` file.

## Compatibility and limitations

The tests exercise existing calculation behavior; this sprint does not add or change financial formulas, policy assumptions, default values, or golden-scenario values. The comparisons establish integration and regression properties, not forecasts of actual future returns, inflation, or government policy.

## Validation status

The focused scenario integration, Sprint 280 pension forecast, Sprint 279 ISA allowance, and Sprint 252 golden-scenario tests passed in the build environment. The full suite must still be run on the user's target environment; collection counts are not pass counts.

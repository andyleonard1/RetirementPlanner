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

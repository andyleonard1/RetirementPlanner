# Version 0.1
- Initial pension projection

# Version 0.2
- Timeline engine
- RetirementYear model

# Version 0.3
- Planner orchestration
- State Pension engine
- Reporting layer

# Version 0.4
- Savings engine

## Sprint 229
- Hardened GoalEngine result-boundary validation.
- Added six regression tests.
- No retirement calculation logic changed.

## Sprint 230

### Complete Assumption Catalog and GUI Coverage Hardening

- Completed top-level audit-catalog coverage for required and optional assumptions.
- Added end-to-end regression coverage for the complete GUI assumptions JSON round-trip.
- No financial calculation semantics changed.

## Sprint 231
### Assumption Operational Coverage and Legacy Boundary Catalogue

- Added an explicit operational-role catalogue for every schema-defined assumption.
- Distinguished live projection inputs, Monte Carlo inputs, legacy compatibility aliases, auxiliary configuration and goal-domain configuration.
- Added four regression tests guarding complete role coverage.
- No financial calculation semantics changed.
- Full suite: **1167 tests passed, 9 subtests** across four validated partitions (292 + 292 + 292 + 291).

## Sprint 232
### Assumption Consumer Boundary Hardening

- Added an explicit consumer-boundary catalogue for operational assumption roles.
- Added four regression tests covering complete role-to-consumer coverage and importability.
- Preserved legacy and auxiliary assumption boundaries without changing financial calculations.
- Full suite: **1171 tests passed, 9 subtests** across four validated partitions (293 + 293 + 293 + 292).

## Sprint 239
### Canonical Assumption Consumer Boundary Audit Hardening

- Added explicit resolver accessors for selected remaining canonical calculation assumptions.
- Routed State Pension, ISA/investment-return, Monte Carlo and validation consumers through the canonical boundary.
- Added four regression tests guarding the consumer boundary.
- Preserved existing financial calculation semantics and legacy compatibility.
- Full regression: **1198 tests passed** across validated test groups.

# Release Notes

## 2.0 RC2 — Architecture Stabilisation

### Architecture

- Consolidated the planner around explicit calculation and analysis engines.
- Introduced typed result objects at major analysis boundaries.
- Added structural engine contracts using `typing.Protocol`.
- Consolidated optimisation traversal into `OptimisationEngine`.
- Added compatibility aliases where required during migration.

### Reporting

- Professional PDF reporting is operational.
- Recommendation and health-report entry points use the current recommendation architecture.
- Chart generation is integrated with PDF reporting.

### Engineering

- Engine diagnostics use Python logging.
- Public interfaces are progressively typed.
- Golden-scenario and regression tests protect existing calculation behaviour.

### Current validation checkpoint

**131 tests passing** at the start of the documentation-consolidation sprint.

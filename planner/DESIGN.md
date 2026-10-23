# Retirement Planner Design Notes

## Project goal

Provide a transparent, testable UK retirement-planning model that separates financial calculations from decision analysis and presentation.

## Requirements

The system should:

- project retirement finances year by year;
- model pension, ISA, savings, tax and State Pension components;
- compare alternative retirement ages;
- expose assumptions clearly;
- support scenario, sensitivity and probabilistic analysis;
- produce repeatable reports;
- preserve calculation behaviour through regression testing.

## Architecture

The architecture is engine-driven:

**Applications → Planner/Scenarios → Calculation Engines → Analysis Engines → Reports**

See `planner/docs/ARCHITECTURE.md` for the detailed dependency rules and `planner/docs/ENGINE_CATALOG.md` for component responsibilities.

## Completed architecture work

- Result-object standardisation
- Optimisation framework consolidation
- Logging consistency
- Typed engine contracts
- Legacy recommendation/report migration

## Future ideas

- broader optimisation suite
- historical market replay
- richer adviser reporting
- interactive user interface

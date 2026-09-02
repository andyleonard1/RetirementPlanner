# Retirement Planner

**Version:** 2.0 RC2  
**Architecture branch:** `rc2-architecture`

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

- `planner/docs/ARCHITECTURE.md` — architecture and dependency rules
- `planner/docs/ENGINE_CATALOG.md` — engine responsibilities and interfaces
- `planner/docs/CODING_STANDARDS.md` — implementation conventions
- `planner/docs/assumptions.md` — assumptions/configuration reference
- `planner/docs/ROADMAP.md` — release roadmap

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

Current checkpoint: **198 tests passing**.

## Development approach

This project uses incremental sprints. Each sprint should preserve the previous passing-test checkpoint, avoid unnecessary rewrites, and leave the calculation behaviour unchanged unless the sprint explicitly targets a calculation rule.

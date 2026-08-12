# Retirement Planner

## Current Version

2.0 RC2

## Current Sprint

Sprint 34 - Sensitivity Reporting

## Branch

rc2-architecture

## Build Status

| Application | Status |
|-------------|--------|
| main.py | ✅ |
| monte_carlo.py | ✅ |
| health_check.py | ✅ |
| compare.py | ✅ |

---

## Completed

- Retirement timeline
- Pension engine
- ISA engine
- Savings engine
- Tax engine
- Cash Flow engine
- Withdrawal engine
- Summary engine
- Recommendation engine
- Health engine
- Goal engine
- Monte Carlo simulation
- PDF report
- Sensitivity analysis reporting
- Charts
- Optimisation prototype

---

## Technical Debt

### High

- Standardise result objects
- Consolidate optimisation framework

### Medium

- Logging consistency
- Typed interfaces
- Engine contracts

### Low

- Documentation expansion
- Test coverage improvements

---

## Engineering Score

Architecture        8.6 / 10

Maintainability     8.0 / 10

Extensibility       9.0 / 10

Documentation       6.0 / 10

Testing             5.5 / 10

Overall             8.6 / 10
## Sensitivity checkpoint 23
- 27 real planner cases executed.
- Recommended ages: 56 (18 cases), 58 (3 cases), 67 (6 cases).
- Range: 56-67.
- Informational only; live recommendation unchanged.

## Sensitivity reporting checkpoint 24
- 27 real planner cases are calculated during PDF report generation.
- Recommended ages: 56 (18 cases), 58 (3 cases), 67 (6 cases).
- Range: 56-67.
- Driver breakdown for pension growth, net spending and ISA growth is included in the PDF.
- Sensitivity remains informational only; the live recommendation is unchanged.
- Full test suite: 115 tests passing.

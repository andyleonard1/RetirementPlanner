# RC4 Assumption Boundary

This document records the frozen assumption-access contract established through Sprint 244.
It is deliberately calculation-free: the purpose is to document which layer owns compatibility, precedence and validation so future changes do not silently alter financial behaviour.

## 1. Canonical boundary

New planner calculation code should obtain assumptions through `planner.assumption_resolver.AssumptionResolver` rather than reading configuration keys directly when a resolver accessor exists.

| Domain | Canonical access | Legacy compatibility |
|---|---|---|
| Inflation | `inflation_rate` | `inflation` |
| Savings interest | `savings_interest_rate` | `savings_interest` |
| Deterministic investment return | `expected_investment_return` | `pension_growth` |

When both canonical and legacy values are present, the canonical value wins. Legacy values remain supported for compatibility but are resolver-owned.

## 2. Monte Carlo return boundary

Monte Carlo has a deliberately different precedence contract because its `expected_return` is the stochastic mean, while `expected_investment_return` is the deterministic projection return:

1. `expected_return`
2. `expected_investment_return`
3. `pension_growth`

Do not collapse this sequence into the ordinary canonical/legacy alias map.

## 3. Validation contract

Numeric resolver accessors reject booleans, non-numeric values and non-finite values. Required numeric assumptions raise an explicit `ValueError` when no usable value is available.

Optional resolver accessors retain their existing defaults. This boundary validates the selected configuration value; it does not change downstream financial calculations.

## 4. Change protocol

Before changing an assumption key, precedence rule or resolver accessor:

1. Update the schema/catalogue documentation if the configuration contract changes.
2. Add or update focused resolver regression tests.
3. Search planner consumers for direct access to the affected key.
4. Run the focused assumption regression set.
5. Run the complete discovered suite in independently verifiable partitions.
6. Record the sprint, test count and deliberately unchanged calculation areas in `RC4_ROADMAP.md` and `PROJECT_STATUS.md`.
7. Create a named ZIP checkpoint before moving to the next sprint.

## 5. Deliberately unchanged areas

The assumption-boundary work does not redefine retirement, tax, State Pension, ISA, savings, withdrawal, investment-return, inflation, Monte Carlo or goal calculation formulas. Configuration-access changes must preserve those downstream semantics unless a future sprint explicitly states otherwise and adds dedicated financial-behaviour regressions.

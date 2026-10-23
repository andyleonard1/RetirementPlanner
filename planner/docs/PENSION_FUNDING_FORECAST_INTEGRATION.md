# Pension Funding and State Pension Forecast Integration — Sprint 280

## Purpose

Sprint 280 adds regression coverage for the boundary between projected inflation, State Pension annual increases, and the cash-flow engine's required pension income. It does not introduce a new forecast rule.

## Current behavior verified

- With the State Pension triple lock enabled, each projected year's `inflation_rate` is used when present; the configured base inflation rate is the fallback.
- The annual increase is the maximum of the selected year's CPI, that year's scheduled/base earnings growth, and 2.5%.
- A matching earnings-growth schedule entry overrides the base earnings-growth forecast for that calendar year; a missing entry falls back to the base rate.
- With the triple lock disabled, the legacy `state_pension_growth` rate is used.
- State Pension amounts are accumulated by age and assigned from age 67 for the primary person and age 69 for the spouse.
- CashFlowEngine inflates the selected spending target when `inflation_link_spending` is enabled, then computes `required_pension_income = max(0, target_spending - cash_available)`. Cash available includes savings interest and both State Pension amounts.

## Explicit limitations

The triple-lock forecast is a scenario model driven by the configured CPI and earnings-growth forecasts, not a claim to predict future UK policy or actual annual earnings/CPI observations. The current calendar-year projection does not model the intra-year State Pension uprating date or a detailed 6 April tax-year transition. This sprint does not change pension drawdown, tax, or investment-return formulas.

## Validation

Run the focused tests with:

```bash
python -m pytest -q tests/test_sprint280_pension_funding_forecast_integration.py tests/test_sprint215_state_pension_triple_lock.py tests/test_sprint217_state_pension_forecast_schedule.py tests/test_sprint248_schedule_interaction_hardening.py
```

Collection and release-evidence reports describe test inventory and artifact consistency; neither substitutes for executing the full test suite.

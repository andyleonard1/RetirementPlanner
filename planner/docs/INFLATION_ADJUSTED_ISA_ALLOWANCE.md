# Inflation-adjusted ISA allowance

## Default and opt-in

The shipped `inflation_link_isa` setting defaults to `false`. With the setting off, the configured ISA allowance remains nominal, even when the projection's inflation factor exceeds 1.0. Set `inflation_link_isa` to `true` to apply the projected year's compounded inflation factor to the allowance.

The adjusted amount remains capped by actual property-sale proceeds. This switch only affects the property-sale ISA-sheltering allowance; it does not independently change other ISA contributions or ISA investment returns.

## Allowance schedules and tax-year transitions

`isa_allowance_schedule_enabled` separately controls whether `isa_allowance_schedule` values are used. Schedule keys use `YYYY/YY` tax-year labels. The engine resolves the most recent configured schedule start year at or before the projection calendar year; before the first configured entry, it falls back to `annual_isa_allowance`. A future entry does not apply before its start year.

The schedule and inflation link are separate layers:

- Schedule disabled: use `annual_isa_allowance`.
- Schedule enabled: use the latest applicable scheduled allowance, or the nominal fallback before the first schedule entry.
- Inflation link enabled: scale whichever allowance was selected by the year's `inflation_factor`.
- Inflation link disabled: retain the selected nominal allowance.

The current timeline stores a calendar year, not a month/day. Accordingly, schedule selection uses the schedule's start-year boundary; it does not model an intra-calendar-year 6 April transition. Do not interpret this as a month-precise UK tax-year engine.

## Validation and regression coverage

Run `python -m pytest -q tests/test_sprint279_inflation_adjusted_isa_allowance.py tests/test_sprint213_inflation_isa_calculation_wiring.py tests/test_sprint214_isa_allowance_schedule.py`. The focused tests cover default-off behavior, explicit opt-in, schedule transition boundaries, independent schedule and inflation controls, and proceeds capping. The golden baseline is intentionally updated for the new shipped default; explicit opt-in calculation behavior remains covered by existing tests.

"""Operational role catalogue for the public assumptions document.

This catalogue deliberately does not change calculation behaviour.  It makes
explicit how each schema-defined assumption participates in the application:
active projection input, stochastic/sensitivity input, compatibility alias,
or configuration/reporting input.
"""
from __future__ import annotations

from planner.assumptions_schema import AssumptionsSchema

# Values are stable machine-readable roles for audit/documentation consumers.
# Every schema-defined top-level key must be classified here so newly added
# assumptions cannot silently become GUI-visible but calculation-ambiguous.
ROLES = {
    # Core deterministic projection inputs.
    "withdrawal_strategy": "projection",
    "current_age": "projection",
    "retirement_age": "projection",
    "projection_end_age": "projection",
    "spouse_current_age": "projection",
    "max_pension_income": "projection",
    "starting_pension": "projection",
    "expected_investment_return": "projection",
    "platform_charge": "projection",
    "fund_charge": "projection",
    "starting_savings": "projection",
    "savings_interest_rate": "projection",
    "personal_allowance": "projection",
    "basic_rate_limit": "projection",
    "basic_rate": "projection",
    "higher_rate": "projection",
    "additional_rate": "projection",
    "tax_free_pension_percentage": "projection",
    "starting_isa": "projection",
    "isa_growth_rate": "projection",
    "annual_isa_allowance": "projection",
    "property_sale": "projection",
    "property_sale_age": "projection",
    "state_pension_full": "projection",
    "current_calendar_year": "projection",
    "state_pension_growth": "projection",
    "state_pension_earnings_growth": "projection",
    "state_pension_triple_lock_enabled": "projection",
    "state_pension_earnings_growth_schedule_enabled": "projection",
    "state_pension_earnings_growth_schedule": "projection",
    "annual_spending_schedule_enabled": "projection",
    "annual_spending_schedule": "projection",
    "investment_return_schedule_enabled": "projection",
    "investment_return_schedule": "projection",
    "isa_return_schedule_enabled": "projection",
    "isa_return_schedule": "projection",
    "spending_phase_1": "projection",
    "spending_phase_2": "projection",
    "spending_phase_3": "projection",
    "phase_1_end_age": "projection",
    "phase_2_end_age": "projection",
    "inflation_rate": "projection",
    "inflation_link_spending": "projection",
    "inflation_link_tax": "projection",
    "inflation_link_isa": "projection",
    "isa_allowance_schedule_enabled": "projection",
    "isa_allowance_schedule": "projection",

    # Stochastic simulation inputs.
    "expected_return": "monte_carlo",
    "investment_volatility": "monte_carlo",
    "inflation_volatility": "monte_carlo",

    # Retained historical names with explicit canonical resolver boundaries.
    "inflation": "legacy_compatibility",
    "savings_interest": "legacy_compatibility",
    "pension_growth": "legacy_compatibility",

    # Auxiliary/sensitivity configuration retained in the public assumptions
    # document but not used as the live age-based spending target.
    "target_net_income": "auxiliary",

    # Goal definitions are consumed by GoalEngine and downstream reports,
    # rather than directly by the financial projection engines.
    "goals": "goals",
}


def role(path: str) -> str:
    """Return the operational role for a top-level assumption path."""
    if path.startswith("goals["):
        return "goals"
    return ROLES[path]


def schema_paths() -> tuple[str, ...]:
    """Return all schema-defined top-level assumption paths."""
    return tuple(sorted(
        AssumptionsSchema.REQUIRED_KEYS
        | AssumptionsSchema.OPTIONAL_BOOLS
        | AssumptionsSchema.OPTIONAL_OBJECTS
    ))


def unclassified_schema_paths() -> tuple[str, ...]:
    """Return schema-defined paths that have no explicit operational role."""
    return tuple(path for path in schema_paths() if path not in ROLES)

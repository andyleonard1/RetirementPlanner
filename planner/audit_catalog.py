"""
Audit metadata catalogue.

Provides a single source of truth for human-readable descriptions of
configuration changes. The catalogue is deliberately independent of the
financial calculation engines.
"""

from __future__ import annotations

from planner.assumptions_schema import AssumptionsSchema


DESCRIPTIONS = {
    "current_age": "Current age changed for this projection.",
    "retirement_age": "Retirement age changed for this projection.",
    "projection_end_age": "Projection end age changed for this projection.",
    "spouse_current_age": "Spouse current age changed for this projection.",
    "max_pension_income": "Maximum pension income changed for this projection.",
    "starting_pension": "Starting pension value changed for this projection.",
    "expected_investment_return": "Expected investment return changed for this projection.",
    "platform_charge": "Platform charge changed for this projection.",
    "fund_charge": "Fund charge changed for this projection.",
    "target_net_income": "Target net income changed for this projection.",
    "starting_savings": "Starting savings changed for this projection.",
    "savings_interest_rate": "Savings interest rate changed for this projection.",
    "inflation": "Inflation assumption changed for this projection.",
    "personal_allowance": "Personal allowance changed for this projection.",
    "basic_rate_limit": "Basic-rate tax limit changed for this projection.",
    "basic_rate": "Basic income-tax rate changed for this projection.",
    "higher_rate": "Higher income-tax rate changed for this projection.",
    "additional_rate": "Additional income-tax rate changed for this projection.",
    "pension_growth": "Pension growth assumption changed for this projection.",
    "expected_return": "Expected return assumption changed for this projection.",
    "investment_volatility": "Investment volatility assumption changed for this projection.",
    "inflation_volatility": "Inflation volatility assumption changed for this projection.",
    "savings_interest": "Savings interest assumption changed for this projection.",
    "tax_free_pension_percentage": "Tax-free pension percentage changed for this projection.",
    "starting_isa": "Starting ISA value changed for this projection.",
    "isa_growth_rate": "ISA growth rate changed for this projection.",
    "annual_isa_allowance": "Annual ISA allowance changed for this projection.",
    "property_sale": "Property sale proceeds changed for this projection.",
    "property_sale_age": "Property sale age changed for this projection.",
    "state_pension_full": "Full state pension assumption changed for this projection.",
    "current_calendar_year": "Current calendar year changed for this projection.",
    "state_pension_growth": "State pension growth assumption changed for this projection.",
    "spending_phase_1": "First spending phase changed for this projection.",
    "spending_phase_2": "Second spending phase changed for this projection.",
    "spending_phase_3": "Third spending phase changed for this projection.",
    "phase_1_end_age": "First spending phase end age changed for this projection.",
    "phase_2_end_age": "Second spending phase end age changed for this projection.",
    "inflation_rate": "Inflation rate assumption changed for this projection.",
    "withdrawal_strategy": "Withdrawal strategy changed for this projection.",
    "inflation_link_spending": "Spending inflation-link setting changed for this projection.",
    "inflation_link_tax": "Tax inflation-link setting changed for this projection.",
    "inflation_link_isa": "ISA inflation-link setting changed for this projection.",
    "goals": "Retirement goals configuration changed for this projection.",
}

DESCRIPTIONS = dict(sorted(DESCRIPTIONS.items()))


def description(path: str, context: str = "user") -> str:
    """Return a human-readable description for an audited configuration path."""
    if path == "retirement_age":
        return {
            "scenario": "Retirement age selected for scenario analysis.",
            "recommendation": "Retirement age evaluated by the recommendation solver.",
            "analysis": "Retirement age changed for analytical comparison.",
        }.get(context, DESCRIPTIONS[path])

    if path.startswith("goals["):
        if ".target" in path:
            return "Retirement goal target changed for this projection."
        if ".name" in path:
            return "Retirement goal name changed for this projection."
        if ".type" in path:
            return "Retirement goal type changed for this projection."
        return "Retirement goal configuration changed for this projection."

    return DESCRIPTIONS.get(path, f"Assumption '{path}' changed for this projection.")


def has_description(path: str) -> bool:
    """Return whether the catalogue explicitly describes a schema path."""
    if path in DESCRIPTIONS:
        return True
    if path.startswith("goals[") and any(
        token in path for token in (".target", ".name", ".type")
    ):
        return True
    return False


def schema_paths() -> tuple[str, ...]:
    """Return all schema-defined top-level assumption paths."""
    return tuple(sorted(AssumptionsSchema.REQUIRED_KEYS))

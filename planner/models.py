ffrom dataclasses import dataclass


@dataclass
class RetirementYear:
    """
    Represents one year of retirement.
    Every engine will add data to this object.
    """

    age: int
    calendar_year: int
    spouse_age: int

    # Pension
    opening_pension: float = 0.0
    pension_growth: float = 0.0
    pension_withdrawal: float = 0.0
    closing_pension: float = 0.0

    # State Pension
    your_state_pension: float = 0.0
    spouse_state_pension: float = 0.0

    # Savings
    savings_opening: float = 0.0
    savings_interest: float = 0.0
    savings_closing: float = 0.0

    # ISA
    isa_opening: float = 0.0
    isa_growth: float = 0.0
    isa_contribution: float = 0.0
    isa_closing: float = 0.0

    # Tax
    taxable_income: float = 0.0
    income_tax: float = 0.0

    # Income
    household_net_income: float = 0.0

    # Summary
    total_assets: float = 0.0
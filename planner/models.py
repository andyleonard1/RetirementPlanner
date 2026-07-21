from dataclasses import dataclass


@dataclass
class RetirementYear:
    """
    Represents one year of retirement.
    Every engine will add data to this object.
    """

    age: int
    calendar_year: int
    spouse_age: int

    # Strategy
    non_pension_income_used: float = 0.0
    cash_savings_used: float = 0.0
    isa_used: float = 0.0
    net_pension_required: float = 0.0
    surplus_cash: float = 0.0
    unmet_spending: float = 0.0
    interest_used: float = 0.0
    cash_used: float = 0.0
    isa_used: float = 0.0
    pension_needed: float = 0.0

    surplus_cash: float = 0.0

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
    savings_money_in: float = 0.0
    savings_money_out: float = 0.0
    savings_closing: float = 0.0
    isa_transfer: float = 0.0

    # ISA
    isa_opening: float = 0.0
    isa_growth: float = 0.0
    isa_contribution: float = 0.0
    isa_closing: float = 0.0
    
    # Tax
    taxable_income: float = 0.0
    
    # Pension tax
    gross_pension_income: float = 0.0
    taxable_pension_income: float = 0.0
    income_tax: float = 0.0
    net_pension_income: float = 0.0
    
    # Income
    household_net_income: float = 0.0
    target_spending: float = 0.0
    income_shortfall: float = 0.0
    # Inflation
    inflation_factor: float = 1.0
    
    # Cash Flow
    cash_available: float = 0.0
    cash_to_isa: float = 0.0
    cash_spent: float = 0.0
    cash_remaining: float = 0.0
    # Income Sources
    interest_used: float = 0.0
    savings_used: float = 0.0
    isa_used: float = 0.0
    pension_needed: float = 0.0

    # Remaining balances after withdrawals
    savings_remaining: float = 0.0
    isa_remaining: float = 0.0
    # Summary
    total_assets: float = 0.0
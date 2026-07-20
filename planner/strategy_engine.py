"""
Strategy Engine

Determines where retirement income should come from.

Version 1

Priority:

1. Savings interest
2. Pension
"""

class StrategyEngine:

    def __init__(self, assumptions):
        self.assumptions = assumptions

    def apply(self, timeline):

        for year in timeline:

            #
            # Spending target
            #
            need = year.target_spending

            #
            # Use available cash first
            #
            interest = year.cash_available

            interest_used = min(need, interest)

            remaining = need - interest_used

            #
            # Pension funds the remainder
            #
            pension = max(0, remaining)

            #
            # Save plan
            #
            year.interest_used = round(interest_used, 2)
            year.pension_needed = round(pension, 2)

            year.surplus_cash = round(
                year.cash_available - interest_used,
                2,
            )

        return timeline
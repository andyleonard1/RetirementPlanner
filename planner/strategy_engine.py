"""
Strategy Engine

Determines where retirement income should come from.

Priority:

1. Savings Interest
2. Savings Capital
3. ISA
4. Pension
"""

class StrategyEngine:

    def __init__(self, assumptions):
        self.assumptions = assumptions

    def apply(self, timeline):

        for year in timeline:

            need = year.target_spending

            for year in timeline:

                need = year.target_spending

                #
                # Use available cash first
                #
                cash_used = min(need, year.cash_available)

                remaining = need - cash_used

                #
                # Pension maximum
                #
                pension_limit = self.assumptions.get("max_pension_income")

                pension = min(remaining, pension_limit)

                remaining -= pension

                #
                # ISA funds whatever is left
                #
                isa = max(0, remaining)

                year.interest_used = cash_used
                year.pension_needed = pension
                year.isa_used = isa
                year.pension_needed = round(pension, 2)

                        #
                        # Remaining balances
                        #
                year.savings_remaining = round(
                            year.savings_closing - savings,
                            2,
                        )

                year.isa_remaining = round(
                            year.isa_closing - isa,
                            2,
                        )
        return timeline
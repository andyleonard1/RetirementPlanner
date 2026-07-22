"""
Strategy Engine

Determines where retirement income should come from.

Priority

1. Cash available (interest + state pension)
2. Pension (up to a limit)
3. ISA
"""


class StrategyEngine:

    def __init__(self, assumptions):
        self.assumptions = assumptions

    def apply(self, timeline):

        pension_limit = self.assumptions.get("max_pension_income")

        for year in timeline:

            need = year.target_spending

            #
            # Use cash first
            #
            cash_used = min(need, year.cash_available)

            remaining = need - cash_used

            #
            # Then pension
            #
            pension = min(remaining, pension_limit)

            remaining -= pension

            #
            # Finally ISA
            #
            isa = max(0, remaining)

            #
            # Save decisions
            #
            year.interest_used = round(cash_used, 2)
            year.pension_needed = round(pension, 2)
            year.isa_used = round(isa, 2)

            #
            # Remaining balances
            #
            year.savings_remaining = year.savings_closing
            year.isa_remaining = round(
                year.isa_closing - isa,
                2,
            )

        return timeline
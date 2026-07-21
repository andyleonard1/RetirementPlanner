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

            #
            # 1. Interest
            #
            interest = min(need, year.cash_available)

            need -= interest

            #
            # 2. Savings
            #
            savings = min(need, year.savings_closing)

            need -= savings

            #
            # 3. ISA
            #
            isa = min(need, year.isa_closing)

            need -= isa

            #
            # 4. Pension
            #
            pension = max(0, need)

            #
            # Store decisions
            #
            year.interest_used = round(interest, 2)
            year.savings_used = round(savings, 2)
            year.isa_used = round(isa, 2)
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
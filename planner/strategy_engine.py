"""
Strategy Engine

Determines where retirement income should come from.

Supported strategies

PENSION_FIRST
    Cash
    Pension
    ISA

ISA_FIRST
    Cash
    ISA
    Pension
"""


class StrategyEngine:

    def __init__(self, assumptions):
        self.assumptions = assumptions

    def apply(self, timeline):

        strategy = self.assumptions.get("withdrawal_strategy")

        for year in timeline:

            #
            # Maximum pension for this year
            # (calculated by TaxOptimizerEngine)
            #
            pension_limit = year.maximum_tax_efficient_pension

            #
            # Spending required
            #
            need = year.target_spending

            #
            # Cash available (interest + state pensions)
            #
            cash_used = min(need, year.cash_available)

            remaining = need - cash_used

            #
            # Choose withdrawal strategy
            #
            if strategy == "ISA_FIRST":

                #
                # Use ISA first
                #
                isa = min(
                    remaining,
                    year.isa_closing,
                )

                remaining -= isa

                pension = min(
                    remaining,
                    pension_limit,
                )

            else:
                #
                # Default = Pension First
                #
                pension = min(
                    remaining,
                    pension_limit,
                )

                remaining -= pension

                isa = max(
                    0.0,
                    remaining,
                )

            #
            # Save decisions
            #
            year.interest_used = round(cash_used, 2)

            year.pension_needed = round(pension, 2)

            year.isa_used = round(isa, 2)

            #
            # Remaining balances
            #
            year.savings_remaining = round(
                year.savings_closing,
                2,
            )

            year.isa_remaining = round(
                max(
                    0.0,
                    year.isa_closing - isa,
                ),
                2,
            )

        return timeline
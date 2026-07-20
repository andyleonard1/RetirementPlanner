"""
Cash Flow Engine

Calculates the household cash available each retirement year
and determines any income shortfall.
"""


class CashFlowEngine:

    def __init__(self, assumptions):
        self.assumptions = assumptions

    def apply(self, timeline):

        for year in timeline:

            # --------------------------------------------------
            # Determine annual spending target
            # --------------------------------------------------

            if year.age <= self.assumptions.get("phase_1_end_age"):
                year.target_spending = self.assumptions.get("spending_phase_1")

            elif year.age <= self.assumptions.get("phase_2_end_age"):
                year.target_spending = self.assumptions.get("spending_phase_2")

            else:
                year.target_spending = self.assumptions.get("spending_phase_3")

            # --------------------------------------------------
            # Calculate available cash income
            # --------------------------------------------------

            year.cash_available = round(
                year.savings_interest
                + year.your_state_pension
                + year.spouse_state_pension,
                2,
            )

            # --------------------------------------------------
            # Calculate remaining income required
            # --------------------------------------------------

            year.income_shortfall = round(
                max(
                    0,
                    year.target_spending - year.cash_available,
                ),
                2,
            )

            # --------------------------------------------------
            # Nothing has been allocated yet
            # (WithdrawalEngine will decide this)
            # --------------------------------------------------

            year.cash_to_isa = 0.0
            year.cash_spent = 0.0
            year.cash_remaining = year.cash_available

        return timeline
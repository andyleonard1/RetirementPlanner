"""
Cash Flow Engine

Calculates available household income and determines
the inflation-adjusted spending target.
"""
import logging

logger = logging.getLogger(__name__)
class CashFlowEngine:

    def __init__(self, assumptions):
        self.assumptions = assumptions

    def apply(self, timeline):
        logger.info("Running WithdrawalEngine")
        phase1_end = self.assumptions.get("phase_1_end_age")
        phase2_end = self.assumptions.get("phase_2_end_age")

        spending1 = self.assumptions.get("spending_phase_1")
        spending2 = self.assumptions.get("spending_phase_2")
        spending3 = self.assumptions.get("spending_phase_3")

        inflate = self.assumptions.get("inflation_link_spending")

        for year in timeline:

            #
            # Base spending for this phase
            #
            if year.age <= phase1_end:
                spending = spending1

            elif year.age <= phase2_end:
                spending = spending2

            else:
                spending = spending3

            #
            # Inflate spending if enabled
            #
            if inflate:
                spending *= year.inflation_factor

            year.target_spending = round(spending, 2)

            #
            # Cash income available before withdrawals
            #
            year.cash_available = round(
                year.savings_interest
                + year.your_state_pension
                + year.spouse_state_pension,
                2,
            )

            #
            # Legacy field (kept for compatibility)
            #
            year.required_pension_income = max(
                0,
                year.target_spending - year.cash_available,
            )

            #
            # Strategy Engine will decide where
            # the remainder comes from.
            #
            year.cash_to_isa = 0.0
            year.cash_spent = 0.0
            year.cash_remaining = year.cash_available

        return timeline
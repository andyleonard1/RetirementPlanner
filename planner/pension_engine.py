"""
Pension Engine

Calculates pension growth and withdrawals for each retirement year.

This engine does not create RetirementYear objects.
Instead, it updates the timeline created by TimelineEngine.
"""
import logging

logger = logging.getLogger(__name__)

class PensionEngine:

    def __init__(self, assumptions):

        self.assumptions = assumptions

        self.starting_pension = assumptions.get("starting_pension")
        self.growth_rate = assumptions.get("pension_growth")

    def apply(self, timeline):
        logger.info("Running PensionEngine")
        pension = self.starting_pension

        for year in timeline:

            opening = pension

            growth = opening * self.growth_rate

            # Withdrawal is now decided by WithdrawalEngine
            withdrawal = year.pension_withdrawal
            
            closing = opening + growth - withdrawal

            year.opening_pension = round(opening, 2)
            year.pension_growth = round(growth, 2)
            year.pension_withdrawal = round(withdrawal, 2)
            year.closing_pension = round(closing, 2)

            pension = closing

        return timeline
"""
Withdrawal Engine

Executes the withdrawal decision made by StrategyEngine.
"""
import logging

logger = logging.getLogger(__name__)

class WithdrawalEngine:

    def __init__(self, assumptions):
        self.assumptions = assumptions

    def apply(self, timeline):
        logger.info("Running Withdrawal Engine")
        for year in timeline:
            year.pension_withdrawal = year.pension_needed

        return timeline
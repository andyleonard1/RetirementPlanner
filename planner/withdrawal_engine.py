"""
Withdrawal Engine

Executes the withdrawal decision made by StrategyEngine.
"""
import logging

from planner.contracts import AssumptionsProvider, Timeline

logger = logging.getLogger(__name__)

class WithdrawalEngine:

    def __init__(self, assumptions: AssumptionsProvider):
        self.assumptions = assumptions

    def apply(self, timeline: Timeline) -> Timeline:
        logger.info("Running Withdrawal Engine")
        for year in timeline:
            year.pension_withdrawal = year.pension_needed

        return timeline
"""
Summary Engine

Calculates summary statistics for the completed retirement plan.
"""

import logging

logger = logging.getLogger(__name__)


class SummaryEngine:

    def __init__(self, assumptions):
        self.assumptions = assumptions

    def apply(self, timeline):

        logger.info("Running Summary Engine")

        final = timeline[-1]

        summary = {
            "ending_pension": final.closing_pension,
            "ending_savings": final.savings_closing,
            "ending_isa": final.isa_closing,
            "ending_assets": (
                final.closing_pension
                + final.savings_closing
                + final.isa_closing
            ),

            "gross_pension": sum(
                y.gross_pension_income
                for y in timeline
            ),

            "net_pension": sum(
                y.net_pension_income
                for y in timeline
            ),

            "state_pension": sum(
                y.your_state_pension
                + y.spouse_state_pension
                for y in timeline
            ),

            "total_tax": sum(
                y.income_tax
                for y in timeline
            ),

            "strategy": self.assumptions.get(
                "withdrawal_strategy"
            ),
        }

        return summary
        
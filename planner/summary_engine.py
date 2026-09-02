"""
Summary Engine

Calculates summary statistics for the completed retirement plan.
"""

import logging

from planner.contracts import AssumptionsProvider, SummaryEngineProtocol, Timeline

logger = logging.getLogger(__name__)


class SummaryEngine:

    def __init__(self, assumptions: AssumptionsProvider):

        self.assumptions = assumptions

    def apply(self, timeline: Timeline) -> dict:

        logger.info("Running Summary Engine")

        final = timeline[-1]

        #
        # Determine whether the plan succeeded.
        #
        success = True
        failure_reason = None
        first_failure_age = None

        for year in timeline:

            if year.closing_pension < 0:

                success = False
                failure_reason = "Pension exhausted"
                first_failure_age = year.age
                break

            #
            # Only check this if the field exists.
            #
            if hasattr(year, "income_shortfall"):

                if year.income_shortfall > 0:

                    success = False
                    failure_reason = "Income shortfall"
                    first_failure_age = year.age
                    break

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

            #
            # Success information.
            #
            "success": success,

            "failure_reason": failure_reason,

            "first_failure_age": first_failure_age,

        }

        return summary

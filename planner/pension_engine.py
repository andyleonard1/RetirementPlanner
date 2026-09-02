"""
Pension Engine

Calculates pension growth and withdrawals for each retirement year.

This engine does not create RetirementYear objects.
Instead, it updates the timeline created by TimelineEngine.
"""

import logging

from planner.contracts import AssumptionsProvider, Timeline
from planner.funds.projection_engine_integration import ProjectionReturnDecision

logger = logging.getLogger(__name__)


class PensionEngine:

    def __init__(
        self,
        assumptions: AssumptionsProvider,
        projection_return_decision: ProjectionReturnDecision | None = None,
    ):

        self.assumptions = assumptions
        self.projection_return_decision = projection_return_decision

        self.starting_pension = assumptions.get("starting_pension")

        self.growth_rate = float(
            assumptions.get("pension_growth")
        )

        #
        # Total tax-free cash available at retirement.
        #
        self.remaining_tax_free_cash = (
            self.starting_pension
            * self.assumptions.get(
                "tax_free_cash_percentage",
                0.25,
            )
        )

    def apply(self, timeline: Timeline) -> Timeline:

        logger.info("Running PensionEngine")

        pension = self.starting_pension

        for year in timeline:

            opening = pension

            #
            # Use Market History / Monte Carlo return if present,
            # otherwise fall back to configured growth.
            #
            if (
                self.projection_return_decision is not None
                and self.projection_return_decision.fund_informed
            ):
                growth_rate = self.projection_return_decision.expected_return
            else:
                growth_rate = getattr(
                    year,
                    "pension_growth_rate",
                    0.0,
                )

                if growth_rate == 0:
                    growth_rate = self.growth_rate

            growth = opening * growth_rate

            #
            # Withdrawal calculated by WithdrawalEngine
            #
            withdrawal = year.pension_withdrawal

            #
            # Split withdrawal into tax-free
            # and taxable portions.
            #
            if self.assumptions.get(
                "use_tax_free_cash",
                True,
            ):

                tax_free = min(
                    withdrawal * 0.25,
                    self.remaining_tax_free_cash,
                )

                taxable = withdrawal - tax_free

                self.remaining_tax_free_cash -= tax_free

            else:

                tax_free = 0.0
                taxable = withdrawal

            #
            # Closing pension
            #
            closing = (
                opening
                + growth
                - withdrawal
            )

            #
            # Store results
            #
            year.opening_pension = round(opening, 2)
            year.pension_growth = round(growth, 2)
            year.pension_withdrawal = round(withdrawal, 2)

            year.tax_free_cash_used = round(
                tax_free,
                2,
            )

            year.taxable_pension_withdrawal = round(
                taxable,
                2,
            )

            year.remaining_tax_free_cash = round(
                self.remaining_tax_free_cash,
                2,
            )

            year.closing_pension = round(closing, 2)

            pension = closing

        return timeline
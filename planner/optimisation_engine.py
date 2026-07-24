"""
Optimisation Engine

Calculates tax-efficient pension withdrawal limits.

Version 1

For each year, calculate how much pension can be
withdrawn while staying within the Personal Allowance.

This engine does NOT decide where money comes from.
It simply provides guidance for StrategyEngine.
"""

import logging

logger = logging.getLogger(__name__)


class OptimisationEngine:

    def __init__(self, assumptions):

        self.assumptions = assumptions

    def apply(self, timeline):

        logger.info("Running OptimisationEngine")

        allowance = self.assumptions.get("personal_allowance")

        for year in timeline:

            #
            # Taxable income already received
            #
            taxable_income = (
                year.your_state_pension
                + year.spouse_state_pension
            )

            #
            # Remaining Personal Allowance
            #
            remaining_allowance = max(
                0.0,
                allowance - taxable_income,
            )

            #
            # Store result for StrategyEngine
            #
            year.maximum_tax_efficient_pension = round(
                remaining_allowance,
                2,
            )

            logger.debug(
                f"Age {year.age}: "
                f"Taxable income={taxable_income}, "
                f"Remaining allowance={remaining_allowance}"
            )

        return timeline
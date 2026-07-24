"""
Tax Optimizer Engine

Calculates the maximum tax-efficient pension income
for each retirement year.

Version 1

Uses the remaining Basic Rate tax band.
"""
import logging

logger = logging.getLogger(__name__)

class TaxOptimizerEngine:

    def __init__(self, assumptions):

        self.assumptions = assumptions

    def apply(self, timeline):
        logger.info("Running Tax Optimiser Engine")
        allowance = self.assumptions.get("personal_allowance")
        basic_limit = self.assumptions.get("basic_rate_limit")

        for year in timeline:

            state_pension = (
                year.your_state_pension
                + year.spouse_state_pension
            )

            #
            # Remaining taxable income
            #
            remaining_basic_band = max(
                0,
                basic_limit - state_pension,
            )

            year.maximum_tax_efficient_pension = round(
                remaining_basic_band,
                2,
            )

        return timeline
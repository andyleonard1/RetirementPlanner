"""
Optimisation Engine

Shared optimisation framework for retirement-income calculations.

The live planner uses the Personal Allowance policy implemented by this
engine. Alternative tax-limit policies can reuse the same framework without
duplicating the timeline traversal and result storage.
"""

import logging

logger = logging.getLogger(__name__)


class OptimisationEngine:

    def __init__(self, assumptions, policy="personal_allowance"):
        self.assumptions = assumptions
        self.policy = policy

    def _calculate_limit(self, year):
        """Return the maximum pension income for the selected policy."""

        state_pension = (
            year.your_state_pension
            + year.spouse_state_pension
        )

        if self.policy == "basic_rate_band":
            basic_limit = self.assumptions.get("basic_rate_limit")
            return max(0.0, basic_limit - state_pension)

        allowance = self.assumptions.get("personal_allowance")
        return max(0.0, allowance - state_pension)

    def apply(self, timeline):
        """Calculate and store the tax-efficient pension limit for each year."""

        logger.info(
            "Running OptimisationEngine (policy=%s)",
            self.policy,
        )

        for year in timeline:
            remaining_allowance = self._calculate_limit(year)

            year.maximum_tax_efficient_pension = round(
                remaining_allowance,
                2,
            )

            logger.debug(
                "Age %s: tax-efficient pension=%s",
                year.age,
                remaining_allowance,
            )

        return timeline

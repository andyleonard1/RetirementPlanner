"""
Strategy Engine

Determines where retirement income should come from.

Supported strategies

PENSION_FIRST
    Cash
    Tax-efficient Pension
    Additional Pension
    ISA

ISA_FIRST
    Cash
    Tax-efficient Pension
    ISA
    Additional Pension

SAVINGS_FIRST
    (future)

OPTIMISED
    (future)
"""

import logging

from planner.contracts import AssumptionsProvider, Timeline

logger = logging.getLogger(__name__)


class StrategyEngine:

    def __init__(self, assumptions: AssumptionsProvider):
        self.assumptions = assumptions

    def apply(self, timeline: Timeline) -> Timeline:

        strategy = self.assumptions.get("withdrawal_strategy")

        if strategy is None:
            strategy = "PENSION_FIRST"

        logger.info("Using strategy: %s", strategy)

        if strategy == "ISA_FIRST":
            return self._isa_first(timeline)

        if strategy == "SAVINGS_FIRST":
            return self._savings_first(timeline)

        if strategy == "OPTIMISED":
            return self._optimised(timeline)

        return self._pension_first(timeline)

    # --------------------------------------------------
    # Pension First
    # --------------------------------------------------

    def _pension_first(self, timeline):

        max_pension_income = self._max_pension_income()

        for year in timeline:

            need = year.target_spending

            cash_used = min(
                need,
                year.cash_available,
            )

            remaining = need - cash_used

            #
            # Always use tax-efficient pension first, but never exceed
            # the configured maximum annual pension income.
            #
            pension = min(
                remaining,
                year.maximum_tax_efficient_pension,
                max_pension_income,
            )

            remaining -= pension

            #
            # Additional pension before ISA, subject to the same
            # annual pension-income ceiling.
            #
            additional_pension = min(
                remaining,
                max(0.0, max_pension_income - pension),
            )
            pension += additional_pension
            remaining -= additional_pension

            #
            # Any amount above the pension ceiling is funded from ISA.
            # This makes max_pension_income an actual planning constraint
            # rather than a display-only assumption.
            #
            isa = min(
                remaining,
                year.isa_closing,
            )
            remaining -= isa

            self._store_results(
                year,
                cash_used,
                pension,
                isa,
                income_shortfall=remaining,
            )

        return timeline

    # --------------------------------------------------
    # ISA First
    # --------------------------------------------------

    def _isa_first(self, timeline):

        max_pension_income = self._max_pension_income()

        for year in timeline:

            need = year.target_spending

            cash_used = min(
                need,
                year.cash_available,
            )

            remaining = need - cash_used

            #
            # Use tax-efficient pension first, bounded by the configured
            # maximum annual pension income.
            #
            pension = min(
                remaining,
                year.maximum_tax_efficient_pension,
                max_pension_income,
            )

            remaining -= pension

            #
            # Then ISA.
            #
            isa = min(
                remaining,
                year.isa_closing,
            )

            remaining -= isa

            #
            # ISA exhausted? Use additional pension only up to the
            # configured annual pension-income ceiling.
            #
            additional_pension = min(
                remaining,
                max(0.0, max_pension_income - pension),
            )
            pension += additional_pension
            remaining -= additional_pension

            self._store_results(
                year,
                cash_used,
                pension,
                isa,
                income_shortfall=remaining,
            )

        return timeline

    # --------------------------------------------------
    # Savings First
    # --------------------------------------------------

    def _savings_first(self, timeline):

        logger.info("Savings First not implemented yet.")

        return self._pension_first(timeline)

    # --------------------------------------------------
    # Optimised
    # --------------------------------------------------

    def _optimised(self, timeline):

        logger.info("Optimised strategy not implemented yet.")

        return self._pension_first(timeline)

    # --------------------------------------------------
    # Shared storage
    # --------------------------------------------------

    def _store_results(
        self,
        year,
        cash_used,
        pension,
        isa,
        income_shortfall=0.0,
    ):

        year.interest_used = round(cash_used, 2)

        year.pension_needed = round(pension, 2)

        year.isa_used = round(isa, 2)

        year.savings_remaining = round(
            year.savings_closing,
            2,
        )

        year.isa_remaining = round(
            max(
                0.0,
                year.isa_closing - isa,
            ),
            2,
        )

        year.income_shortfall = round(
            max(0.0, income_shortfall),
            2,
        )

    def _max_pension_income(self):
        value = float(self.assumptions.get("max_pension_income"))
        if value < 0:
            raise ValueError("max_pension_income cannot be negative.")
        return value

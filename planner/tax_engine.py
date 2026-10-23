"""
Tax Engine

Calculates the gross pension withdrawal required to
provide the desired net pension income after income tax.

Supports tax-free pension cash (PCLS).
"""

import logging

from planner.contracts import AssumptionsProvider, Timeline

logger = logging.getLogger(__name__)


class TaxEngine:

    def __init__(self, assumptions: AssumptionsProvider):

        self.assumptions = assumptions

    def apply(self, timeline: Timeline) -> Timeline:

        logger.info("Running Tax Engine")

        allowance = float(self.assumptions.get("personal_allowance"))

        basic_limit = float(self.assumptions.get("basic_rate_limit"))

        basic_rate = self.assumptions.get("basic_rate")

        inflation_link_tax = bool(
            self.assumptions.get("inflation_link_tax", False)
        )

        higher_rate = self.assumptions.get("higher_rate")

        tax_free_percentage = float(
            self.assumptions.get(
                "tax_free_pension_percentage",
                self.assumptions.get("tax_free_cash_percentage", 0.25),
            )
        )
        starting_pension = float(
            self.assumptions.get("starting_pension", 0.0)
        )
        remaining_tax_free_cash = (
            starting_pension * tax_free_percentage
        )

        for year in timeline:

            # Tax thresholds are either held at their configured nominal
            # values or inflation-linked to the same per-year factor used
            # by the live projection.  The first projection year therefore
            # uses the configured values (inflation_factor == 1.0).
            tax_factor = (
                year.inflation_factor if inflation_link_tax else 1.0
            )
            year_allowance = allowance * tax_factor
            year_basic_limit = basic_limit * tax_factor

            #
            # Required net income from pension.
            #
            required_net = year.pension_needed

            #
            # First estimate.
            #
            gross = required_net

            for _ in range(10):

                #
                # Split gross withdrawal into
                # tax-free and taxable elements.
                #
                if self.assumptions.get(
                    "use_tax_free_cash",
                    True,
                ):

                    tax_free = min(
                        gross * tax_free_percentage,
                        remaining_tax_free_cash,
                    )

                else:

                    tax_free = 0.0

                taxable_pension = gross - tax_free

                total_income = (
                    taxable_pension
                    + year.your_state_pension
                )

                taxable_income = max(
                    0.0,
                    total_income - year_allowance,
                )

                if taxable_income <= (
                    year_basic_limit - year_allowance
                ):

                    tax = (
                        taxable_income
                        * basic_rate
                    )

                else:

                    basic_band = (
                        year_basic_limit - year_allowance
                    )

                    higher_band = (
                        taxable_income
                        - basic_band
                    )

                    tax = (
                        basic_band * basic_rate
                        + higher_band * higher_rate
                    )

                new_gross = (
                    required_net
                    + tax
                )

                if abs(
                    new_gross - gross
                ) < 0.01:

                    gross = new_gross

                    break

                gross = new_gross

            #
            # Store results.
            #
            year.gross_pension_income = round(
                gross,
                2,
            )

            year.tax_free_cash_used = round(
                tax_free,
                2,
            )

            year.taxable_pension_withdrawal = round(
                taxable_pension,
                2,
            )

            year.taxable_pension_income = round(
                taxable_income,
                2,
            )

            remaining_tax_free_cash = max(
                0.0,
                remaining_tax_free_cash - tax_free,
            )

            year.income_tax = round(
                tax,
                2,
            )

            year.remaining_tax_free_cash = round(
                remaining_tax_free_cash,
                2,
            )

            year.net_pension_income = round(
                required_net,
                2,
            )

            #
            # PensionEngine deducts the gross amount.
            #
            year.pension_withdrawal = round(
                gross,
                2,
            )

        return timeline
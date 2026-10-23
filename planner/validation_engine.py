"""
Validation Engine

Validates the assumptions before any retirement
calculations are performed.
"""

import logging
import math
from numbers import Real

from planner.contracts import AssumptionsProvider
from planner.assumption_resolver import AssumptionResolver

logger = logging.getLogger(__name__)


class ValidationEngine:

    def __init__(self, assumptions: AssumptionsProvider):

        self.assumptions = assumptions

    def validate(self) -> None:

        logger.info("Validating assumptions")

        self._check_ages()
        self._check_money()
        self._check_tax()
        self._check_investments()
        self._check_spending()

        logger.info("Configuration validated successfully")

    # -----------------------------------------------------
    # Age validation
    # -----------------------------------------------------

    def _check_ages(self):

        current = self._number("current_age")
        retirement = self._number("retirement_age")
        end = self._number("projection_end_age")

        if current < 18:
            raise ValueError(
                "Current age must be at least 18."
            )

        if retirement < current:
            raise ValueError(
                "Retirement age cannot be before current age."
            )

        if end <= retirement:
            raise ValueError(
                "Projection end age must be after retirement age."
            )

    # -----------------------------------------------------
    # Financial validation
    # -----------------------------------------------------

    def _check_money(self):

        self._positive(
            "starting_pension"
        )

        self._positive(
            "starting_savings"
        )

        self._positive(
            "starting_isa"
        )

        self._non_negative("annual_isa_allowance")
        self._non_negative("property_sale")

        self._non_negative(
            "max_pension_income"
        )

    # -----------------------------------------------------
    # Tax validation
    # -----------------------------------------------------

    def _check_tax(self):

        allowance = self._number("personal_allowance")

        if allowance < 0:
            raise ValueError(
                "Personal allowance cannot be negative."
            )

        basic = self._number("basic_rate")
        higher = self._number("higher_rate")
        additional = self._number("additional_rate")
        tax_free_percentage = self._number("tax_free_pension_percentage")

        if not 0 <= tax_free_percentage <= 1:
            raise ValueError(
                "tax_free_pension_percentage must be between 0 and 1."
            )

        property_sale_age = self._number("property_sale_age")

        if property_sale_age < self._number("retirement_age") or property_sale_age > self._number("projection_end_age"):
            raise ValueError(
                "property_sale_age must be within the projection period."
            )

        for rate, name in [

            (basic, "basic_rate"),

            (higher, "higher_rate"),

            (additional, "additional_rate"),

        ]:

            if not 0 <= rate <= 1:

                raise ValueError(
                    f"{name} must be between 0 and 1."
                )

    # -----------------------------------------------------
    # Investment assumptions
    # -----------------------------------------------------

    def _check_investments(self):

        expected = AssumptionResolver(self.assumptions).expected_investment_return()
        expected_return = AssumptionResolver(self.assumptions).monte_carlo_expected_return()
        volatility = AssumptionResolver(self.assumptions).investment_volatility()
        platform_charge = self._number("platform_charge")
        fund_charge = self._number("fund_charge")

        if expected < -0.20 or expected > 0.25:

            raise ValueError(
                "Expected investment return looks unrealistic."
            )

        if expected_return < -0.20 or expected_return > 0.25:

            raise ValueError(
                "Expected return looks unrealistic."
            )

        if volatility < 0:

            raise ValueError(
                "Investment volatility cannot be negative."
            )

        for charge, name in (
            (platform_charge, "platform_charge"),
            (fund_charge, "fund_charge"),
        ):
            if charge < 0:
                raise ValueError(f"{name} cannot be negative.")
            if charge >= 1:
                raise ValueError(f"{name} must be less than 1.")

        if platform_charge + fund_charge >= 1:
            raise ValueError(
                "platform_charge plus fund_charge must be less than 1."
            )

    # -----------------------------------------------------
    # Spending phases
    # -----------------------------------------------------

    def _check_spending(self):

        phase1 = self._number("spending_phase_1")
        phase2 = self._number("spending_phase_2")
        phase3 = self._number("spending_phase_3")

        for value, name in [

            (phase1, "spending_phase_1"),

            (phase2, "spending_phase_2"),

            (phase3, "spending_phase_3"),

        ]:

            if value <= 0:

                raise ValueError(
                    f"{name} must be greater than zero."
                )

    # -----------------------------------------------------
    # Helpers
    # -----------------------------------------------------

    def _positive(self, key):

        value = self._number(key)

        if value < 0:

            raise ValueError(
                f"{key} cannot be negative."
            )

    def _non_negative(self, key):

        value = self._number(key)

        if value < 0:

            raise ValueError(
                f"{key} cannot be negative."
            )
    # -----------------------------------------------------
    # Required numeric assumption helper
    # -----------------------------------------------------

    def _number(self, key):

        value = self.assumptions.get(key)

        if isinstance(value, bool) or not isinstance(value, Real):
            raise ValueError(
                f"{key} must be a finite number."
            )

        if not math.isfinite(value):
            raise ValueError(
                f"{key} must be a finite number."
            )

        return value

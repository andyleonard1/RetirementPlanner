"""
Validation Engine

Validates the assumptions before any retirement
calculations are performed.
"""

import logging

logger = logging.getLogger(__name__)


class ValidationEngine:

    def __init__(self, assumptions):

        self.assumptions = assumptions

    def validate(self):

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

        current = self.assumptions.get("current_age")
        retirement = self.assumptions.get("retirement_age")
        end = self.assumptions.get("projection_end_age")

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

    # -----------------------------------------------------
    # Tax validation
    # -----------------------------------------------------

    def _check_tax(self):

        allowance = self.assumptions.get(
            "personal_allowance"
        )

        if allowance < 0:
            raise ValueError(
                "Personal allowance cannot be negative."
            )

        basic = self.assumptions.get(
            "basic_rate"
        )

        higher = self.assumptions.get(
            "higher_rate"
        )

        additional = self.assumptions.get(
            "additional_rate"
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

        expected = self.assumptions.get(
            "expected_investment_return"
        )

        volatility = self.assumptions.get(
            "investment_volatility"
        )

        if expected < -0.20 or expected > 0.25:

            raise ValueError(
                "Expected investment return looks unrealistic."
            )

        if volatility < 0:

            raise ValueError(
                "Investment volatility cannot be negative."
            )

    # -----------------------------------------------------
    # Spending phases
    # -----------------------------------------------------

    def _check_spending(self):

        phase1 = self.assumptions.get(
            "spending_phase_1"
        )

        phase2 = self.assumptions.get(
            "spending_phase_2"
        )

        phase3 = self.assumptions.get(
            "spending_phase_3"
        )

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

        value = self.assumptions.get(key)

        if value < 0:

            raise ValueError(
                f"{key} cannot be negative."
            )
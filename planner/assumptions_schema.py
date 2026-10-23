"""
Assumptions schema.

Defines the configuration contract for ``data/assumptions.json``.  The
schema deliberately handles structure and types only; business/range rules
remain in ValidationEngine.
"""

from __future__ import annotations

import logging
import math
from numbers import Real
from typing import Any

logger = logging.getLogger(__name__)


class AssumptionsSchema:
    """Validate the structural contract of planner assumptions."""

    REQUIRED_NUMERIC = {
        "current_age",
        "retirement_age",
        "projection_end_age",
        "spouse_current_age",
        "max_pension_income",
        "starting_pension",
        "expected_investment_return",
        "platform_charge",
        "fund_charge",
        "target_net_income",
        "starting_savings",
        "savings_interest_rate",
        "inflation",
        "personal_allowance",
        "basic_rate_limit",
        "basic_rate",
        "higher_rate",
        "additional_rate",
        "pension_growth",
        "expected_return",
        "investment_volatility",
        "inflation_volatility",
        "savings_interest",
        "tax_free_pension_percentage",
        "starting_isa",
        "isa_growth_rate",
        "annual_isa_allowance",
        "property_sale",
        "property_sale_age",
        "state_pension_full",
        "current_calendar_year",
        "state_pension_growth",
        "state_pension_earnings_growth",
        "spending_phase_1",
        "spending_phase_2",
        "spending_phase_3",
        "phase_1_end_age",
        "phase_2_end_age",
        "inflation_rate",
    }

    REQUIRED_STRINGS = {"withdrawal_strategy"}

    REQUIRED_BOOLEANS = {
        "inflation_link_spending",
        "inflation_link_tax",
        "inflation_link_isa",
        "state_pension_triple_lock_enabled",
    }

    REQUIRED_LISTS = {"goals"}

    OPTIONAL_BOOLS = {
        "isa_allowance_schedule_enabled",
        "state_pension_earnings_growth_schedule_enabled",
        "annual_spending_schedule_enabled",
        "investment_return_schedule_enabled",
        "isa_return_schedule_enabled",
    }
    OPTIONAL_OBJECTS = {
        "isa_allowance_schedule",
        "state_pension_earnings_growth_schedule",
        "annual_spending_schedule",
        "investment_return_schedule",
        "isa_return_schedule",
    }

    REQUIRED_KEYS = (
        REQUIRED_NUMERIC
        | REQUIRED_STRINGS
        | REQUIRED_BOOLEANS
        | REQUIRED_LISTS
    )

    @classmethod
    def validate(cls, data: dict[str, Any]) -> None:
        if not isinstance(data, dict):
            raise ValueError("Assumptions root must be a JSON object.")

        missing = sorted(cls.REQUIRED_KEYS - data.keys())
        if missing:
            raise ValueError(
                "Missing required assumptions: " + ", ".join(missing)
            )

        for key in sorted(cls.REQUIRED_NUMERIC):
            cls._require_finite_number(data[key], key)

        for key in sorted(cls.REQUIRED_STRINGS):
            if not isinstance(data[key], str) or not data[key].strip():
                raise ValueError(f"{key} must be a non-empty string.")

        for key in sorted(cls.REQUIRED_BOOLEANS):
            if not isinstance(data[key], bool):
                raise ValueError(f"{key} must be a boolean.")

        for key in sorted(cls.OPTIONAL_BOOLS):
            if key in data and not isinstance(data[key], bool):
                raise ValueError(f"{key} must be a boolean.")

        for key in sorted(cls.OPTIONAL_OBJECTS):
            if key in data:
                if key == "isa_allowance_schedule":
                    cls._validate_isa_allowance_schedule(data[key])
                elif key == "annual_spending_schedule":
                    cls._validate_annual_spending_schedule(data[key])
                elif key in {"investment_return_schedule", "isa_return_schedule"}:
                    cls._validate_annual_rate_schedule(data[key], key)
                else:
                    cls._validate_annual_numeric_schedule(
                        data[key], key
                    )

        cls._validate_goals(data["goals"])

        known_keys = cls.REQUIRED_KEYS | cls.OPTIONAL_BOOLS | cls.OPTIONAL_OBJECTS
        unknown = sorted(set(data) - known_keys)
        if unknown:
            logger.warning(
                "Unknown assumption keys will be retained: %s",
                ", ".join(unknown),
            )

    @staticmethod
    def _require_finite_number(value: Any, key: str) -> None:
        if isinstance(value, bool) or not isinstance(value, Real):
            raise ValueError(f"{key} must be a finite number.")
        if not math.isfinite(value):
            raise ValueError(f"{key} must be a finite number.")


    @staticmethod
    def _validate_annual_numeric_schedule(value: Any, key: str) -> None:
        if not isinstance(value, dict):
            raise ValueError(f"{key} must be an object.")

        for calendar_year, rate in value.items():
            if (
                not isinstance(calendar_year, str)
                or len(calendar_year) != 4
                or not calendar_year.isdigit()
            ):
                raise ValueError(
                    f"{key} keys must use YYYY calendar-year strings."
                )
            if (
                isinstance(rate, bool)
                or not isinstance(rate, Real)
                or not math.isfinite(rate)
                or rate < 0
            ):
                raise ValueError(
                    f"{key} values must be non-negative finite numbers."
                )

    @staticmethod
    def _validate_annual_rate_schedule(value: Any, key: str) -> None:
        if not isinstance(value, dict):
            raise ValueError(f"{key} must be an object.")

        for calendar_year, rate in value.items():
            if (
                not isinstance(calendar_year, str)
                or len(calendar_year) != 4
                or not calendar_year.isdigit()
            ):
                raise ValueError(
                    f"{key} keys must use YYYY calendar-year strings."
                )
            if (
                isinstance(rate, bool)
                or not isinstance(rate, Real)
                or not math.isfinite(rate)
                or rate < -1
            ):
                raise ValueError(
                    f"{key} values must be finite numbers greater than or equal to -1."
                )

    @staticmethod
    def _validate_annual_spending_schedule(value: Any) -> None:
        if not isinstance(value, dict):
            raise ValueError("annual_spending_schedule must be an object.")

        for calendar_year, spending in value.items():
            if (
                not isinstance(calendar_year, str)
                or len(calendar_year) != 4
                or not calendar_year.isdigit()
            ):
                raise ValueError(
                    "annual_spending_schedule keys must use YYYY calendar-year strings."
                )
            if (
                isinstance(spending, bool)
                or not isinstance(spending, Real)
                or not math.isfinite(spending)
                or spending <= 0
            ):
                raise ValueError(
                    "annual_spending_schedule values must be positive finite numbers."
                )

    @staticmethod
    def _validate_isa_allowance_schedule(value: Any) -> None:
        if not isinstance(value, dict):
            raise ValueError("isa_allowance_schedule must be an object.")

        for tax_year, allowance in value.items():
            if not isinstance(tax_year, str) or not tax_year.strip():
                raise ValueError("isa_allowance_schedule keys must be tax-year strings.")
            parts = tax_year.split("/")
            if len(parts) != 2 or len(parts[0]) != 4 or len(parts[1]) != 2 or not parts[0].isdigit() or not parts[1].isdigit():
                raise ValueError("isa_allowance_schedule keys must use YYYY/YY format.")
            if int(parts[1]) != (int(parts[0]) + 1) % 100:
                raise ValueError(f"Invalid ISA allowance tax year: {tax_year}.")
            if isinstance(allowance, bool) or not isinstance(allowance, Real) or not math.isfinite(allowance):
                raise ValueError(f"ISA allowance for {tax_year} must be a finite number.")
            if allowance < 0:
                raise ValueError(f"ISA allowance for {tax_year} cannot be negative.")

    @staticmethod
    def _validate_goals(goals: Any) -> None:
        if not isinstance(goals, list):
            raise ValueError("goals must be a list.")

        for index, goal in enumerate(goals):
            if not isinstance(goal, dict):
                raise ValueError(f"goals[{index}] must be an object.")

            if not isinstance(goal.get("name"), str) or not goal["name"].strip():
                raise ValueError(f"goals[{index}].name must be a non-empty string.")

            if not isinstance(goal.get("type"), str) or not goal["type"].strip():
                raise ValueError(f"goals[{index}].type must be a non-empty string.")

            if "target" in goal:
                AssumptionsSchema._require_finite_number(
                    goal["target"],
                    f"goals[{index}].target",
                )

            if "enabled" in goal and not isinstance(goal["enabled"], bool):
                raise ValueError(f"goals[{index}].enabled must be a boolean.")

            if "operator" in goal:
                operators = {">=", ">", "<=", "<", "==", "!="}
                if goal["operator"] not in operators:
                    raise ValueError(
                        f"goals[{index}].operator must be one of: "
                        + ", ".join(sorted(operators))
                        + "."
                    )

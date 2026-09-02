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
    }

    REQUIRED_LISTS = {"goals"}

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

        cls._validate_goals(data["goals"])

        unknown = sorted(set(data) - cls.REQUIRED_KEYS)
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

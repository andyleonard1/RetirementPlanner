"""Canonical assumption access with explicit legacy compatibility boundaries."""
from __future__ import annotations

import logging
import math
from numbers import Real
from typing import Any

logger = logging.getLogger(__name__)


class AssumptionResolver:
    """Resolve canonical planner assumptions while preserving legacy aliases.

    New calculation code should use these accessors rather than reading one of
    the historical duplicate keys directly.  When both values are present,
    the canonical key wins and a warning is emitted if the legacy value differs.
    """

    _ALIASES = {
        "inflation_rate": "inflation",
        "savings_interest_rate": "savings_interest",
        "expected_investment_return": "pension_growth",
    }

    def __init__(self, assumptions: Any):
        self.assumptions = assumptions

    @staticmethod
    def _require_finite_number(value: Any, key: str) -> float:
        if isinstance(value, bool) or not isinstance(value, Real) or not math.isfinite(value):
            raise ValueError(f"{key} must be a finite number.")
        return float(value)

    def _numeric(self, canonical_key: str, default: Any = None) -> float:
        value = self.get(canonical_key, default)
        if value is None:
            raise ValueError(f"missing numeric assumption: {canonical_key}")
        return self._require_finite_number(value, canonical_key)

    def get(self, canonical_key: str, default: Any = None) -> Any:
        value = self.assumptions.get(canonical_key)
        legacy_key = self._ALIASES.get(canonical_key)
        if value is None and legacy_key:
            value = self.assumptions.get(legacy_key)
            if value is not None:
                logger.debug(
                    "Legacy assumption '%s' used as fallback for '%s'.",
                    legacy_key,
                    canonical_key,
                )
        elif legacy_key and self.assumptions.get(legacy_key) is not None:
            legacy_value = self.assumptions.get(legacy_key)
            if value != legacy_value:
                logger.debug(
                    "Canonical assumption '%s' overrides legacy '%s'.",
                    canonical_key,
                    legacy_key,
                )
        return default if value is None else value

    def inflation_rate(self) -> float:
        return self._numeric("inflation_rate")

    def savings_interest_rate(self) -> float:
        return self._numeric("savings_interest_rate")

    def expected_investment_return(self) -> float:
        return self._numeric("expected_investment_return")

    def investment_volatility(self, default: float = 0.0) -> float:
        return self._numeric("investment_volatility", default)

    def inflation_volatility(self, default: float = 0.0) -> float:
        return self._numeric("inflation_volatility", default)

    def isa_growth_rate(self, default: float = 0.0) -> float:
        return self._numeric("isa_growth_rate", default)

    def state_pension_full(self, default: float | None = None) -> Any:
        return self.get("state_pension_full", default)

    def state_pension_growth(self, default: float | None = None) -> Any:
        return self.get("state_pension_growth", default)

    def state_pension_earnings_growth(self, default: float | None = None) -> Any:
        return self.get("state_pension_earnings_growth", default)

    def state_pension_triple_lock_enabled(self, default: bool = False) -> bool:
        return bool(self.get("state_pension_triple_lock_enabled", default))

    def state_pension_earnings_growth_schedule_enabled(self, default: bool = False) -> bool:
        return bool(self.get("state_pension_earnings_growth_schedule_enabled", default))

    def state_pension_earnings_growth_schedule(self) -> dict:
        return self.get("state_pension_earnings_growth_schedule", {}) or {}

    def monte_carlo_expected_return(self) -> float:
        # Stochastic return has its own explicit precedence because
        # ``expected_return`` is the Monte Carlo mean, while
        # ``expected_investment_return`` is the deterministic projection
        # return.  ``pension_growth`` remains the final legacy fallback.
        for key in ("expected_return", "expected_investment_return", "pension_growth"):
            value = self.assumptions.get(key)
            if value is not None:
                return self._require_finite_number(value, key)
        raise ValueError("missing numeric assumption: expected_return")

    def platform_charge(self, default: float = 0.0) -> float:
        return self._numeric("platform_charge", default)

    def fund_charge(self, default: float = 0.0) -> float:
        return self._numeric("fund_charge", default)

    def investment_return_schedule_enabled(self, default: bool = False) -> bool:
        return bool(self.get("investment_return_schedule_enabled", default))

    def investment_return_schedule(self) -> dict:
        return self.get("investment_return_schedule", {}) or {}

    def isa_return_schedule_enabled(self, default: bool = False) -> bool:
        return bool(self.get("isa_return_schedule_enabled", default))

    def isa_return_schedule(self) -> dict:
        return self.get("isa_return_schedule", {}) or {}

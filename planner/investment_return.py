"""Resolve configured investment returns and investment charges."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from planner.assumption_resolver import AssumptionResolver


@dataclass(frozen=True)
class InvestmentReturnConfig:
    """Configured gross return assumptions and their net projection return."""

    gross_projection_return: float
    monte_carlo_expected_return: float
    platform_charge: float
    fund_charge: float

    @property
    def total_charge(self) -> float:
        return self.platform_charge + self.fund_charge

    @property
    def net_projection_return(self) -> float:
        return self.gross_projection_return - self.total_charge

    @property
    def net_monte_carlo_expected_return(self) -> float:
        return self.monte_carlo_expected_return - self.total_charge


class InvestmentReturnResolver:
    """Provide one calculation boundary for return/charge assumptions.

    ``expected_investment_return`` is the canonical gross deterministic
    projection return. ``expected_return`` remains the Monte Carlo mean return.
    ``pension_growth`` is retained only as a legacy fallback for older callers
    that do not provide the newer fields.
    """

    @classmethod
    def resolve(cls, assumptions: Any) -> InvestmentReturnConfig:
        gross_projection_return = AssumptionResolver(assumptions).expected_investment_return()
        monte_carlo_expected_return = AssumptionResolver(assumptions).monte_carlo_expected_return()
        resolver = AssumptionResolver(assumptions)
        platform_charge = resolver.platform_charge()
        fund_charge = resolver.fund_charge()
        return InvestmentReturnConfig(
            gross_projection_return=gross_projection_return,
            monte_carlo_expected_return=monte_carlo_expected_return,
            platform_charge=platform_charge,
            fund_charge=fund_charge,
        )

    @classmethod
    def scheduled_gross_projection_return(cls, assumptions: Any, calendar_year: int) -> float:
        resolver = AssumptionResolver(assumptions)
        base = resolver.expected_investment_return()
        if not resolver.investment_return_schedule_enabled():
            return base
        schedule = resolver.investment_return_schedule()
        value = schedule.get(str(calendar_year))
        return base if value is None else float(value)

    @classmethod
    def scheduled_isa_return(cls, assumptions: Any, calendar_year: int) -> float:
        resolver = AssumptionResolver(assumptions)
        base = resolver.isa_growth_rate()
        if not resolver.isa_return_schedule_enabled():
            return base
        schedule = resolver.isa_return_schedule()
        value = schedule.get(str(calendar_year))
        return base if value is None else float(value)

    @staticmethod
    def _get_number(
        assumptions: Any,
        key: str,
        *,
        fallback_key: str | None = None,
        default: float | None = None,
    ) -> float:
        value = assumptions.get(key)
        if value is None and fallback_key is not None:
            value = assumptions.get(fallback_key)
        if value is None:
            if default is None:
                raise ValueError(f"missing investment assumption: {key}")
            return float(default)
        return float(value)

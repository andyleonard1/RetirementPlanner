"""Controlled integration boundary for fund-informed projection returns."""
from __future__ import annotations

from dataclasses import dataclass

from .fund_informed_projection_inputs import FundInformedProjectionInput


@dataclass(frozen=True)
class ProjectionReturnDecision:
    expected_return: float
    source: str
    fund_informed: bool


class ProjectionEngineIntegration:
    """Select a projection return without mutating the pension engine."""

    def select_return(
        self,
        legacy_return: float,
        fund_input: FundInformedProjectionInput | None = None,
    ) -> ProjectionReturnDecision:
        if fund_input is None or not fund_input.enabled:
            return ProjectionReturnDecision(
                expected_return=float(legacy_return),
                source="legacy projection return",
                fund_informed=False,
            )

        return ProjectionReturnDecision(
            expected_return=float(fund_input.expected_return),
            source=f"fund-informed scenario: {fund_input.scenario_name}",
            fund_informed=True,
        )

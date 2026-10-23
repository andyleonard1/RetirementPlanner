"""User-supplied fund allocation validation for RC4 Sprint 82."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True)
class FundAllocation:
    fund_identifier: str
    allocation: float


@dataclass(frozen=True)
class PortfolioAllocationResult:
    allocations: tuple[FundAllocation, ...]
    total_allocation: float
    valid: bool
    reason: str


class PortfolioAllocationValidator:
    """Validate user-entered portfolio allocations without normalising them."""

    def __init__(self, *, tolerance: float = 1e-9):
        self._tolerance = tolerance

    def validate(
        self,
        allocations: Mapping[str, float],
    ) -> PortfolioAllocationResult:
        items = tuple(
            FundAllocation(str(fund), float(weight))
            for fund, weight in allocations.items()
        )

        if not items:
            return PortfolioAllocationResult(
                (), 0.0, False, "At least one fund allocation is required."
            )

        if any(item.allocation < 0 for item in items):
            return PortfolioAllocationResult(
                items,
                sum(item.allocation for item in items),
                False,
                "Fund allocations cannot be negative.",
            )

        total = sum(item.allocation for item in items)

        if abs(total - 1.0) > self._tolerance:
            return PortfolioAllocationResult(
                items,
                total,
                False,
                "Fund allocations must total 100%.",
            )

        return PortfolioAllocationResult(
            items,
            total,
            True,
            "Fund allocations total 100%.",
        )

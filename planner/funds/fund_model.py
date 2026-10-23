"""Actual pension fund data model for RC4 Sprint 67."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class Fund:
    provider: str
    name: str
    identifier: str | None = None
    annual_charge: float = 0.0

    def validate(self) -> None:
        if not self.provider.strip():
            raise ValueError("provider is required")
        if not self.name.strip():
            raise ValueError("name is required")
        if self.annual_charge < 0:
            raise ValueError("annual_charge cannot be negative")


@dataclass(frozen=True)
class FundAllocation:
    fund: Fund
    percentage: float

    def validate(self) -> None:
        self.fund.validate()
        if self.percentage < 0 or self.percentage > 100:
            raise ValueError("percentage must be between 0 and 100")


@dataclass(frozen=True)
class FundPortfolio:
    allocations: tuple[FundAllocation, ...]

    def validate(self) -> None:
        if not self.allocations:
            raise ValueError("at least one fund allocation is required")

        for allocation in self.allocations:
            allocation.validate()

        total = sum(a.percentage for a in self.allocations)
        if abs(total - 100.0) > 1e-9:
            raise ValueError("fund allocations must total 100 percent")

    @classmethod
    def from_allocations(
        cls,
        allocations: Iterable[FundAllocation],
    ) -> "FundPortfolio":
        portfolio = cls(tuple(allocations))
        portfolio.validate()
        return portfolio

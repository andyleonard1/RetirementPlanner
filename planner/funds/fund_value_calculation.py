"""Calculate current fund values from starting pension and allocations."""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from typing import Mapping

from .portfolio_allocation import PortfolioAllocationValidator


@dataclass(frozen=True)
class FundValue:
    fund_identifier: str
    allocation: float
    value: Decimal


@dataclass(frozen=True)
class FundValueCalculationResult:
    starting_pension: Decimal
    fund_values: tuple[FundValue, ...]
    total_value: Decimal


class FundValueCalculator:
    """Translate validated user allocations into monetary fund values."""

    def __init__(self, *, tolerance: float = 1e-9):
        self._validator = PortfolioAllocationValidator(tolerance=tolerance)

    def calculate(
        self,
        starting_pension: float | Decimal,
        allocations: Mapping[str, float],
    ) -> FundValueCalculationResult:
        pension = Decimal(str(starting_pension))

        if pension < 0:
            raise ValueError("Starting pension cannot be negative.")

        validation = self._validator.validate(allocations)
        if not validation.valid:
            raise ValueError(validation.reason)

        values = []
        for allocation in validation.allocations:
            value = (pension * Decimal(str(allocation.allocation))).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            values.append(
                FundValue(
                    allocation.fund_identifier,
                    allocation.allocation,
                    value,
                )
            )

        total = sum((item.value for item in values), Decimal("0.00"))

        # Allocation validation guarantees the unrounded total equals the
        # starting pension. Penny rounding can otherwise introduce a tiny
        # discrepancy, so reconcile the final fund to preserve the source total.
        difference = pension.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) - total
        if values and difference:
            last = values[-1]
            values[-1] = FundValue(
                last.fund_identifier,
                last.allocation,
                last.value + difference,
            )
            total += difference

        return FundValueCalculationResult(
            pension.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
            tuple(values),
            total,
        )

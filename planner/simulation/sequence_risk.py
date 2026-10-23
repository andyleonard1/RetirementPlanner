"""Sequence-of-returns risk analysis for RC4.

This module is intentionally independent of the deterministic retirement engines.
It compares identical return sets in different orders while allowing withdrawals.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class SequenceRiskResult:
    first_terminal_value: float
    second_terminal_value: float
    absolute_difference: float
    percentage_difference: float


class SequenceRiskAnalyzer:
    """Compare identical return sets applied in different orders."""

    @staticmethod
    def terminal_value(
        starting_value: float,
        annual_returns: Iterable[float],
        withdrawals: Iterable[float] | None = None,
    ) -> float:
        if starting_value < 0:
            raise ValueError("starting_value cannot be negative")

        returns = list(annual_returns)
        withdrawal_values = list(withdrawals) if withdrawals is not None else [0.0] * len(returns)
        if len(withdrawal_values) != len(returns):
            raise ValueError("withdrawals must match the number of returns")

        value = starting_value
        for annual_return, withdrawal in zip(returns, withdrawal_values):
            if withdrawal < 0:
                raise ValueError("withdrawals cannot be negative")
            value = max(0.0, value * (1.0 + annual_return) - withdrawal)
        return value

    def compare(
        self,
        starting_value: float,
        first_returns: Iterable[float],
        second_returns: Iterable[float],
        withdrawals: Iterable[float] | None = None,
    ) -> SequenceRiskResult:
        first = list(first_returns)
        second = list(second_returns)
        if sorted(first) != sorted(second):
            raise ValueError(
                "sequence comparison requires the same annual returns in different order"
            )

        first_value = self.terminal_value(starting_value, first, withdrawals)
        second_value = self.terminal_value(starting_value, second, withdrawals)
        difference = abs(first_value - second_value)
        baseline = max(first_value, second_value)
        percentage = 0.0 if baseline == 0 else difference / baseline

        return SequenceRiskResult(
            first_terminal_value=first_value,
            second_terminal_value=second_value,
            absolute_difference=difference,
            percentage_difference=percentage,
        )

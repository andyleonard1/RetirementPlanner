"""Isolated Monte Carlo infrastructure for RC4."""
from __future__ import annotations

from dataclasses import dataclass
import random
from statistics import quantiles
from typing import Iterable


@dataclass(frozen=True)
class SimulationConfig:
    paths: int = 1000
    years: int = 30
    mean_return: float = 0.04
    volatility: float = 0.10
    seed: int | None = 42

    def validate(self) -> None:
        if self.paths <= 0:
            raise ValueError("paths must be greater than zero")
        if self.years <= 0:
            raise ValueError("years must be greater than zero")
        if self.volatility < 0:
            raise ValueError("volatility cannot be negative")


@dataclass(frozen=True)
class SimulationSummary:
    paths: int
    years: int
    percentile_10: float
    percentile_50: float
    percentile_90: float
    success_probability: float


class MonteCarloEngine:
    """Generate reproducible annual return paths and summarise terminal values."""

    def __init__(self, config: SimulationConfig):
        config.validate()
        self.config = config

    def generate_return_paths(self) -> list[list[float]]:
        rng = random.Random(self.config.seed)
        return [[rng.gauss(self.config.mean_return, self.config.volatility)
                 for _ in range(self.config.years)]
                for _ in range(self.config.paths)]

    @staticmethod
    def terminal_values(starting_value: float,
                        paths: Iterable[Iterable[float]]) -> list[float]:
        if starting_value < 0:
            raise ValueError("starting_value cannot be negative")
        values = []
        for path in paths:
            value = starting_value
            for annual_return in path:
                value *= 1 + annual_return
            values.append(value)
        return values

    def summarise(self, starting_value: float,
                  success_threshold: float = 0.0) -> SimulationSummary:
        values = sorted(self.terminal_values(starting_value,
                                              self.generate_return_paths()))
        if len(values) == 1:
            p10 = p50 = p90 = values[0]
        else:
            qs = quantiles(values, n=10, method="inclusive")
            p10, p50, p90 = qs[0], qs[4], qs[8]
        success = sum(v >= success_threshold for v in values) / len(values)
        return SimulationSummary(self.config.paths, self.config.years,
                                 p10, p50, p90, success)

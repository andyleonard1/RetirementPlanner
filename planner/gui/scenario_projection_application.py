"""Application/controller boundary for the scenario comparison desktop UI."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping, Sequence

from planner.assumptions import Assumptions
from planner.funds.portfolio_historical_statistics import PortfolioHistoricalStatisticsCalculator
from planner.projection.scenario_projection_comparison import ScenarioProjectionComparisonRunner
from planner.projection.scenario_projection_view_model import ScenarioProjectionViewModel


@dataclass(frozen=True)
class ScenarioProjectionInputs:
    """User-editable inputs required to build a scenario comparison."""

    starting_pension: float
    retirement_age: int
    projection_end_age: int
    scenarios: tuple[str, ...] = ("conservative", "central", "optimistic")

    def __post_init__(self) -> None:
        if self.starting_pension < 0:
            raise ValueError("starting_pension cannot be negative")
        if self.retirement_age < 1:
            raise ValueError("retirement_age must be positive")
        if self.projection_end_age < self.retirement_age:
            raise ValueError("projection_end_age must be at least retirement_age")
        names = tuple(dict.fromkeys(str(name).strip().lower() for name in self.scenarios))
        if not names:
            raise ValueError("at least one scenario is required")
        object.__setattr__(self, "scenarios", names)


class ScenarioProjectionApplication:
    """Bind user inputs to the existing calculation and GUI boundaries.

    This class owns orchestration only. Financial calculations remain in the
    existing planner engines and the comparison runner.
    """

    def __init__(
        self,
        assumptions: Assumptions,
        *,
        statistics_calculator: PortfolioHistoricalStatisticsCalculator | None = None,
        comparison_runner: ScenarioProjectionComparisonRunner | None = None,
    ) -> None:
        if not isinstance(assumptions, Assumptions):
            raise TypeError("assumptions must be Assumptions")
        self.assumptions = assumptions
        self.statistics_calculator = statistics_calculator or PortfolioHistoricalStatisticsCalculator()
        self.comparison_runner = comparison_runner or ScenarioProjectionComparisonRunner()

    def inputs(self) -> ScenarioProjectionInputs:
        """Return current planner inputs without changing the assumptions."""
        return ScenarioProjectionInputs(
            starting_pension=float(self.assumptions.get("starting_pension")),
            retirement_age=int(self.assumptions.get("retirement_age")),
            projection_end_age=int(self.assumptions.get("projection_end_age")),
        )

    def apply_inputs(self, inputs: ScenarioProjectionInputs) -> None:
        """Apply validated GUI inputs in memory; persistence remains explicit."""
        if not isinstance(inputs, ScenarioProjectionInputs):
            raise TypeError("inputs must be ScenarioProjectionInputs")
        self.assumptions.set("starting_pension", inputs.starting_pension)
        self.assumptions.set("retirement_age", inputs.retirement_age)
        self.assumptions.set("projection_end_age", inputs.projection_end_age)
        self.assumptions.validate()

    def build_view_model(
        self,
        *,
        allocations: Mapping[str, float],
        fund_returns: Mapping[str, Sequence[float]],
        scenarios: Iterable[str] | None = None,
    ) -> ScenarioProjectionViewModel:
        """Calculate using the existing runner and expose only the GUI view model."""
        selected = tuple(scenarios) if scenarios is not None else self.inputs().scenarios
        statistics = self.statistics_calculator.calculate(allocations, fund_returns)
        comparison = self.comparison_runner.run(
            assumptions=self.assumptions,
            statistics=statistics,
            scenarios=selected,
        )
        return ScenarioProjectionViewModel.from_comparison(comparison)

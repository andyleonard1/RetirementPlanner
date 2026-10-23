"""Application/controller boundary for the scenario comparison desktop UI."""
from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Iterable, Mapping, Sequence

from planner.assumptions import Assumptions
from planner.funds.portfolio_historical_statistics import PortfolioHistoricalStatisticsCalculator
from planner.projection.scenario_projection_comparison import ScenarioProjectionComparisonRunner
from planner.projection.scenario_projection_export import export_snapshot_bundle
from planner.projection.scenario_projection_report import ScenarioProjectionReport
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


class _FrozenDict(dict):
    """Dictionary-shaped read-only container used at the application boundary."""

    def _blocked(self, *args, **kwargs):
        raise TypeError("workflow result mappings are immutable")

    __setitem__ = __delitem__ = clear = pop = popitem = setdefault = update = _blocked
    __ior__ = _blocked


class _FrozenList(list):
    """List-shaped read-only container used at the application boundary."""

    def _blocked(self, *args, **kwargs):
        raise TypeError("workflow result sequences are immutable")

    __setitem__ = __delitem__ = __iadd__ = __imul__ = _blocked
    append = clear = extend = insert = pop = remove = reverse = sort = _blocked


@dataclass(frozen=True)
class ScenarioProjectionWorkflowResult:
    """Immutable projection/report boundary result shared by CLI and GUI consumers."""

    inputs: ScenarioProjectionInputs
    view_model: ScenarioProjectionViewModel
    snapshot: Mapping[str, Any]
    report_payload: Mapping[str, Any]
    report_text: str

    def __post_init__(self) -> None:
        if not isinstance(self.inputs, ScenarioProjectionInputs):
            raise TypeError("inputs must be ScenarioProjectionInputs")
        if not isinstance(self.view_model, ScenarioProjectionViewModel):
            raise TypeError("view_model must be ScenarioProjectionViewModel")
        report = ScenarioProjectionReport()
        expected_payload = report.build_from_snapshot(self.snapshot)
        expected_text = report.render_text_from_snapshot(self.snapshot)
        if self.report_payload != expected_payload:
            raise ValueError("report_payload must match snapshot payload")
        if self.report_text != expected_text:
            raise ValueError("report_text must match snapshot text")
        object.__setattr__(self, "report_payload", self._freeze(self.report_payload))

    @staticmethod
    def _freeze(value: Any) -> Any:
        if isinstance(value, Mapping):
            return _FrozenDict({
                key: ScenarioProjectionWorkflowResult._freeze(item)
                for key, item in value.items()
            })
        if isinstance(value, list):
            return _FrozenList(ScenarioProjectionWorkflowResult._freeze(item) for item in value)
        if isinstance(value, tuple):
            return tuple(ScenarioProjectionWorkflowResult._freeze(item) for item in value)
        return value

    def export_bundle(
        self,
        directory: str | Any,
        stem: str = "retirement_projection",
        *,
        overwrite: bool = False,
    ) -> dict[str, Any]:
        """Export this already-published workflow result without rebuilding it."""
        return export_snapshot_bundle(
            self.snapshot,
            directory,
            stem,
            overwrite=overwrite,
        )


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

    def run_report_workflow(
        self,
        *,
        allocations: Mapping[str, float],
        fund_returns: Mapping[str, Sequence[float]],
        scenarios: Iterable[str] | None = None,
    ) -> ScenarioProjectionWorkflowResult:
        """Run one projection and publish its report/export-ready snapshot boundary."""
        selected = tuple(scenarios) if scenarios is not None else self.inputs().scenarios
        view_model = self.build_view_model(
            allocations=allocations,
            fund_returns=fund_returns,
            scenarios=selected,
        )
        snapshot = view_model.report_snapshot()
        report = ScenarioProjectionReport()
        return ScenarioProjectionWorkflowResult(
            inputs=ScenarioProjectionInputs(
                starting_pension=float(self.assumptions.get("starting_pension")),
                retirement_age=int(self.assumptions.get("retirement_age")),
                projection_end_age=int(self.assumptions.get("projection_end_age")),
                scenarios=selected,
            ),
            view_model=view_model,
            snapshot=snapshot,
            report_payload=report.build_from_snapshot(snapshot),
            report_text=report.render_text_from_snapshot(snapshot),
        )

    @staticmethod
    def export_workflow_result(
        result: ScenarioProjectionWorkflowResult,
        directory: str | Any,
        stem: str = "retirement_projection",
        *,
        overwrite: bool = False,
    ) -> dict[str, Any]:
        """Compatibility wrapper for exporting a published workflow result."""
        if not isinstance(result, ScenarioProjectionWorkflowResult):
            raise TypeError("result must be ScenarioProjectionWorkflowResult")
        return result.export_bundle(directory, stem, overwrite=overwrite)

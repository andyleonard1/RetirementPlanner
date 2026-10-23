"""GUI-neutral orchestration for the professional PDF report suite.

This module coordinates existing calculation/report boundaries. It does not
implement or alter any retirement-financial calculation logic.
"""
from __future__ import annotations

import copy
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Mapping, Sequence

from planner.adviser_engine import AdviserEngine
from planner.assumptions import Assumptions
from planner.goal_engine import GoalEngine
from planner.health_engine import HealthEngine
from planner.monte_carlo_engine import MonteCarloEngine
from planner.planner import RetirementPlanner
from planner.recommendations.report_adapter import RecommendationReportAdapter
from planner.recommendations.recommendation_quality import RecommendationQualityEngine
from planner.risk_engine import RiskEngine
from planner.scenario_engine import ScenarioEngine
from planner.scenarios.scenario import Scenario
from planner.scenarios.scenario_manager import ScenarioManager
from planner.projection import ScenarioProjectionWorkflowResult

from reports.goal_pdf_report import GoalPDFReport
from reports.health_check_pdf_report import HealthCheckPDFReport
from reports.recommendation_pdf_report import RecommendationPDFReport
from reports.scenario_projection_pdf_report import ScenarioProjectionPDFReport
from reports.strategy_comparison_pdf_report import StrategyComparisonPDFReport


REPORT_SUITE_KEYS = (
    "scenario_projection",
    "strategy_comparison",
    "recommendation",
    "health_check",
    "retirement_goals",
)


@dataclass(frozen=True)
class ReportSuiteExportResult:
    """Published paths for the five professional PDF reports."""

    scenario_projection: Path
    strategy_comparison: Path
    recommendation: Path
    health_check: Path
    retirement_goals: Path

    @property
    def paths(self) -> Mapping[str, Path]:
        return {
            "scenario_projection": self.scenario_projection,
            "strategy_comparison": self.strategy_comparison,
            "recommendation": self.recommendation,
            "health_check": self.health_check,
            "retirement_goals": self.retirement_goals,
        }


def export_report_suite(
    *,
    assumptions: Assumptions,
    scenario_result: ScenarioProjectionWorkflowResult,
    allocations: Mapping[str, float],
    fund_returns: Mapping[str, Sequence[float]],
    directory: str | Path,
    monte_carlo_iterations: int = 5000,
    monte_carlo_seed: int | None = None,
    overwrite: bool = False,
) -> ReportSuiteExportResult:
    """Generate all professional PDFs from the current application state.

    ``scenario_result`` is consumed directly for the scenario projection PDF;
    the other reports reuse their existing calculation engines against a deep
    copy of the supplied assumptions. No report renderer performs a second
    calculation. By default existing output files are protected; ``overwrite``
    enables recoverable replacement of the complete five-file bundle.
    """
    if not isinstance(assumptions, Assumptions):
        raise TypeError("assumptions must be an Assumptions instance")
    if not isinstance(scenario_result, ScenarioProjectionWorkflowResult):
        raise TypeError("scenario_result must be ScenarioProjectionWorkflowResult")
    if monte_carlo_iterations <= 0:
        raise ValueError("monte_carlo_iterations must be greater than zero")

    target_dir = Path(directory)
    target_dir.mkdir(parents=True, exist_ok=True)

    paths = ReportSuiteExportResult(
        scenario_projection=target_dir / "retirement_scenario_projection.pdf",
        strategy_comparison=target_dir / "retirement_strategy_comparison.pdf",
        recommendation=target_dir / "retirement_recommendation.pdf",
        health_check=target_dir / "retirement_health_check.pdf",
        retirement_goals=target_dir / "retirement_goals.pdf",
    )

    final_paths = paths.paths
    _validate_suite_destinations(final_paths, overwrite=overwrite)

    with TemporaryDirectory(prefix=".retirement-planner-report-suite-", dir=target_dir) as staging_name:
        staging_dir = Path(staging_name)
        staged_paths = ReportSuiteExportResult(
            scenario_projection=staging_dir / paths.scenario_projection.name,
            strategy_comparison=staging_dir / paths.strategy_comparison.name,
            recommendation=staging_dir / paths.recommendation.name,
            health_check=staging_dir / paths.health_check.name,
            retirement_goals=staging_dir / paths.retirement_goals.name,
        )

        ScenarioProjectionPDFReport().create(scenario_result, staged_paths.scenario_projection)

        comparison_results = ScenarioEngine(assumptions=copy.deepcopy(assumptions)).compare_strategies()
        StrategyComparisonPDFReport().create(comparison_results, staged_paths.strategy_comparison)

        recommendation_report, recommended_assumptions, result, decision, recommendations, risk = _build_recommendation(
            assumptions
        )
        RecommendationPDFReport().create(recommendation_report, staged_paths.recommendation)

        monte_carlo = MonteCarloEngine(copy.deepcopy(recommended_assumptions)).run(
            iterations=monte_carlo_iterations,
            seed=monte_carlo_seed,
        )
        health = HealthEngine().build(result.summary, recommendation_report, monte_carlo)
        goals = GoalEngine(copy.deepcopy(recommended_assumptions)).evaluate(
            result.summary,
            monte_carlo,
            result.timeline,
        )
        HealthCheckPDFReport().create(
            health,
            recommendation_report,
            monte_carlo,
            result.summary,
            staged_paths.health_check,
        )
        GoalPDFReport().create(goals, staged_paths.retirement_goals)

        _publish_pdf_bundle(staged_paths.paths, final_paths, overwrite=overwrite)

    return paths


def _validate_suite_destinations(paths: Mapping[str, Path], *, overwrite: bool) -> None:
    """Reject destination collisions before any report calculation or PDF write."""
    if overwrite:
        return
    conflicts = [path for path in paths.values() if path.exists()]
    if conflicts:
        raise FileExistsError(f"report suite destination already exists: {conflicts[0]}")


def _publish_pdf_bundle(
    staged_paths: Mapping[str, Path],
    final_paths: Mapping[str, Path],
    *,
    overwrite: bool = False,
) -> None:
    """Publish all five staged PDFs with rollback if any replacement fails."""
    if tuple(staged_paths) != tuple(final_paths):
        raise ValueError("staged and final report suites must have matching keys")
    destinations = tuple(final_paths.values())
    if len({path.parent.resolve() for path in destinations}) != 1:
        raise ValueError("report suite files must share one destination directory")
    if not overwrite:
        _validate_suite_destinations(final_paths, overwrite=False)

    backups: dict[Path, Path] = {}
    published: list[Path] = []
    try:
        parent = destinations[0].parent.resolve()
        for key, destination in final_paths.items():
            staged = staged_paths[key]
            if not staged.exists():
                raise FileNotFoundError(f"staged report was not created: {staged}")
            if overwrite and destination.exists():
                backup = parent / f".{destination.name}.backup"
                suffix = 1
                while backup.exists():
                    backup = parent / f".{destination.name}.backup.{suffix}"
                    suffix += 1
                destination.replace(backup)
                backups[destination] = backup

        for key, destination in final_paths.items():
            staged_paths[key].replace(destination)
            published.append(destination)
    except Exception:
        for destination in published:
            destination.unlink(missing_ok=True)
        for destination, backup in backups.items():
            if backup.exists():
                backup.replace(destination)
        raise
    finally:
        for backup in backups.values():
            backup.unlink(missing_ok=True)
        for staged in staged_paths.values():
            staged.unlink(missing_ok=True)


def build_scenarios(
    assumptions: Assumptions,
    minimum_age: int = 55,
    maximum_age: int = 75,
) -> list[Scenario]:
    """Build recommendation scenarios from a supplied assumptions baseline."""
    scenarios: list[Scenario] = []
    for age in range(minimum_age, maximum_age + 1):
        scenario_assumptions = copy.deepcopy(assumptions)
        scenario_assumptions.set("retirement_age", age)
        scenarios.append(Scenario(name=f"Retire {age}", assumptions=scenario_assumptions))
    return scenarios


def _build_recommendation(
    assumptions: Assumptions,
) -> tuple[dict[str, Any], Assumptions, Any, Any, list[Any], Any]:
    manager = ScenarioManager()
    for scenario in build_scenarios(assumptions):
        manager.add(scenario)

    decision = manager.decision_summary()
    recommendations = manager.recommendations()
    recommended_age = (
        decision.recommended_age
        if decision is not None
        else assumptions.get("retirement_age")
    )

    recommended_assumptions = copy.deepcopy(assumptions)
    recommended_assumptions.set("retirement_age", recommended_age)
    result = RetirementPlanner(recommended_assumptions).run()

    recommendations.insert(
        0,
        RecommendationQualityEngine().build(
            decision,
            result.optimisation_decision,
        ),
    )
    risk = RiskEngine().analyse(result.timeline)
    report = RecommendationReportAdapter().build(
        recommended_assumptions,
        result,
        decision,
        recommendations,
        risk,
    )
    return report, recommended_assumptions, result, decision, recommendations, risk

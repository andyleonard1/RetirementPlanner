"""
Run the defined assumption sensitivity grid through a supplied function or
through the real retirement planner.

The real-planner path is deliberately isolated from the live recommendation
path: it creates deep-copied assumptions for each case and never writes back
to the caller's assumptions.
"""

from dataclasses import dataclass
from collections import Counter
import copy

from .sensitivity_grid import SensitivityCase, SensitivityGrid


@dataclass(frozen=True, slots=True)
class SensitivityRun:
    case: SensitivityCase
    recommended_age: int | None
    successful_ages: tuple[int, ...] = ()


@dataclass(frozen=True, slots=True)
class SensitivitySummary:
    runs: tuple[SensitivityRun, ...]
    recommended_ages: tuple[int, ...]
    min_age: int | None
    max_age: int | None
    most_common_age: int | None
    most_common_count: int
    total_cases: int


class SensitivityRunner:
    def __init__(self, grid=None):
        self.grid = grid or SensitivityGrid()

    def run(self, recommend):
        results = tuple(
            SensitivityRun(case, recommend(case))
            for case in self.grid.cases()
        )
        return self._summarise(results)

    def run_real(self, assumptions, minimum_age=55, maximum_age=75):
        """Run every grid case through the real retirement planner.

        Returns a SensitivitySummary. The supplied assumptions object is never
        modified; each case gets a deep copy with the three sensitivity inputs
        changed.
        """
        from planner.recommendations.recommendation_engine import RecommendationEngine
        from planner.scenarios.scenario_comparison import ScenarioComparison
        from planner.services.retirement_solver import RetirementSolver
        from planner.scenarios.retirement_age_scoring_engine import RetirementAgeScoringEngine

        runs = []

        for case in self.grid.cases():
            case_assumptions = copy.deepcopy(assumptions)
            case_assumptions.set("pension_growth", case.pension_growth)
            case_assumptions.set("target_net_income", case.net_spending)
            case_assumptions.set("isa_growth_rate", case.isa_growth)

            results = RetirementSolver(case_assumptions).explore(
                minimum_age=minimum_age,
                maximum_age=maximum_age,
            )

            comparisons = []
            for age, result in zip(
                range(minimum_age, maximum_age + 1),
                results,
            ):
                summary = result.summary
                comparisons.append(
                    ScenarioComparison(
                        name=f"Age {age}",
                        success=result.success,
                        ending_assets=summary["ending_assets"],
                        ending_pension=summary["ending_pension"],
                        ending_isa=summary["ending_isa"],
                        ending_savings=summary["ending_savings"],
                        total_tax=summary["total_tax"],
                        retirement_age=age,
                    )
                )

            scores = RetirementAgeScoringEngine().score(comparisons)
            successful_scores = [score for score in scores if score.success]

            if successful_scores:
                recommended = max(
                    successful_scores,
                    key=lambda score: (
                        score.total_score,
                        -score.retirement_age,
                    ),
                )
                recommended_age = recommended.retirement_age
            else:
                recommended_age = None

            runs.append(
                SensitivityRun(
                    case=case,
                    recommended_age=recommended_age,
                    successful_ages=tuple(
                        comparison.retirement_age
                        for comparison in comparisons
                        if comparison.success
                    ),
                )
            )

        return self._summarise(tuple(runs))

    @staticmethod
    def _summarise(results):
        ages = tuple(
            sorted(
                result.recommended_age
                for result in results
                if result.recommended_age is not None
            )
        )
        counts = Counter(ages)
        common = counts.most_common(1)

        return SensitivitySummary(
            runs=tuple(results),
            recommended_ages=ages,
            min_age=min(ages) if ages else None,
            max_age=max(ages) if ages else None,
            most_common_age=common[0][0] if common else None,
            most_common_count=common[0][1] if common else 0,
            total_cases=len(results),
        )

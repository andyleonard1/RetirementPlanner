"""
Scenario Manager

Stores and manages retirement planning scenarios.
"""

from planner.planner import RetirementPlanner

from planner.scenarios.scenario_comparison import (
    ScenarioComparison,
)

from planner.scenarios.decision_summary import (
    DecisionSummary,
)

from planner.recommendations.recommendation_engine import (
    RecommendationEngine,
)

from planner.scenarios.retirement_age_comparison import (
    RetirementAgeComparison,
)

from planner.scenarios.retirement_age_tradeoff import (
    RetirementAgeTradeoff,
)

from planner.scenarios.retirement_age_scoring_engine import (
    RetirementAgeScoringEngine,
)
class ScenarioManager:

    def __init__(self):
        self._scenarios = []

    # -----------------------------------------

    def add(self, scenario):
        self._scenarios.append(scenario)

    # -----------------------------------------

    def all(self):
        return list(self._scenarios)

    # -----------------------------------------

    def count(self):
        return len(self._scenarios)

    # -----------------------------------------

    def run_all(self):

        results = []

        for scenario in self._scenarios:

            planner = RetirementPlanner(
                scenario.assumptions
            )

            results.append(
                planner.run()
            )

        return results

    # -----------------------------------------

    def compare(self):

        comparisons = []

        for scenario in self._scenarios:

            planner = RetirementPlanner(
                scenario.assumptions
            )

            result = planner.run()

            comparisons.append(
                ScenarioComparison(
                    name=scenario.name,

                    success=result.success,

                    ending_assets=result.summary[
                        "ending_assets"
                    ],

                    ending_pension=result.summary[
                        "ending_pension"
                    ],

                    ending_isa=result.summary[
                        "ending_isa"
                    ],

                    ending_savings=result.summary[
                        "ending_savings"
                    ],

                    total_tax=result.summary[
                        "total_tax"
                    ],

                    retirement_age=scenario.assumptions.get(
                        "retirement_age"
                    ),
                )
            )

        return comparisons

    # -----------------------------------------
    # -----------------------------------------

    def retirement_age_comparison(self):

        comparisons = self.compare()

        comparisons = sorted(
            comparisons,
            key=lambda comparison:
            comparison.retirement_age,
        )

        results = []

        previous_assets = None

        for comparison in comparisons:

            if previous_assets is None:

                change_from_previous_age = None

            else:

                change_from_previous_age = (
                    comparison.ending_assets
                    - previous_assets
                )

            results.append(
                RetirementAgeComparison(
                    retirement_age=(
                        comparison.retirement_age
                    ),

                    success=(
                        comparison.success
                    ),

                    ending_assets=(
                        comparison.ending_assets
                    ),

                    ending_pension=(
                        comparison.ending_pension
                    ),

                    ending_isa=(
                        comparison.ending_isa
                    ),

                    ending_savings=(
                        comparison.ending_savings
                    ),

                    total_tax=(
                        comparison.total_tax
                    ),

                    change_from_previous_age=(
                        change_from_previous_age
                    ),
                )
            )

            previous_assets = (
                comparison.ending_assets
            )

        return results

    # -----------------------------------------

    def retirement_age_tradeoffs(self):

        comparisons = sorted(
            self.compare(),
            key=lambda comparison:
            comparison.retirement_age,
        )

        successful = [
            comparison
            for comparison in comparisons
            if comparison.success
        ]

        if not successful:
            return []

        starting = min(
            successful,
            key=lambda comparison:
            comparison.retirement_age,
        )

        tradeoffs = []

        for later in comparisons:

            if later.retirement_age <= starting.retirement_age:
                continue

            years_waited = (
                later.retirement_age
                - starting.retirement_age
            )

            additional_assets = (
                later.ending_assets
                - starting.ending_assets
            )

            tradeoffs.append(
                RetirementAgeTradeoff(
                    starting_age=(
                        starting.retirement_age
                    ),
                    later_age=(
                        later.retirement_age
                    ),
                    years_waited=years_waited,
                    starting_assets=(
                        starting.ending_assets
                    ),
                    later_assets=(
                        later.ending_assets
                    ),
                    additional_assets=(
                        additional_assets
                    ),
                    additional_assets_per_year=(
                        additional_assets / years_waited
                    ),
                    later_success=(
                        later.success
                    ),
                )
            )

        return tradeoffs

    def retirement_age_scores(self):

        return RetirementAgeScoringEngine().score(
            self.compare()
        )

    # -----------------------------------------

    def recommendations(self):

        comparisons = self.compare()
        tradeoffs = self.retirement_age_tradeoffs()

        return RecommendationEngine().generate(
            comparisons,
            tradeoffs,
        )

    # -----------------------------------------

    def decision_summary(self):

        comparisons = self.compare()

        successful = [
            comparison
            for comparison in comparisons
            if comparison.success
        ]

        if not successful:
            return None

        earliest = min(
            successful,
            key=lambda comparison:
            comparison.retirement_age
        )

        later_age = earliest.retirement_age + 1

        later = next(
            (
                comparison
                for comparison in comparisons
                if comparison.retirement_age
                == later_age
            ),
            None,
        )

        if later is not None:

            additional_assets = (
                later.ending_assets
                - earliest.ending_assets
            )

            later_ending_assets = (
                later.ending_assets
            )

        else:

            additional_assets = None
            later_ending_assets = None

        return DecisionSummary(

            recommended_age=(
                earliest.retirement_age
            ),

            ending_pension=(
                earliest.ending_pension
            ),

            ending_isa=(
                earliest.ending_isa
            ),

            ending_savings=(
                earliest.ending_savings
            ),

            ending_assets=(
                earliest.ending_assets
            ),

            later_age=(
                later_age
                if later is not None
                else None
            ),

            later_ending_assets=(
                later_ending_assets
            ),

            additional_assets_from_waiting=(
                additional_assets
            ),
        )

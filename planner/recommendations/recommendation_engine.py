"""
Recommendation Engine

Produces human-readable recommendations based on
scenario comparison results.
"""

from planner.recommendations.recommendation import Recommendation


class RecommendationEngine:

    # -------------------------------------------------
    # Find the earliest retirement age that succeeds
    # -------------------------------------------------

    def _earliest_successful_age(self, comparisons):

        successful = [
            comparison
            for comparison in comparisons
            if comparison.success
        ]

        if not successful:
            return None

        return min(
            comparison.retirement_age
            for comparison in successful
        )

    # -------------------------------------------------
    # Find the successful age with the highest ending assets
    # -------------------------------------------------

    def _highest_ending_assets_successful_age(self, comparisons):

        successful = [
            comparison
            for comparison in comparisons
            if comparison.success
        ]

        if not successful:
            return None

        return max(
            successful,
            key=lambda comparison:
            comparison.ending_assets,
        )

    # -------------------------------------------------
    # Find a scenario for a specific retirement age
    # -------------------------------------------------

    def _scenario_at_age(
        self,
        comparisons,
        age,
    ):

        for comparison in comparisons:

            if comparison.retirement_age == age:
                return comparison

        return None

    # -------------------------------------------------
    # Find the most useful later successful retirement trade-off
    # -------------------------------------------------

    def _best_waiting_tradeoff(self, tradeoffs):

        successful = [
            tradeoff
            for tradeoff in tradeoffs
            if tradeoff.later_success
        ]

        if not successful:
            return None

        return max(
            successful,
            key=lambda tradeoff: (
                tradeoff.additional_assets_per_year,
                tradeoff.additional_assets,
            ),
        )

    # -------------------------------------------------
    # Generate recommendations
    # -------------------------------------------------

    def generate(self, comparisons, tradeoffs=None):

        recommendations = []

        if not comparisons:
            return recommendations

        #
        # -------------------------------------------------
        # 1. EARLIEST SUCCESSFUL RETIREMENT AGE
        # -------------------------------------------------
        #

        earliest_age = self._earliest_successful_age(
            comparisons
        )

        if earliest_age is not None:

            recommendations.append(
                Recommendation(
                    priority=1,
                    title="Recommended Retirement Age",
                    message=(
                        f"Age {earliest_age} is the earliest "
                        "tested retirement age that satisfies "
                        "the current planning goals."
                    ),
                    impact=(
                        f"Earliest successful retirement age: "
                        f"{earliest_age}"
                    ),
                )
            )

            #
            # -------------------------------------------------
            # 2. HIGHEST PROJECTED ENDING ASSETS
            # -------------------------------------------------

            strongest = self._highest_ending_assets_successful_age(
                comparisons
            )

            if (
                strongest is not None
                and strongest.retirement_age != earliest_age
            ):

                recommendations.append(
                    Recommendation(
                        priority=2,
                        title="Highest Projected Ending Assets",
                        message=(
                            f"Age {strongest.retirement_age} produces "
                            "the highest projected ending assets among "
                            "the successful retirement ages tested."
                        ),
                        impact=(
                            f"Projected ending assets: "
                            f"£{strongest.ending_assets:,.0f}"
                        ),
                    )
                )

            #
            # -------------------------------------------------
            # 3. BENEFIT OF WAITING ONE YEAR
            # -------------------------------------------------
            #

            later_age = earliest_age + 1

            later_scenario = self._scenario_at_age(
                comparisons,
                later_age,
            )

            earliest_scenario = self._scenario_at_age(
                comparisons,
                earliest_age,
            )

            if (
                later_scenario is not None
                and earliest_scenario is not None
            ):

                asset_difference = (
                    later_scenario.ending_assets
                    - earliest_scenario.ending_assets
                )

                if asset_difference > 0:

                    recommendations.append(
                        Recommendation(
                            priority=2,
                            title="Benefit of Waiting One Year",
                            message=(
                                f"Waiting until age {later_age} "
                                "increases projected ending "
                                "assets compared with retiring "
                                f"at age {earliest_age}."
                            ),
                            impact=(
                                f"Additional projected ending "
                                f"assets: "
                                f"£{asset_difference:,.0f}"
                            ),
                        )
                    )

                elif asset_difference < 0:

                    recommendations.append(
                        Recommendation(
                            priority=2,
                            title="Benefit of Waiting One Year",
                            message=(
                                f"Waiting until age {later_age} "
                                "does not improve projected "
                                f"ending assets compared with "
                                f"age {earliest_age}."
                            ),
                            impact=(
                                f"Projected ending assets are "
                                f"£{abs(asset_difference):,.0f} "
                                "lower."
                            ),
                        )
                    )

                else:

                    recommendations.append(
                        Recommendation(
                            priority=2,
                            title="Benefit of Waiting One Year",
                            message=(
                                f"Waiting until age {later_age} "
                                "produces the same projected "
                                "ending assets as retiring at "
                                f"age {earliest_age}."
                            ),
                            impact=(
                                "No change in projected "
                                "ending assets."
                            ),
                        )
                    )

        #
        # -------------------------------------------------
        # 4. RETIREMENT AGE TRADE-OFF
        # -------------------------------------------------
        #

        if tradeoffs:

            tradeoff = self._best_waiting_tradeoff(
                tradeoffs
            )

            if tradeoff is not None:

                recommendations.append(
                    Recommendation(
                        priority=3,
                        title="Retirement Age Trade-off",
                        message=(
                            f"Waiting until age {tradeoff.later_age} "
                            f"adds projected assets compared with "
                            f"retiring at age {tradeoff.starting_age}."
                        ),
                        impact=(
                            f"Additional projected assets: "
                            f"£{tradeoff.additional_assets:,.0f}; "
                            f"£{tradeoff.additional_assets_per_year:,.0f} "
                            "per year waited."
                        ),
                    )
                )

        #
        # -------------------------------------------------
        # 5. INDIVIDUAL SCENARIO STATUS
        # -------------------------------------------------
        #

        for comparison in comparisons:

            if comparison.success:

                recommendations.append(
                    Recommendation(
                        priority=4,
                        title="Plan Successful",
                        message=(
                            f"The retirement plan "
                            f"'{comparison.name}' meets "
                            "the current planning goals."
                        ),
                        impact=(
                            f"Projected ending assets "
                            f"£{comparison.ending_assets:,.0f}"
                        ),
                    )
                )

            else:

                recommendations.append(
                    Recommendation(
                        priority=4,
                        title="Plan Not Sustainable",
                        message=(
                            f"The retirement plan "
                            f"'{comparison.name}' does not meet "
                            "the current planning goals."
                        ),
                        impact=(
                            "Consider retiring later or "
                            "reducing spending."
                        ),
                    )
                )

        #
        # -------------------------------------------------
        # 4. SORT BY PRIORITY
        # -------------------------------------------------
        #

        recommendations.sort(
            key=lambda recommendation: (
                recommendation.priority
            )
        )

        return recommendations

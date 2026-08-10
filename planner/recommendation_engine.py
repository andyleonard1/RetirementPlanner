"""
Recommendation Engine

Produces human-readable recommendations based on
scenario comparison results.
"""

from planner.recommendations.recommendation import Recommendation


class RecommendationEngine:

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

    def generate(self, comparisons):
        print("RECOMMENDATION ENGINE:", __file__)
        print("COMPARISONS:", comparisons)
        if not comparisons:
            return []

        recommendations = []

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
        # 2. INDIVIDUAL SCENARIO STATUS
        # -------------------------------------------------
        #

        for comparison in comparisons:

            if comparison.success:

                recommendations.append(
                    Recommendation(
                        priority=2,
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
                        priority=2,
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
        # 3. ENSURE PRIORITY ORDER
        # -------------------------------------------------
        #

        recommendations.sort(
            key=lambda recommendation: recommendation.priority
        )

        return recommendations
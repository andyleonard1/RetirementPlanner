"""
Retirement Age Scoring Engine

Calculates transparent comparison scores for tested retirement ages.
This layer supplies decision data; it does not choose the final
recommended retirement age.
"""

from planner.scenarios.retirement_age_score import RetirementAgeScore


class RetirementAgeScoringEngine:

    EARLIEST_AGE_WEIGHT = 0.40
    ENDING_ASSETS_WEIGHT = 0.40
    WAITING_EFFICIENCY_WEIGHT = 0.20

    def score(self, comparisons):

        if not comparisons:
            return []

        ordered = sorted(
            comparisons,
            key=lambda comparison: comparison.retirement_age,
        )

        successful = [
            comparison
            for comparison in ordered
            if comparison.success
        ]

        if not successful:
            return [
                RetirementAgeScore(
                    retirement_age=comparison.retirement_age,
                    success=False,
                    earliest_age_score=0.0,
                    ending_assets_score=0.0,
                    waiting_efficiency_score=0.0,
                    total_score=0.0,
                )
                for comparison in ordered
            ]

        earliest_age = successful[0].retirement_age
        latest_age = successful[-1].retirement_age

        asset_values = [
            comparison.ending_assets
            for comparison in successful
        ]
        min_assets = min(asset_values)
        max_assets = max(asset_values)

        earliest_assets = successful[0].ending_assets

        efficiency_values = {}
        for comparison in successful:
            if comparison.retirement_age == earliest_age:
                efficiency_values[comparison.retirement_age] = 0.0
                continue

            years_waited = (
                comparison.retirement_age - earliest_age
            )

            efficiency_values[comparison.retirement_age] = (
                (comparison.ending_assets - earliest_assets)
                / years_waited
            )

        later_efficiencies = [
            value
            for age, value in efficiency_values.items()
            if age != earliest_age
        ]

        max_efficiency = (
            max(later_efficiencies)
            if later_efficiencies
            else 0.0
        )

        min_efficiency = (
            min(later_efficiencies)
            if later_efficiencies
            else 0.0
        )

        results = []

        for comparison in ordered:

            if not comparison.success:
                results.append(
                    RetirementAgeScore(
                        retirement_age=comparison.retirement_age,
                        success=False,
                        earliest_age_score=0.0,
                        ending_assets_score=0.0,
                        waiting_efficiency_score=0.0,
                        total_score=0.0,
                    )
                )
                continue

            if latest_age == earliest_age:
                earliest_age_score = 100.0
            else:
                earliest_age_score = (
                    100.0
                    * (latest_age - comparison.retirement_age)
                    / (latest_age - earliest_age)
                )

            if max_assets == min_assets:
                ending_assets_score = 100.0
            else:
                ending_assets_score = (
                    100.0
                    * (comparison.ending_assets - min_assets)
                    / (max_assets - min_assets)
                )

            if comparison.retirement_age == earliest_age:
                waiting_efficiency_score = 0.0
            elif max_efficiency == min_efficiency:
                waiting_efficiency_score = 100.0
            else:
                waiting_efficiency_score = (
                    100.0
                    * (
                        efficiency_values[comparison.retirement_age]
                        - min_efficiency
                    )
                    / (max_efficiency - min_efficiency)
                )

            total_score = (
                earliest_age_score * self.EARLIEST_AGE_WEIGHT
                + ending_assets_score * self.ENDING_ASSETS_WEIGHT
                + waiting_efficiency_score
                * self.WAITING_EFFICIENCY_WEIGHT
            )

            results.append(
                RetirementAgeScore(
                    retirement_age=comparison.retirement_age,
                    success=True,
                    earliest_age_score=earliest_age_score,
                    ending_assets_score=ending_assets_score,
                    waiting_efficiency_score=waiting_efficiency_score,
                    total_score=total_score,
                )
            )

        return results

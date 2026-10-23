"""Build robust, human-readable overall retirement recommendations."""

from planner.recommendations.recommendation import Recommendation


class RecommendationQualityEngine:
    """Combine existing retirement-age and optimisation decisions safely.

    This is an interpretation layer only. It never mutates either input and
    deliberately avoids manufacturing a recommendation when the underlying
    decision data is incomplete.
    """

    def _safe_age(self, decision):
        age = getattr(decision, "recommended_age", None)
        return age if isinstance(age, (int, float)) else None

    def _safe_score(self, decision):
        score = getattr(decision, "total_score", None)
        return score if isinstance(score, (int, float)) else None

    def _optimisation_text(self, decision):
        if decision is None:
            return None

        recommendation = getattr(decision, "recommendation", None)
        higher_policy = getattr(decision, "higher_policy", None)
        material = getattr(decision, "material", False)

        if not hasattr(decision, "higher_policy") and not hasattr(decision, "recommendation"):
            return "No optimisation policy advantage is established by the available analysis."
        maximum_age = getattr(decision, "maximum_difference_age", None)

        if higher_policy is None:
            return "The tested optimisation policies are effectively equivalent."

        if material:
            text = f"Use {higher_policy} as the preferred optimisation policy because the difference is material."
        else:
            text = (
                f"{higher_policy} provides the higher tax-efficient pension capacity, "
                "but the difference is not material."
            )

        if maximum_age is not None:
            text += f" Its largest tested advantage occurs at age {maximum_age}."

        return text

    def build(self, retirement_decision, optimisation_decision):
        age = self._safe_age(retirement_decision) if retirement_decision is not None else None
        score = self._safe_score(retirement_decision) if retirement_decision is not None else None

        if retirement_decision is None or age is None:
            optimisation_text = self._optimisation_text(optimisation_decision)
            return Recommendation(
                priority=0,
                title="Overall Retirement Strategy",
                message="No reliable retirement-age decision is available for the current plan.",
                impact=(
                    "The overall strategy cannot be selected from incomplete retirement-age analysis. "
                    + (optimisation_text or "No optimisation decision is available.")
                ),
            )

        if optimisation_decision is None:
            impact = (
                f"Retirement-age score: {score:.1f}/100. "
                "No optimisation policy comparison is available."
                if score is not None
                else "Retirement-age score is unavailable. No optimisation policy comparison is available."
            )
            return Recommendation(
                0,
                "Overall Retirement Strategy",
                f"Retire at age {age} based on the current retirement-age analysis.",
                impact,
            )

        optimisation_text = self._optimisation_text(optimisation_decision)
        explanation = getattr(optimisation_decision, "explanation", None)
        maximum_age = getattr(optimisation_decision, "maximum_difference_age", None)

        message = f"Retire at age {age} based on the current retirement-age analysis."
        if optimisation_text:
            message += " " + optimisation_text

        # If the optimisation advantage peaks at another age, explicitly
        # qualify it rather than allowing the two analyses to appear to be in
        # conflict. The retirement-age decision remains authoritative for age.
        if maximum_age is not None and maximum_age != age:
            message += (
                f" The optimisation difference is largest at age {maximum_age}; "
                "this does not change the selected retirement age."
            )

        if score is not None:
            impact = f"Retirement-age score: {score:.1f}/100."
        else:
            impact = "Retirement-age score is unavailable."

        if explanation:
            impact += " " + explanation

        return Recommendation(0, "Overall Retirement Strategy", message, impact)

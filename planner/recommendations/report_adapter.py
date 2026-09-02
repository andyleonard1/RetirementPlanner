"""
Recommendation report adapter.

Bridges the current retirement-age recommendation architecture to the
legacy dictionary-based reporting interfaces used by the console health
and recommendation reports.
"""

from planner.audit_catalog import description


class RecommendationReportAdapter:

    def build(
        self,
        assumptions,
        result,
        decision,
        recommendations,
        risk,
    ):
        """Build the report dictionary expected by legacy report consumers."""

        total_score = (
            decision.total_score
            if decision is not None
            and decision.total_score is not None
            else 0.0
        )

        confidence = self._confidence(total_score)

        reasons = [
            recommendation.message
            for recommendation in recommendations
            if recommendation.priority <= 3
        ]

        if not reasons:
            reasons = [
                "No successful retirement-age recommendation was identified."
            ]

        summary = result.summary

        return {
            "strategy": assumptions.get("withdrawal_strategy"),
            "confidence": confidence,
            "reasons": reasons,
            "ending_assets": summary["ending_assets"],
            "ending_pension": summary["ending_pension"],
            "ending_isa": summary["ending_isa"],
            "ending_savings": summary["ending_savings"],
            "total_tax": summary["total_tax"],
            "risk_rating": risk.rating,
            "risk_score": risk.score,
            "risk_messages": risk.risks,
            "recommended_age": (
                decision.recommended_age
                if decision is not None
                else assumptions.get("retirement_age")
            ),
            "recommendation_score": total_score,
            "optimisation_decision": self._optimisation_decision(result),
            "overall_recommendation": self._overall_recommendation(recommendations),
            "assumption_changes": [
                {
                    "path": change.path,
                    "before": change.before,
                    "after": change.after,
                    "category": self._change_category(
                        getattr(result, "audit_context", "user")
                    ),
                    "description": self._change_description(
                        change.path,
                        getattr(result, "audit_context", "user"),
                    ),
                    "before_display": self._format_change_value(change.before),
                    "after_display": self._format_change_value(change.after),
                }
                for change in getattr(result, "assumption_changes", ())
            ],
        }


    @staticmethod
    def _overall_recommendation(recommendations):
        for recommendation in recommendations:
            if recommendation.title == "Overall Retirement Strategy":
                return {
                    "title": recommendation.title,
                    "message": recommendation.message,
                    "impact": recommendation.impact,
                }
        return None

    @staticmethod
    def _optimisation_decision(result):
        decision = getattr(result, "optimisation_decision", None)
        if decision is None:
            return None

        return {
            "higher_policy": decision.higher_policy,
            "lower_policy": decision.lower_policy,
            "average_difference": decision.average_difference,
            "maximum_difference": decision.maximum_difference,
            "maximum_difference_age": decision.maximum_difference_age,
            "material": decision.material,
            "recommendation": decision.recommendation,
            "explanation": decision.explanation,
        }

    @staticmethod
    def _change_category(context):
        labels = {
            "user": "USER ASSUMPTION",
            "scenario": "SCENARIO",
            "recommendation": "RECOMMENDATION",
            "analysis": "ANALYSIS",
        }
        return labels.get(context, "USER ASSUMPTION")

    @staticmethod
    def _change_description(path, context):
        return description(path, context)

    @staticmethod
    def _format_change_value(value):
        if value is None:
            return "not set"
        if isinstance(value, float):
            if value != value:
                return "NaN"
            return f"{value:g}"
        return str(value)

    @staticmethod
    def _confidence(score):
        """Translate the 0-100 retirement-age score into a report confidence."""

        if score >= 90:
            return "VERY HIGH"
        if score >= 75:
            return "HIGH"
        if score >= 60:
            return "MEDIUM"
        return "LOW"

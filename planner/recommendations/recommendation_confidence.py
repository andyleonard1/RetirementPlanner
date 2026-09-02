"""
Recommendation Confidence

Combines the available recommendation evidence into a conservative,
human-readable confidence assessment. This is a read-only reporting layer.
"""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RecommendationConfidence:
    level: str
    score: float
    reasons: tuple[str, ...]


class RecommendationConfidenceEngine:
    """Assess confidence without changing the underlying recommendation."""

    def analyse(
        self,
        decision=None,
        scores=(),
        optimisation_material=False,
        risk_score=None,
    ):
        if decision is None or decision.total_score is None:
            return RecommendationConfidence(
                level="LOW",
                score=0.0,
                reasons=("No complete retirement-age decision is available.",),
            )

        total = float(decision.total_score)
        successful = [
            s for s in scores
            if getattr(s, "success", False)
        ]

        points = max(0.0, min(100.0, total))
        reasons = []

        if total >= 90:
            reasons.append("The retirement-age score is very strong.")
        elif total >= 75:
            reasons.append("The retirement-age score is strong.")
        elif total >= 60:
            reasons.append("The retirement-age score provides moderate support.")
        else:
            reasons.append("The retirement-age score provides limited support.")

        if len(successful) == 1:
            points += 5
            reasons.append("Only one sustainable retirement age was identified.")
        elif len(successful) >= 2:
            ordered = sorted(
                successful,
                key=lambda s: float(getattr(s, "total_score", 0.0)),
                reverse=True,
            )
            margin = (
                float(getattr(ordered[0], "total_score", 0.0))
                - float(getattr(ordered[1], "total_score", 0.0))
            )
            if margin >= 10:
                points += 5
                reasons.append("The preferred retirement age has a clear score advantage.")
            elif margin >= 3:
                reasons.append("The preferred retirement age has a modest score advantage.")
            else:
                points -= 10
                reasons.append("Several sustainable ages have similar scores.")

        if optimisation_material:
            points -= 5
            reasons.append(
                "A material optimisation-policy difference adds an additional decision trade-off."
            )
        else:
            points += 5
            reasons.append("Optimisation-policy differences are not material.")

        if risk_score is not None:
            risk = float(risk_score)
            if risk <= 3:
                points += 5
                reasons.append("The assessed retirement risk is low.")
            elif risk >= 7:
                points -= 10
                reasons.append("The assessed retirement risk is relatively high.")

        score = max(0.0, min(100.0, points))

        if score >= 75:
            level = "HIGH"
        elif score >= 60:
            level = "MEDIUM"
        else:
            level = "LOW"

        return RecommendationConfidence(
            level=level,
            score=round(score, 1),
            reasons=tuple(reasons),
        )

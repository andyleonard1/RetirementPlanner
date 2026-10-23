"""
Health Engine

Produces an overall retirement health assessment from the
completed plan, recommendation and Monte Carlo results.
"""

import logging

logger = logging.getLogger(__name__)


class HealthEngine:

    def __init__(self):

        pass

    def build(self, summary, recommendation, monte_carlo):

        score = 0

        reasons = []

        #
        # Monte Carlo
        #

        success = monte_carlo.success_rate

        if success >= 99:
            score += 30
            reasons.append("Outstanding probability of success")

        elif success >= 95:
            score += 27
            reasons.append("Very high probability of success")

        elif success >= 90:
            score += 24
            reasons.append("High probability of success")

        elif success >= 80:
            score += 18
            reasons.append("Reasonable probability of success")

        else:
            score += 10
            reasons.append("Investment risk is elevated")

        #
        # Pension remaining
        #

        if summary["ending_pension"] > 0:
            score += 20
            reasons.append("Pension fund remains positive")

        #
        # ISA remaining
        #

        if summary["ending_isa"] > 0:
            score += 10
            reasons.append("ISA remains positive")

        #
        # Savings remaining
        #

        if summary["ending_savings"] > 0:
            score += 10
            reasons.append("Cash savings remain positive")

        #
        # Estate value
        #

        if summary["ending_assets"] > 1000000:
            score += 10

        elif summary["ending_assets"] > 500000:
            score += 8

        elif summary["ending_assets"] > 250000:
            score += 5

        #
        # Tax efficiency
        #

        if summary["total_tax"] < 50000:
            score += 10

        elif summary["total_tax"] < 100000:
            score += 7

        else:
            score += 4

        #
        # Recommendation confidence
        #

        confidence = recommendation["confidence"]

        if confidence == "VERY HIGH":
            score += 10

        elif confidence == "HIGH":
            score += 8

        elif confidence == "MEDIUM":
            score += 5

        #
        # Overall rating
        #

        rating = self._rating(score)

        logger.info(
            "Retirement Health Score %.1f/10",
            score / 10,
        )

        return {

            "score": round(score / 10, 1),

            "rating": rating,

            "reasons": reasons,

        }

    # -------------------------------------------------

    def _rating(self, score):

        if score >= 90:
            return "EXCELLENT"

        if score >= 75:
            return "VERY GOOD"

        if score >= 60:
            return "GOOD"

        if score >= 40:
            return "FAIR"

        return "POOR"
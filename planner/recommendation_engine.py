"""
Recommendation Engine

Produces a plain-English explanation of the
recommended retirement strategy.
"""


class RecommendationEngine:

    def apply(self, decision):
        risk = decision["risk"]
        winner = decision["summary"]
        strategy = decision["recommended"]

        runner = decision.get("runner_up")

        reasons = []

        confidence = "LOW"

        if runner:

            loser = runner["summary"]

            asset_gain = (
                winner["ending_assets"]
                - loser["ending_assets"]
            )

            tax_saved = (
                loser["total_tax"]
                - winner["total_tax"]
            )

            pension_gain = (
                winner["ending_pension"]
                - loser["ending_pension"]
            )

            isa_gain = (
                winner["ending_isa"]
                - loser["ending_isa"]
            )

            savings_gain = (
                winner["ending_savings"]
                - loser["ending_savings"]
            )

            if asset_gain > 0:
                reasons.append(
                    f"Leaves £{asset_gain:,.0f} more total assets."
                )

            if tax_saved > 0:
                reasons.append(
                    f"Saves £{tax_saved:,.0f} in lifetime tax."
                )

            if pension_gain > 0:
                reasons.append(
                    f"Retains £{pension_gain:,.0f} more pension wealth."
                )

            if isa_gain > 0:
                reasons.append(
                    f"Retains £{isa_gain:,.0f} more ISA wealth."
                )

            if savings_gain > 0:
                reasons.append(
                    f"Retains £{savings_gain:,.0f} more cash savings."
                )

            #
            # Confidence
            #
            if asset_gain > 250000:
                confidence = "VERY HIGH"

            elif asset_gain > 100000:
                confidence = "HIGH"

            elif asset_gain > 25000:
                confidence = "MEDIUM"

            else:
                confidence = "LOW"

        else:

            reasons.append(
                "Only one strategy was available for comparison."
            )

        return {

            "strategy": strategy,

            "ending_assets": winner["ending_assets"],

            "ending_pension": winner["ending_pension"],

            "ending_isa": winner["ending_isa"],

            "ending_savings": winner["ending_savings"],

            "total_tax": winner["total_tax"],

            "confidence": confidence,

            "reasons": reasons,
            
            "risk_rating": risk["rating"],

            "risk_score": risk["score"],

            "risk_messages": risk["risks"],
        }
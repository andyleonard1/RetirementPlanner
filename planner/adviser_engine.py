"""
Adviser Engine

Produces a human-readable explanation of the retirement plan.
"""

import logging

logger = logging.getLogger(__name__)


class AdviserEngine:

    def build(
        self,
        summary,
        recommendation,
        monte_carlo,
        health,
    ):

        logger.info("Running Adviser Engine")

        paragraphs = []

        #
        # Overall assessment
        #

        paragraphs.append(

            f"Overall retirement health is "
            f"{health['rating']} "
            f"with a score of "
            f"{health['score']:.1f}/10."

        )

        #
        # Monte Carlo
        #

        success = monte_carlo.success_rate

        if success >= 95:

            paragraphs.append(

                "The Monte Carlo simulation "
                "shows a very high probability "
                "that your retirement plan will "
                "remain financially sustainable."

            )

        elif success >= 90:

            paragraphs.append(

                "The retirement plan appears "
                "robust under most investment "
                "conditions."

            )

        elif success >= 80:

            paragraphs.append(

                "The retirement plan is broadly "
                "sustainable but could benefit "
                "from additional contingency."

            )

        else:

            paragraphs.append(

                "Investment risk is relatively "
                "high and the retirement plan "
                "may require changes."

            )

        #
        # Assets
        #

        assets = summary["ending_assets"]

        paragraphs.append(

            f"Projected remaining assets at "
            f"age 90 are approximately "
            f"£{assets:,.0f}."

        )

        #
        # Recommendation
        #

        paragraphs.append(

            f"The recommended withdrawal "
            f"strategy is "
            f"{recommendation['strategy']}."

        )

        paragraphs.append(

            f"Recommendation confidence is "
            f"{recommendation['confidence']}."

        )

        #
        # Tax
        #

        paragraphs.append(

            f"Estimated lifetime income tax "
            f"is £{summary['total_tax']:,.0f}."

        )

        #
        # Strengths
        #

        if health["reasons"]:

            paragraphs.append(

                "Key strengths include: "

                + ", ".join(health["reasons"]) + "."

            )

        return paragraphs
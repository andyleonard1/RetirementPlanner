"""
Risk Engine

Analyses a completed retirement projection and
identifies potential risks.
"""

from planner.results import RiskResult


class RiskEngine:

    def analyse(self, timeline):

        risks = []
        score = 10

        pension_empty = any(
            year.closing_pension <= 0
            for year in timeline
        )

        if pension_empty:
            risks.append("Pension exhausted.")
            score -= 3
        else:
            risks.append("Pension never exhausted.")

        isa_empty = any(
            year.isa_remaining <= 0
            for year in timeline
        )

        if isa_empty:
            risks.append("ISA exhausted.")
            score -= 2
        else:
            risks.append("ISA remains positive.")

        savings_empty = any(
            year.savings_remaining <= 0
            for year in timeline
        )

        if savings_empty:
            risks.append("Savings exhausted.")
            score -= 1
        else:
            risks.append("Savings remain positive.")

        shortfall = any(
            year.income_shortfall > 0
            for year in timeline
        )

        if shortfall:
            risks.append("Income shortfall detected.")
            score -= 4
        else:
            risks.append("Target spending achieved every year.")

        score = max(score, 0)

        if score >= 9:
            rating = "LOW"
        elif score >= 7:
            rating = "MEDIUM"
        else:
            rating = "HIGH"

        return RiskResult(
            score=score,
            rating=rating,
            risks=risks,
        )

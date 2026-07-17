"""
Savings Engine

Projects the user's cash savings over time.
"""


class SavingsEngine:

    def __init__(self, assumptions):

        self.assumptions = assumptions

        self.starting_savings = assumptions.get("starting_savings")
        self.interest_rate = assumptions.get("savings_interest_rate")

    def apply(self, timeline):

        savings = self.starting_savings

        for year in timeline:

            opening = savings

            interest = opening * self.interest_rate

            # Nothing moves in or out yet
            money_in = 0.0
            money_out = 0.0

            closing = opening + interest + money_in - money_out

            year.savings_opening = round(opening, 2)
            year.savings_interest = round(interest, 2)
            year.savings_money_in = round(money_in, 2)
            year.savings_money_out = round(money_out, 2)
            year.savings_closing = round(closing, 2)

            savings = closing

        return timeline
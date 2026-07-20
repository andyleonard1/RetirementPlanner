"""
Withdrawal Engine

Determines where retirement income is sourced from.
"""


class WithdrawalEngine:

    def __init__(self, assumptions):
        self.assumptions = assumptions

    def apply(self, timeline):

    

        for year in timeline:

            

            year.pension_withdrawal = year.pension_needed
            

        return timeline
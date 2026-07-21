"""
Withdrawal Engine

Executes the withdrawal decision made by StrategyEngine.
"""


class WithdrawalEngine:

    def __init__(self, assumptions):
        self.assumptions = assumptions

    def apply(self, timeline):

        for year in timeline:

            #
            # TaxEngine will later convert this net amount
            # into a gross pension withdrawal.
            #
            year.pension_withdrawal = year.pension_needed
            return timeline
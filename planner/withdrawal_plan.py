"""
Withdrawal Plan

Represents the recommended withdrawals
for a single retirement year.
"""


class WithdrawalPlan:

    def __init__(self):

        self.pension = 0.0
        self.isa = 0.0
        self.savings = 0.0
        self.cash_interest = 0.0

    @property
    def total(self):

        return (
            self.pension
            + self.isa
            + self.savings
            + self.cash_interest
        )
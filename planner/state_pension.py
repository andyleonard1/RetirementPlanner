"""
State Pension Engine

Calculates State Pension for both spouses and updates the
RetirementYear objects created by the TimelineEngine.
"""


class StatePensionEngine:

    def __init__(self, assumptions):

        self.assumptions = assumptions

        self.full_pension = assumptions.get("state_pension_full")
        self.growth = assumptions.get("state_pension_growth")

    def apply(self, timeline):

        for year in timeline:

            age = year.age

            years_since_67 = max(0, age - 67)
            years_since_69 = max(0, age - 69)

            your_pension = 0
            spouse_pension = 0

            if age >= 67:
                your_pension = (
                    self.full_pension
                    * ((1 + self.growth) ** years_since_67)
                )

            if age >= 69:
                spouse_start = (
                    self.full_pension
                    * ((1 + self.growth) ** 2)
                )

                spouse_pension = (
                    spouse_start
                    * ((1 + self.growth) ** years_since_69)
                )

            year.your_state_pension = round(your_pension, 2)
            year.spouse_state_pension = round(spouse_pension, 2)

        return timeline
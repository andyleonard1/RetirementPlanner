class StatePensionEngine:
    """
    Projects State Pension for both spouses.
    """

    def __init__(self, assumptions):
        self.assumptions = assumptions

        # These will come from assumptions.json later
        self.full_pension = assumptions.get("state_pension_full")
        self.growth = assumptions.get("state_pension_growth")

    def project(self):

        start_age = self.assumptions.get("retirement_age")
        end_age = self.assumptions.get("projection_end_age")

        projection = []

        for age in range(start_age, end_age + 1):

            years_since_67 = max(0, age - 67)
            years_since_69 = max(0, age - 69)

            your_pension = 0
            spouse_pension = 0

            if age >= 67:
                your_pension = self.full_pension * ((1 + self.growth) ** years_since_67)

            if age >= 69:
                spouse_start = self.full_pension * ((1 + self.growth) ** 2)
                spouse_pension = spouse_start * ((1 + self.growth) ** years_since_69)

            projection.append({
                "age": age,
                "your_pension": round(your_pension, 2),
                "spouse_pension": round(spouse_pension, 2)
            })

        return projection
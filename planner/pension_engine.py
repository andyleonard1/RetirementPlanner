from dataclasses import dataclass


@dataclass
class PensionYear:
    age: int
    opening: float
    growth: float
    withdrawal: float
    closing: float
    annual_change: float
    growth_rate: float


class PensionEngine:
    """
    Calculates the pension fund value for each year of retirement.
    """

    def __init__(self, assumptions):

        self.assumptions = assumptions

        self.starting_pension = assumptions.get("starting_pension")
        self.growth_rate = assumptions.get("pension_growth")

    def project(self):

        projection = []

        pension = self.starting_pension

        for age in range(
            self.assumptions.get("retirement_age"),
            self.assumptions.get("projection_end_age") + 1,
        ):

            opening = pension

            growth = opening * self.growth_rate

            withdrawal = self.assumptions.get("target_net_income")

            closing = opening + growth - withdrawal

            annual_change = closing - opening

            growth_rate = self.growth_rate * 100

            projection.append(
                PensionYear(
                    age,
                    round(opening, 2),
                    round(growth, 2),
                    round(withdrawal, 2),
                    round(closing, 2),
                    round(annual_change, 2),
                    round(growth_rate, 2),
                )
            )

            pension = closing

        return projection
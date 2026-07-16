from dataclasses import dataclass


@dataclass
class PensionYear:
    age: int
    opening: float
    growth: float
    withdrawal: float
    closing: float


class PensionEngine:

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

            projection.append(
                PensionYear(
                    age,
                    round(opening, 2),
                    round(growth, 2),
                    round(withdrawal, 2),
                    round(closing, 2),
                )
            )

            pension = closing

        return projection
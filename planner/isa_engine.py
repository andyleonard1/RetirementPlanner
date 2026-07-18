"""
ISA Engine

Projects ISA balances by transferring money from savings.
"""


class ISAEngine:

    def __init__(self, assumptions):

        self.assumptions = assumptions

        self.starting_isa = assumptions.get("starting_isa")
        self.growth_rate = assumptions.get("isa_growth_rate")
        self.allowance = assumptions.get("annual_isa_allowance")

    def apply(self, timeline):

        isa = self.starting_isa

        for year in timeline:

            opening = isa

            growth = opening * self.growth_rate

            available = year.savings_closing

            transfer = min(self.allowance, available)

            year.savings_money_out = transfer
            year.savings_closing -= transfer

            closing = opening + growth + transfer

            year.isa_opening = round(opening, 2)
            year.isa_growth = round(growth, 2)
            year.isa_money_in = round(transfer, 2)
            year.isa_closing = round(closing, 2)

            isa = closing
        year.total_assets = round(
    year.closing_pension
    + year.savings_closing
    + year.isa_closing,
    2,
)
        return timeline
   
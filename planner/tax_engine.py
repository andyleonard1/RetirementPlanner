"""
Tax Engine

Calculates the gross pension withdrawal required to
provide the desired net pension income after income tax.

Version 2
---------
This version taxes total taxable income:

    Gross Pension Withdrawal
  + State Pension
  - Personal Allowance

For now it assumes:
    • England tax bands
    • Basic rate only (20%)
    • No tax-free cash (PCLS) yet
"""

class TaxEngine:

    def __init__(self, assumptions):
        self.assumptions = assumptions

    def apply(self, timeline):

        allowance = self.assumptions.get("personal_allowance")
        basic_limit = self.assumptions.get("basic_rate_limit")
        basic_rate = self.assumptions.get("basic_rate")
        higher_rate = self.assumptions.get("higher_rate")
        additional_rate = self.assumptions.get("additional_rate")

        for year in timeline:

            #
            # Net pension income required from WithdrawalEngine
            #
            required_net = year.income_shortfall

            #
            # First estimate
            #
            gross = required_net

            #
            # Iterate until gross and tax stabilise
            #
            for _ in range(10):

                total_income = (
                    gross
                    + year.your_state_pension
                )

                taxable = max(0.0, total_income - allowance)

                #
                # Income Tax
                #
                if taxable <= (basic_limit - allowance):

                    tax = taxable * basic_rate

                else:

                    basic_band = basic_limit - allowance

                    higher_band = taxable - basic_band

                    tax = (
                        basic_band * basic_rate
                        + higher_band * higher_rate
                    )

                new_gross = required_net + tax

                #
                # Stop when converged
                #
                if abs(new_gross - gross) < 0.01:
                    gross = new_gross
                    break

                gross = new_gross

            #
            # Store results
            #
            year.gross_pension_income = round(gross, 2)
            year.taxable_pension_income = round(taxable, 2)
            year.income_tax = round(tax, 2)
            year.net_pension_income = round(required_net, 2)

            #
            # PensionEngine will deduct this amount
            #
            year.pension_withdrawal = round(gross, 2)

        return timeline
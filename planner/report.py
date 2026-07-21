"""
Console Report

Displays the retirement timeline in a simple table.
"""


class ConsoleReport:

    def print(self, timeline, summary):

        print()

        print(
            f"{'Age':<5}"
            f"{'Year':>8}"
            f"{'Pension':>15}"
            f"{'Gross WD':>15}"
            f"{'Tax':>12}"
            f"{'Net WD':>15}"
            f"{'Savings':>15}"
            f"{'ISA':>15}"
            f"{'Cash':>12}"
            f"{'Your SP':>12}"
            f"{'Spouse SP':>12}"
        )

        print("-" * 136)

        for year in timeline:

            print(
                f"{year.age:<5}"
                f"{year.calendar_year:>8}"
                f"{year.closing_pension:>15,.0f}"
                f"{year.gross_pension_income:>15,.0f}"
                f"{year.income_tax:>12,.0f}"
                f"{year.net_pension_income:>15,.0f}"
                f"{year.savings_closing:>15,.0f}"
                f"{year.isa_closing:>15,.0f}"
                f"{year.cash_available:>12,.0f}"
                f"{year.your_state_pension:>12,.0f}"
                f"{year.spouse_state_pension:>12,.0f}"
            )

        print()
        print("=" * 70)
        print("RETIREMENT SUMMARY")
        print("=" * 70)

        print(f"Ending Pension      £{summary['ending_pension']:,.0f}")
        print(f"Ending Savings      £{summary['ending_savings']:,.0f}")
        print(f"Ending ISA          £{summary['ending_isa']:,.0f}")
        print(f"Total Assets        £{summary['ending_assets']:,.0f}")

        print()

        print(f"Gross Pension Drawn £{summary['gross_pension']:,.0f}")
        print(f"Net Pension Income  £{summary['net_pension']:,.0f}")
        print(f"State Pension       £{summary['state_pension']:,.0f}")
        print(f"Income Tax Paid     £{summary['total_tax']:,.0f}")
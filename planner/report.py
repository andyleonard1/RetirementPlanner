"""
Console Report

Displays the retirement timeline in a simple table.
"""


class ConsoleReport:

    def print(self, timeline):

        print()

        print(
            f"{'Age':<5}"
            f"{'Year':>8}"
            f"{'Pension':>15}"
            f"{'Your SP':>15}"
            f"{'Spouse SP':>15}"
        )

        print("-" * 70)

        for year in timeline:

            print(
                f"{year.age:<5}"
                f"{year.calendar_year:>8}"
                f"{year.closing_pension:>15,.0f}"
                f"{year.your_state_pension:>15,.0f}"
                f"{year.spouse_state_pension:>15,.0f}"
            )
"""
Console Report

Displays the retirement timeline in a simple table.
"""


class ConsoleReport:

    def print(
        self,
        timeline,
        summary,
        decision=None,
        age_comparison=None,
    ):
        print()
        print(
            f"Withdrawal Strategy : "
            f"{summary['strategy']}"
        )
        print()
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

        print(
            f"Ending Pension      "
            f"£{summary['ending_pension']:,.0f}"
        )

        print(
            f"Ending Savings      "
            f"£{summary['ending_savings']:,.0f}"
        )

        print(
            f"Ending ISA          "
            f"£{summary['ending_isa']:,.0f}"
        )

        print(
            f"Total Assets        "
            f"£{summary['ending_assets']:,.0f}"
        )

        print()

        print(
            f"Gross Pension Drawn "
            f"£{summary['gross_pension']:,.0f}"
        )

        print(
            f"Net Pension Income  "
            f"£{summary['net_pension']:,.0f}"
        )

        print(
            f"State Pension       "
            f"£{summary['state_pension']:,.0f}"
        )

        print(
            f"Income Tax Paid     "
            f"£{summary['total_tax']:,.0f}"
        )

        # -------------------------------------------------
        # RETIREMENT AGE COMPARISON
        # -------------------------------------------------

        if age_comparison is not None:

            print()
            print("=" * 70)
            print("RETIREMENT AGE COMPARISON")
            print("=" * 70)

            print(
                f"{'Age':<8}"
                f"{'Status':<14}"
                f"{'Ending Assets':>18}"
                f"{'Change':>18}"
            )

            print("-" * 58)

            for comparison in age_comparison:

                status = (
                    "SUCCESS"
                    if comparison.success
                    else "NOT SUSTAINABLE"
                )

                change = comparison.change_from_previous_age

                change_text = (
                    "-"
                    if change is None
                    else f"£{change:,.0f}"
                )

                print(
                    f"{comparison.retirement_age:<8}"
                    f"{status:<14}"
                    f"£{comparison.ending_assets:>17,.0f}"
                    f"{change_text:>18}"
                )

        # -------------------------------------------------
        # RETIREMENT DECISION
        # -------------------------------------------------

        if decision is not None:

            print()
            print("=" * 70)
            print("RETIREMENT DECISION")
            print("=" * 70)

            print(
                f"Recommended Age    "
                f"{decision.recommended_age}"
            )

            print(
                f"Ending Pension     "
                f"£{decision.ending_pension:,.0f}"
            )

            print(
                f"Ending Savings     "
                f"£{decision.ending_savings:,.0f}"
            )

            print(
                f"Ending ISA         "
                f"£{decision.ending_isa:,.0f}"
            )

            print(
                f"Ending Assets      "
                f"£{decision.ending_assets:,.0f}"
            )

            if decision.later_age is not None:

                print()
                print(
                    f"If retiring at "
                    f"{decision.later_age}:"
                )

                if (
                    decision.later_ending_assets
                    is not None
                ):
                    print(
                        f"Ending Assets      "
                        f"£{decision.later_ending_assets:,.0f}"
                    )

                if (
                    decision.additional_assets_from_waiting
                    is not None
                ):
                    print(
                        f"Additional Assets  "
                        f"£{decision.additional_assets_from_waiting:,.0f}"
                    )
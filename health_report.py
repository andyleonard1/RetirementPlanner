"""
Health Report

Prints an executive retirement health dashboard.
"""

from planner.version import VERSION


class HealthReport:

    def print(
        self,
        health,
        recommendation,
        monte_carlo,
        summary,
    ):

        print()

        print("=" * 60)
        print("RETIREMENT HEALTH DASHBOARD")
        print("=" * 60)

        print()

        print(f"Version                  {VERSION}")

        print()

        print(
            f"Overall Score            {health['score']:.1f} / 10"
        )

        print(
            f"Rating                   {health['rating']}"
        )

        print()

        print(
            f"Success Probability      {monte_carlo.success_rate:.1f}%"
        )

        print(
            f"Recommended Strategy     {recommendation['strategy']}"
        )

        print(
            f"Confidence               {recommendation['confidence']}"
        )

        print()

        print(
            f"Projected Estate         £{summary['ending_assets']:,.0f}"
        )

        print(
            f"Projected Pension        £{summary['ending_pension']:,.0f}"
        )

        print(
            f"Projected ISA            £{summary['ending_isa']:,.0f}"
        )

        print(
            f"Projected Savings        £{summary['ending_savings']:,.0f}"
        )

        print()

        print(
            f"Lifetime Tax             £{summary['total_tax']:,.0f}"
        )

        print()

        print("Key Strengths")

        print("-------------")

        for reason in health["reasons"]:

            print(f"[OK] {reason}")

        print()

        print("=" * 60)

        print()
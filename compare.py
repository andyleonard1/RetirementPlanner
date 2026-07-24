"""
Compare retirement strategies.
"""

from planner.scenario_engine import ScenarioEngine


def main():

    engine = ScenarioEngine()

    results = engine.compare_strategies()

    print()
    print("=" * 80)
    print("RETIREMENT STRATEGY COMPARISON")
    print("=" * 80)

    print(
        f"{'Strategy':<18}"
        f"{'Assets':>15}"
        f"{'Pension':>15}"
        f"{'ISA':>15}"
        f"{'Tax':>15}"
    )

    print("-" * 80)

    for result in results:

        summary = result["summary"]

        print(
            f"{result['name']:<18}"
            f"£{summary['ending_assets']:>14,.0f}"
            f"£{summary['ending_pension']:>14,.0f}"
            f"£{summary['ending_isa']:>14,.0f}"
            f"£{summary['total_tax']:>14,.0f}"
        )

    print("-" * 80)

    winner = max(
        results,
        key=lambda r: r["summary"]["ending_assets"]
    )

    lowest_tax = min(
        results,
        key=lambda r: r["summary"]["total_tax"]
    )

    print()
    print(f"Best Estate : {winner['name']}")
    print(f"Lowest Tax  : {lowest_tax['name']}")

    print("=" * 80)


if __name__ == "__main__":
    main()
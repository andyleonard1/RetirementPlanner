"""
Comparison report.
"""

from reports.report_utils import (
    heading,
    currency,
)


class ComparisonReport:

    def print(self, results):

        heading("RETIREMENT STRATEGY COMPARISON")

        print(
            f"{'Strategy':<18}"
            f"{'Assets':>15}"
            f"{'Pension':>15}"
            f"{'ISA':>15}"
            f"{'Tax':>15}"
        )

        print("-" * 78)

        for result in results:

            s = result["summary"]

            print(
                f"{result['name']:<18}"
                f"{currency(s['ending_assets']):>15}"
                f"{currency(s['ending_pension']):>15}"
                f"{currency(s['ending_isa']):>15}"
                f"{currency(s['total_tax']):>15}"
            )

        print()
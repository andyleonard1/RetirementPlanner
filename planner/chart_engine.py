"""
Chart Engine

Generates charts for retirement reports.
"""

from pathlib import Path

import matplotlib.pyplot as plt


class ChartEngine:

    def __init__(self, output_folder="charts"):

        self.output = Path(output_folder)

        self.output.mkdir(exist_ok=True)

    def create_all(self, timeline):

        self.pension_chart(timeline)

        self.asset_chart(timeline)

    def pension_chart(self, timeline):

        ages = [y.age for y in timeline]

        pension = [y.closing_pension for y in timeline]

        plt.figure(figsize=(8,4))

        plt.plot(ages, pension)

        plt.title("Pension Value")

        plt.xlabel("Age")

        plt.ylabel("£")

        plt.grid(True)

        plt.tight_layout()

        plt.savefig(self.output / "pension.png")

        plt.close()

    def asset_chart(self, timeline):

        ages = [y.age for y in timeline]

        assets = [

            y.closing_pension

            + y.isa_remaining

            + y.savings_remaining

            for y in timeline

        ]

        plt.figure(figsize=(8,4))

        plt.plot(ages, assets)

        plt.title("Total Assets")

        plt.xlabel("Age")

        plt.ylabel("£")

        plt.grid(True)

        plt.tight_layout()

        plt.savefig(self.output / "assets.png")

        plt.close()
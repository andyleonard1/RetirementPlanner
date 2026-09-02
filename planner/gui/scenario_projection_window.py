"""Tkinter presentation for the scenario projection view model.

The GUI is deliberately kept outside the financial/domain layers.  It consumes
``ScenarioProjectionViewModel`` only and performs no financial calculations.
"""
from __future__ import annotations

from typing import Any

from planner.projection.scenario_projection_view_model import ScenarioProjectionViewModel


def format_currency(value: float) -> str:
    """Format a monetary value for display without changing its value."""
    return f"£{value:,.0f}"


def format_percent(value: float) -> str:
    """Format a decimal return as a percentage for display."""
    return f"{value:.1%}"


class ScenarioProjectionWindow:
    """Small desktop window for comparing retirement projection scenarios.

    Tkinter is imported lazily so the core planner remains usable on systems
    without a graphical environment.  ``view_model`` is the only financial
    input; this class does not recalculate projection results.
    """

    def __init__(self, view_model: ScenarioProjectionViewModel, root: Any | None = None):
        if not isinstance(view_model, ScenarioProjectionViewModel):
            raise TypeError("view_model must be ScenarioProjectionViewModel")

        self.view_model = view_model
        self._root = root
        self._owns_root = root is None
        self._cards_frame = None
        self._table = None

    def build(self) -> Any:
        """Build and return the Tk root without entering the event loop."""
        import tkinter as tk
        from tkinter import ttk

        if self._root is None:
            self._root = tk.Tk()
        self._root.title("Retirement Scenario Comparison")
        self._root.geometry("920x620")

        container = ttk.Frame(self._root, padding=16)
        container.pack(fill="both", expand=True)

        ttk.Label(
            container,
            text="Retirement scenario comparison",
            font=("TkDefaultFont", 16, "bold"),
        ).pack(anchor="w", pady=(0, 12))

        self._cards_frame = ttk.Frame(container)
        self._cards_frame.pack(fill="x", pady=(0, 16))
        for card in self.view_model.scenario_cards:
            card_frame = ttk.LabelFrame(self._cards_frame, text=card.name, padding=10)
            card_frame.pack(side="left", fill="both", expand=True, padx=4)
            ttk.Label(card_frame, text=f"Return: {format_percent(card.annual_return)}").pack(anchor="w")
            ttk.Label(card_frame, text=f"Ending pension: {format_currency(card.ending_balance)}").pack(anchor="w")
            ttk.Label(card_frame, text=f"Source: {card.source}").pack(anchor="w")

        summary = ttk.Frame(container)
        summary.pack(fill="x", pady=(0, 12))
        ttk.Label(summary, text=f"Lowest: {format_currency(self.view_model.lowest_ending_balance)}").pack(side="left", padx=4)
        ttk.Label(summary, text=f"Highest: {format_currency(self.view_model.highest_ending_balance)}").pack(side="left", padx=12)
        ttk.Label(summary, text=f"Spread: {format_currency(self.view_model.ending_balance_spread)}").pack(side="left", padx=12)

        columns = ("scenario", "year", "starting", "growth", "withdrawals", "ending")
        self._table = ttk.Treeview(container, columns=columns, show="headings", height=18)
        headings = {
            "scenario": "Scenario",
            "year": "Year",
            "starting": "Starting pension",
            "growth": "Investment growth",
            "withdrawals": "Withdrawals",
            "ending": "Ending pension",
        }
        for column in columns:
            self._table.heading(column, text=headings[column])
        for row in self.view_model.year_rows:
            self._table.insert(
                "",
                "end",
                values=(
                    row.scenario,
                    row.year,
                    format_currency(row.starting_balance),
                    format_currency(row.investment_growth),
                    format_currency(row.withdrawals),
                    format_currency(row.ending_balance),
                ),
            )
        self._table.pack(fill="both", expand=True)
        return self._root

    def run(self) -> None:
        """Build the window and, when owned, enter the Tk event loop."""
        root = self.build()
        if self._owns_root:
            root.mainloop()

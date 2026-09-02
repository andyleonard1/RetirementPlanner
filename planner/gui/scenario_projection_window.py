"""Tkinter presentation for the scenario projection view model and inputs."""
from __future__ import annotations

from typing import Any, Mapping, Sequence

from planner.gui.scenario_projection_application import (
    ScenarioProjectionApplication,
    ScenarioProjectionInputs,
)
from planner.projection.scenario_projection_view_model import ScenarioProjectionViewModel


SUPPORTED_SCENARIOS = ("conservative", "central", "optimistic")


def format_currency(value: float) -> str:
    """Format a monetary value for display without changing its value."""
    return f"£{value:,.0f}"


def format_percent(value: float) -> str:
    """Format a decimal return as a percentage for display."""
    return f"{value:.1%}"


class ScenarioProjectionWindow:
    """Desktop window for editing projection inputs and refreshing results.

    The window owns presentation/event handling only. All financial calculations
    remain behind ``ScenarioProjectionApplication`` and its existing domain
    calculation boundaries.
    """

    def __init__(
        self,
        view_model: ScenarioProjectionViewModel,
        root: Any | None = None,
        *,
        application: ScenarioProjectionApplication | None = None,
        allocations: Mapping[str, float] | None = None,
        fund_returns: Mapping[str, Sequence[float]] | None = None,
    ):
        if not isinstance(view_model, ScenarioProjectionViewModel):
            raise TypeError("view_model must be ScenarioProjectionViewModel")
        if application is not None and not isinstance(application, ScenarioProjectionApplication):
            raise TypeError("application must be ScenarioProjectionApplication")
        if application is not None and (allocations is None or fund_returns is None):
            raise ValueError("allocations and fund_returns are required with application")

        self.view_model = view_model
        self.application = application
        self.allocations = dict(allocations or {})
        self.fund_returns = {name: tuple(values) for name, values in (fund_returns or {}).items()}
        self._root = root
        self._owns_root = root is None
        self._cards_frame = None
        self._table = None
        self._content = None
        self._pension_var = None
        self._retirement_age_var = None
        self._end_age_var = None
        self._scenario_vars: dict[str, Any] = {}

    @staticmethod
    def parse_inputs(
        starting_pension: str,
        retirement_age: str,
        projection_end_age: str,
        selected_scenarios: Sequence[str],
    ) -> ScenarioProjectionInputs:
        """Parse GUI strings into the validated immutable input contract."""
        try:
            pension = float(starting_pension.replace(",", "").replace("£", "").strip())
            retirement = int(retirement_age.strip())
            end_age = int(projection_end_age.strip())
        except (AttributeError, ValueError) as exc:
            raise ValueError("pension and ages must be valid numeric values") from exc

        scenarios = tuple(str(name).strip().lower() for name in selected_scenarios if str(name).strip())
        invalid = tuple(name for name in scenarios if name not in SUPPORTED_SCENARIOS)
        if invalid:
            raise ValueError(f"unsupported scenario(s): {', '.join(invalid)}")
        return ScenarioProjectionInputs(pension, retirement, end_age, scenarios)

    def _current_input_strings(self) -> tuple[str, str, str, tuple[str, ...]]:
        if self._pension_var is None:
            inputs = self.application.inputs() if self.application else None
            if inputs is None:
                raise RuntimeError("editable inputs require an application")
            return (
                str(inputs.starting_pension),
                str(inputs.retirement_age),
                str(inputs.projection_end_age),
                inputs.scenarios,
            )
        selected = tuple(name for name, var in self._scenario_vars.items() if bool(var.get()))
        return (
            self._pension_var.get(),
            self._retirement_age_var.get(),
            self._end_age_var.get(),
            selected,
        )

    def _run_projection(self) -> None:
        """Validate inputs, apply them in memory, rebuild the view model and refresh."""
        import tkinter.messagebox as messagebox

        if self.application is None:
            return
        try:
            inputs = self.parse_inputs(*self._current_input_strings())
            self.application.apply_inputs(inputs)
            self.view_model = self.application.build_view_model(
                allocations=self.allocations,
                fund_returns=self.fund_returns,
                scenarios=inputs.scenarios,
            )
            self._refresh_results()
        except (ValueError, TypeError) as exc:
            messagebox.showerror("Invalid projection inputs", str(exc), parent=self._root)

    def _save_assumptions(self) -> None:
        """Persist the current validated assumptions only after an explicit click."""
        import tkinter.messagebox as messagebox

        if self.application is None:
            return
        try:
            self.application.assumptions.save()
        except (ValueError, OSError) as exc:
            messagebox.showerror("Could not save assumptions", str(exc), parent=self._root)
            return
        messagebox.showinfo("Assumptions saved", "Validated assumptions were saved.", parent=self._root)

    def build(self) -> Any:
        """Build and return the Tk root without entering the event loop."""
        import tkinter as tk
        from tkinter import ttk

        if self._root is None:
            self._root = tk.Tk()
        self._root.title("Retirement Scenario Comparison")
        self._root.geometry("980x720")

        container = ttk.Frame(self._root, padding=16)
        container.pack(fill="both", expand=True)

        ttk.Label(
            container,
            text="Retirement scenario comparison",
            font=("TkDefaultFont", 16, "bold"),
        ).pack(anchor="w", pady=(0, 12))

        if self.application is not None:
            self._build_input_controls(container, ttk)

        self._content = ttk.Frame(container)
        self._content.pack(fill="both", expand=True)
        self._render_results(ttk)
        return self._root

    def _build_input_controls(self, container: Any, ttk: Any) -> None:
        import tkinter as tk

        inputs = self.application.inputs()
        controls = ttk.LabelFrame(container, text="Projection inputs", padding=10)
        controls.pack(fill="x", pady=(0, 12))

        self._pension_var = tk.StringVar(value=str(inputs.starting_pension))
        self._retirement_age_var = tk.StringVar(value=str(inputs.retirement_age))
        self._end_age_var = tk.StringVar(value=str(inputs.projection_end_age))

        fields = (
            ("Starting pension (£)", self._pension_var),
            ("Retirement age", self._retirement_age_var),
            ("Projection end age", self._end_age_var),
        )
        for column, (label, variable) in enumerate(fields):
            ttk.Label(controls, text=label).grid(row=0, column=column, padx=5, sticky="w")
            ttk.Entry(controls, textvariable=variable, width=18).grid(row=1, column=column, padx=5, sticky="ew")

        scenario_frame = ttk.Frame(controls)
        scenario_frame.grid(row=2, column=0, columnspan=3, sticky="w", pady=(8, 0))
        ttk.Label(scenario_frame, text="Scenarios:").pack(side="left", padx=(0, 8))
        for name in SUPPORTED_SCENARIOS:
            variable = tk.BooleanVar(value=name in inputs.scenarios)
            self._scenario_vars[name] = variable
            ttk.Checkbutton(scenario_frame, text=name.title(), variable=variable).pack(side="left", padx=4)

        buttons = ttk.Frame(controls)
        buttons.grid(row=3, column=0, columnspan=3, sticky="w", pady=(10, 0))
        ttk.Button(buttons, text="Run projection", command=self._run_projection).pack(side="left", padx=(0, 6))
        ttk.Button(buttons, text="Save assumptions", command=self._save_assumptions).pack(side="left")

    def _render_results(self, ttk: Any) -> None:
        for child in self._content.winfo_children():
            child.destroy()
        self._cards_frame = None
        self._table = None

        self._cards_frame = ttk.Frame(self._content)
        self._cards_frame.pack(fill="x", pady=(0, 16))
        for card in self.view_model.scenario_cards:
            card_frame = ttk.LabelFrame(self._cards_frame, text=card.name, padding=10)
            card_frame.pack(side="left", fill="both", expand=True, padx=4)
            ttk.Label(card_frame, text=f"Return: {format_percent(card.annual_return)}").pack(anchor="w")
            ttk.Label(card_frame, text=f"Ending pension: {format_currency(card.ending_balance)}").pack(anchor="w")
            ttk.Label(card_frame, text=f"Source: {card.source}").pack(anchor="w")

        summary = ttk.Frame(self._content)
        summary.pack(fill="x", pady=(0, 12))
        ttk.Label(summary, text=f"Lowest: {format_currency(self.view_model.lowest_ending_balance)}").pack(side="left", padx=4)
        ttk.Label(summary, text=f"Highest: {format_currency(self.view_model.highest_ending_balance)}").pack(side="left", padx=12)
        ttk.Label(summary, text=f"Spread: {format_currency(self.view_model.ending_balance_spread)}").pack(side="left", padx=12)

        columns = ("scenario", "year", "starting", "growth", "withdrawals", "ending")
        self._table = ttk.Treeview(self._content, columns=columns, show="headings", height=18)
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

    def _refresh_results(self) -> None:
        import tkinter.ttk as ttk

        if self._content is not None:
            self._render_results(ttk)

    def run(self) -> None:
        """Build the window and, when owned, enter the Tk event loop."""
        root = self.build()
        if self._owns_root:
            root.mainloop()

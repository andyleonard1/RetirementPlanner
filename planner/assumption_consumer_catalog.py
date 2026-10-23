"""Explicit consumer boundaries for the public assumptions document.

This module is metadata only.  It does not resolve, mutate, or calculate any
assumption.  Its purpose is to make the hand-off from the public assumptions
contract to the relevant application boundary explicit and testable.
"""
from __future__ import annotations

from planner.assumption_usage_catalog import ROLES

CONSUMERS = {
    "projection": (
        "planner.planner",
        "planner.inflation_engine",
        "planner.state_pension",
        "planner.property_sale_engine",
        "planner.savings_engine",
        "planner.isa_engine",
        "planner.cashflow_engine",
        "planner.withdrawal_engine",
        "planner.tax_engine",
        "planner.pension_engine",
        "planner.validation_engine",
        "planner.timeline",
        "planner.strategy_engine",
        "planner.investment_return",
    ),
    "monte_carlo": (
        "planner.monte_carlo_engine",
        "planner.simulation.monte_carlo",
        "planner.validation_engine",
    ),
    "legacy_compatibility": (
        "planner.assumption_resolver",
    ),
    "auxiliary": (
        "planner.simulation.tax_free_cash",
        "planner.recommendations.sensitivity_runner",
    ),
    "goals": (
        "planner.goal_engine",
        "reports.goal_report",
        "reports.goal_pdf_report",
    ),
}


def consumer_modules(path: str) -> tuple[str, ...]:
    """Return the explicit application boundary for an assumption path."""
    role = "goals" if path.startswith("goals[") else ROLES[path]
    return CONSUMERS[role]


def unclassified_consumer_roles() -> tuple[str, ...]:
    """Return operational roles without an explicit consumer boundary."""
    roles = set(ROLES.values())
    return tuple(sorted(roles - set(CONSUMERS)))

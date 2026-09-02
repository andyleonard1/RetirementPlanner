"""
Typed engine contracts.

These protocols define the stable interfaces shared by the retirement
planner engines. They are deliberately structural: existing engine classes
do not need to inherit from a common base class to satisfy a contract.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Protocol, TypeAlias, runtime_checkable

from planner.models import RetirementYear

Timeline: TypeAlias = list[RetirementYear]


@runtime_checkable
class AssumptionsProvider(Protocol):
    """Read-only interface required by planning engines."""

    def get(self, key: str, default: Any = None) -> Any:
        ...


@runtime_checkable
class TimelineBuilderProtocol(Protocol):
    """Builds the initial retirement timeline."""

    def build(self) -> Timeline:
        ...


@runtime_checkable
class TimelineTransformerProtocol(Protocol):
    """Reads and/or mutates a retirement timeline."""

    def apply(self, timeline: Timeline) -> Timeline:
        ...


@runtime_checkable
class SummaryEngineProtocol(Protocol):
    """Produces summary statistics from a completed timeline."""

    def apply(self, timeline: Sequence[RetirementYear]) -> dict[str, Any]:
        ...


@runtime_checkable
class ValidatorProtocol(Protocol):
    """Validates planner configuration before calculation."""

    def validate(self) -> None:
        ...

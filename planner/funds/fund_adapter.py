"""Provider-neutral fund source adapter boundary for RC4 Sprint 73."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Iterable

from .fund_import import ImportedFundReturn


@dataclass(frozen=True)
class FundSourceMetadata:
    source_name: str
    source_version: str | None = None


class FundDataAdapter(ABC):
    """Interface implemented by external fund-data sources."""

    @property
    @abstractmethod
    def metadata(self) -> FundSourceMetadata:
        raise NotImplementedError

    @abstractmethod
    def returns(self) -> Iterable[ImportedFundReturn]:
        raise NotImplementedError


class InMemoryFundDataAdapter(FundDataAdapter):
    """Simple adapter used by tests and future manual/import workflows."""

    def __init__(
        self,
        records: Iterable[ImportedFundReturn],
        source_name: str = "manual",
        source_version: str | None = None,
    ):
        self._records = tuple(records)
        self._metadata = FundSourceMetadata(source_name, source_version)

    @property
    def metadata(self) -> FundSourceMetadata:
        return self._metadata

    def returns(self) -> tuple[ImportedFundReturn, ...]:
        return self._records

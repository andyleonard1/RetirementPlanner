"""Structured historical fund-return observations for RC4 Sprint 86."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping


@dataclass(frozen=True)
class HistoricalFundReturn:
    fund_identifier: str
    year: int
    return_rate: float
    source: str
    data_type: str = "actual"

    def validate(self) -> None:
        if not self.fund_identifier.strip():
            raise ValueError("fund_identifier is required")
        if self.year < 1900:
            raise ValueError("year must be 1900 or later")
        if not self.source.strip():
            raise ValueError("source is required")
        if self.data_type not in {"actual", "estimated"}:
            raise ValueError("data_type must be 'actual' or 'estimated'")


class HistoricalFundReturnStore:
    """Store annual observations with provenance and duplicate protection."""

    def __init__(self, returns: Iterable[HistoricalFundReturn] = ()):
        self._returns: dict[tuple[str, int], HistoricalFundReturn] = {}
        for item in returns:
            self.add(item)

    def add(self, item: HistoricalFundReturn) -> None:
        item.validate()
        key = (item.fund_identifier, item.year)
        if key in self._returns:
            raise ValueError(
                f"duplicate historical return: {item.fund_identifier} {item.year}"
            )
        self._returns[key] = item

    def for_fund(self, fund_identifier: str) -> tuple[HistoricalFundReturn, ...]:
        return tuple(
            sorted(
                (
                    item
                    for item in self._returns.values()
                    if item.fund_identifier == fund_identifier
                ),
                key=lambda item: item.year,
            )
        )

    def all(self) -> tuple[HistoricalFundReturn, ...]:
        return tuple(
            sorted(
                self._returns.values(),
                key=lambda item: (item.fund_identifier, item.year),
            )
        )

    def actual_for_fund(self, fund_identifier: str) -> tuple[HistoricalFundReturn, ...]:
        return tuple(
            item for item in self.for_fund(fund_identifier)
            if item.data_type == "actual"
        )

    def estimated_for_fund(
        self, fund_identifier: str
    ) -> tuple[HistoricalFundReturn, ...]:
        return tuple(
            item for item in self.for_fund(fund_identifier)
            if item.data_type == "estimated"
        )


class HistoricalFundReturnImporter:
    """Import provider-neutral historical-return records."""

    REQUIRED_FIELDS = {"fund_identifier", "year", "return_rate", "source"}

    def import_records(
        self, records: Iterable[Mapping[str, object]]
    ) -> tuple[HistoricalFundReturn, ...]:
        imported = []
        for record in records:
            missing = self.REQUIRED_FIELDS.difference(record)
            if missing:
                raise ValueError(
                    "missing historical return fields: "
                    + ", ".join(sorted(missing))
                )
            try:
                item = HistoricalFundReturn(
                    fund_identifier=str(record["fund_identifier"]).strip(),
                    year=int(record["year"]),
                    return_rate=float(record["return_rate"]),
                    source=str(record["source"]).strip(),
                    data_type=str(record.get("data_type", "actual")).strip().lower(),
                )
            except (TypeError, ValueError) as exc:
                raise ValueError("invalid historical fund return record") from exc
            item.validate()
            imported.append(item)
        return tuple(imported)

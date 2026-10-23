"""Provider-neutral fund data import layer."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping


@dataclass(frozen=True)
class ImportedFundReturn:
    fund_identifier: str
    year: int
    return_rate: float


class FundDataImporter:
    REQUIRED_FIELDS = {"fund_identifier", "year", "return_rate"}

    def import_records(self, records: Iterable[Mapping[str, object]]) -> tuple[ImportedFundReturn, ...]:
        imported = []
        for record in records:
            missing = self.REQUIRED_FIELDS.difference(record)
            if missing:
                raise ValueError("missing fund data fields: " + ", ".join(sorted(missing)))
            try:
                identifier = str(record["fund_identifier"]).strip()
                year = int(record["year"])
                return_rate = float(record["return_rate"])
            except (TypeError, ValueError) as exc:
                raise ValueError("invalid fund return record") from exc
            if not identifier:
                raise ValueError("fund_identifier is required")
            if year < 1900:
                raise ValueError("year must be 1900 or later")
            imported.append(ImportedFundReturn(identifier, year, return_rate))
        return tuple(imported)

    def import_csv(self, path: str | Path) -> tuple[ImportedFundReturn, ...]:
        import csv
        with Path(path).open("r", newline="", encoding="utf-8") as handle:
            return self.import_records(csv.DictReader(handle))

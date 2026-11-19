"""Shared cooperative cancellation signal for report export workflows."""
from __future__ import annotations

from threading import Event


class ReportExportCancelled(Exception):
    """Raised when a cooperative report-export cancellation is observed."""


def raise_if_cancelled(cancellation_event: Event | None, message: str) -> None:
    """Stop at a safe boundary; never forcibly interrupt an active PDF renderer."""
    if cancellation_event is not None and cancellation_event.is_set():
        raise ReportExportCancelled(message)

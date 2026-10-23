"""Small injectable GUI seams used to keep desktop event handling headless-testable."""
from __future__ import annotations

from typing import Any, Protocol


class DialogService(Protocol):
    """Minimal message-dialog contract required by the scenario window."""

    def showerror(self, title: str, message: str, **kwargs: Any) -> Any:
        ...

    def showinfo(self, title: str, message: str, **kwargs: Any) -> Any:
        ...


class FileDialogService(Protocol):
    """Minimal file-dialog contract required by report export actions."""

    def askdirectory(self, **kwargs: Any) -> str:
        ...


class RecordingFileDialog:
    """Headless directory-picker double for GUI report-export tests."""

    def __init__(self, directory: str = ""):
        self.directory = directory
        self.calls: list[dict[str, Any]] = []

    def askdirectory(self, **kwargs: Any) -> str:
        self.calls.append(dict(kwargs))
        return self.directory


class RecordingDialog:
    """Headless dialog double that records user-facing messages."""

    def __init__(self) -> None:
        self.errors: list[tuple[str, str]] = []
        self.infos: list[tuple[str, str]] = []

    def showerror(self, title: str, message: str, **_: Any) -> None:
        self.errors.append((title, message))

    def showinfo(self, title: str, message: str, **_: Any) -> None:
        self.infos.append((title, message))

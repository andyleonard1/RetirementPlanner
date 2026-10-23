"""Small injectable GUI event seams for headless lifecycle testing."""
from __future__ import annotations

from typing import Any, Callable, Protocol


class GuiEventService(Protocol):
    """Minimal event/binding contract used by the scenario window."""

    def bind(self, event: str, callback: Callable[[Any], Any]) -> Any:
        ...

    def after_idle(self, callback: Callable[[], Any]) -> Any:
        ...


class TkEventService:
    """Adapter around a Tk-compatible root's event APIs."""

    def __init__(self, root: Any):
        self.root = root

    def bind(self, event: str, callback: Callable[[Any], Any]) -> Any:
        return self.root.bind(event, callback)

    def after_idle(self, callback: Callable[[], Any]) -> Any:
        return self.root.after_idle(callback)


class RecordingEventService:
    """Headless event double that records bindings and scheduled callbacks."""

    def __init__(self) -> None:
        self.bindings: dict[str, Callable[[Any], Any]] = {}
        self.idle_callbacks: list[Callable[[], Any]] = []

    def bind(self, event: str, callback: Callable[[Any], Any]) -> None:
        self.bindings[event] = callback

    def after_idle(self, callback: Callable[[], Any]) -> int:
        self.idle_callbacks.append(callback)
        return len(self.idle_callbacks) - 1

    def run_idle(self) -> None:
        callbacks = tuple(self.idle_callbacks)
        self.idle_callbacks.clear()
        for callback in callbacks:
            callback()

    def trigger(self, event: str) -> Any:
        """Invoke a recorded binding, matching a Tk event for headless tests."""
        callback = self.bindings[event]
        return callback(None)

from __future__ import annotations

from typing import Any, Protocol


class ObserverStatePort(Protocol):
    """Minimal controller capability required by observer view models."""

    def get_observer_state(self, observer: Any, publisher: Any = None) -> dict[str, Any]:
        ...

    def add_observer(self, observer: Any) -> None:
        ...

    def remove_observer(self, observer: Any) -> None:
        ...


class PreviewTextPort(ObserverStatePort, Protocol):
    """Controller capabilities required by preview text view models."""

    def perform_update_preview_text(self, text: str) -> None:
        ...

    def perform_text_selected(self, selection_data: dict[str, Any]) -> None:
        ...


class SearchPort(ObserverStatePort, Protocol):
    """Controller capabilities required by search view models."""

    def perform_end_search(self) -> None:
        ...

    def perform_manual_search(self, search_options: dict[str, Any], caller_mode: str, caller_id: str) -> None:
        ...

    def perform_previous_suggestion(self, caller_id: str | None = None) -> None:
        ...

    def perform_next_suggestion(self, caller_id: str | None = None) -> None:
        ...

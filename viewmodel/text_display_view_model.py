from __future__ import annotations

from typing import Any

from viewmodel.base_view_model import BaseObserverViewModel
from viewmodel.ports import PreviewTextPort


class TextDisplayViewModel(BaseObserverViewModel):
    """Framework-independent state and actions for text display components."""

    observer_id = "text_display"

    def __init__(self, controller: PreviewTextPort, *args: Any, **kwargs: Any) -> None:
        super().__init__(controller=controller, *args, **kwargs)
        self.text: str = ""
        self.cursor_position: str | None = None
        self.is_typing: bool = False

    def apply_state(self, state: dict[str, Any], publisher: Any = None) -> None:
        if "text" in state:
            self.text = state.get("text", "")

    def update_for_observer(self, observer: Any, publisher: Any) -> None:
        state = self._controller.get_observer_state(observer, publisher)
        self.apply_state(state, publisher)

    def select_text(self, selected_text: str, position: int) -> None:
        self._controller.perform_text_selected(
            {"position": position, "selected_text": selected_text}
        )

    def update_preview_text(self, text: str) -> None:
        self.text = text
        self._controller.perform_update_preview_text(text)

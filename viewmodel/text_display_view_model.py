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
        self.cursor_position: int | None = None
        self.is_typing: bool = False
        self.should_preserve_scroll: bool = False
        self.did_replace_text: bool = False
        self._has_received_text: bool = False

    def apply_state(self, state: dict[str, Any], publisher: Any = None) -> None:
        """
        Applies projected text state.

        Scroll behavior is intentionally explicit but backward-compatible:
        - If the controller provides ``preserve_scroll_position`` or
          ``should_preserve_scroll``, that value is used.
        - If the controller provides ``reset_scroll_position``, the inverse is used.
        - Until the controller sends explicit information, the first text render resets
          to the top and later text updates preserve the viewport.
        """
        self.did_replace_text = False

        if "text" not in state:
            return

        new_text = state.get("text", "") or ""
        reset_requested = bool(state.get("reset_scroll_position", False))
        self.did_replace_text = reset_requested or new_text != self.text
        self.should_preserve_scroll = self._resolve_scroll_preservation(state)
        self.text = new_text
        self._has_received_text = True

    def update_for_observer(self, observer: Any, publisher: Any) -> None:
        state = self._controller.get_observer_state(observer, publisher)
        self.apply_state(state, publisher)

    def select_text(self, selected_text: str, position: int) -> None:
        self._controller.perform_text_selected(
            {"position": position, "selected_text": selected_text}
        )

    def update_preview_text(self, text: str) -> None:
        self.text = text
        self.should_preserve_scroll = True
        self._has_received_text = True
        self._controller.perform_update_preview_text(text)

    def _resolve_scroll_preservation(self, state: dict[str, Any]) -> bool:
        """
        Resolves whether the text widget should preserve its current scroll position.

        The controller can later provide one of these keys in the observer state:
        - ``preserve_scroll_position``: direct boolean decision
        - ``should_preserve_scroll``: direct boolean decision
        - ``reset_scroll_position``: inverse boolean decision
        """
        if "reset_scroll_position" in state:
            return not bool(state["reset_scroll_position"])

        for key in ("preserve_scroll_position", "should_preserve_scroll"):
            if key in state:
                return bool(state[key])

        return self._has_received_text

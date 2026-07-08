from __future__ import annotations

from typing import Any, Callable

from viewmodel.text_display_view_model import TextDisplayViewModel
from viewmodel.ports import PreviewTextPort


class AnnotationTextDisplayViewModel(TextDisplayViewModel):
    """View model for annotation text and highlight state."""

    observer_id = "annotation_text_display"

    def __init__(
        self,
        controller: PreviewTextPort,
        is_static_observer: bool = False,
        on_change: Callable[[], None] | None = None,
        auto_register: bool = True,
    ) -> None:
        super().__init__(
            controller=controller,
            observer_id=self.observer_id,
            is_static_observer=is_static_observer,
            on_change=on_change,
            auto_register=auto_register if is_static_observer else False,
        )
        self.tag_highlight_data: list[tuple[str, str, int, int]] = []
        self.search_highlight_data: list[tuple[str, str, int, int]] = []

    def apply_state(self, state: dict[str, Any], publisher: Any = None) -> None:
        super().apply_state(state, publisher)

        if self.did_replace_text:
            self.tag_highlight_data = []
            self.search_highlight_data = []

        if "tag_highlight_data" in state:
            self.tag_highlight_data = state.get("tag_highlight_data", [])
        if "search_highlight_data" in state:
            self.search_highlight_data = state.get("search_highlight_data", [])

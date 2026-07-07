from __future__ import annotations

from typing import Any, Callable

from viewmodel.text_display_view_model import TextDisplayViewModel
from viewmodel.ports import PreviewTextPort


class PreviewTextDisplayViewModel(TextDisplayViewModel):
    """View model for the editable preview text display."""

    observer_id = "preview_text_display"

    def __init__(
        self,
        controller: PreviewTextPort,
        on_change: Callable[[], None] | None = None,
        auto_register: bool = True,
    ) -> None:
        super().__init__(
            controller=controller,
            observer_id=self.observer_id,
            is_static_observer=True,
            on_change=on_change,
            auto_register=auto_register,
        )

    def update(self, publisher: Any) -> None:
        if self.is_typing:
            return
        super().update(publisher)

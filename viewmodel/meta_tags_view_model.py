from __future__ import annotations

from typing import Any, Callable

from viewmodel.base_view_model import BaseObserverViewModel
from viewmodel.ports import ObserverStatePort


class MetaTagsViewModel(BaseObserverViewModel):
    observer_id = "meta_tags"

    def __init__(self, controller: ObserverStatePort, on_change: Callable[[], None] | None = None, auto_register: bool = True) -> None:
        super().__init__(controller, self.observer_id, False, on_change, auto_register)
        self.tag_types: list[str] = []
        self.file_name: str = ""
        self.meta_tags: dict[str, Any] = {}

    def apply_state(self, state: dict[str, Any], publisher: Any = None) -> None:
        if "tag_types" in state:
            self.tag_types = state["tag_types"]
        if "file_name" in state:
            self.file_name = state["file_name"]
        if "meta_tags" in state:
            self.meta_tags = state.get("meta_tags", {})

    def update_meta_tags(self, meta_tags: dict[str, str]) -> None:
        self._controller.perform_update_meta_tags(meta_tags)

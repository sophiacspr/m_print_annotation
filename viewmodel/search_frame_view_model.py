from __future__ import annotations

from typing import Any, Callable
from uuid import uuid4

from viewmodel.base_view_model import BaseObserverViewModel
from viewmodel.ports import SearchPort


class SearchFrameViewModel(BaseObserverViewModel):
    observer_id = "search"

    def __init__(
        self,
        controller: SearchPort,
        root_view_id: str,
        on_change: Callable[[], None] | None = None,
        auto_register: bool = True,
    ) -> None:
        self.root_view_id = root_view_id
        self.view_id = f"{root_view_id}_search"
        self.search_id = uuid4().hex
        super().__init__(controller, self.observer_id, False, on_change, auto_register)
        self.index: int = 0
        self.num_results: int = 0

    def apply_state(self, state: dict[str, Any], publisher: Any = None) -> None:
        self.index = state.get("index", 0)
        self.num_results = state.get("num_results", 0)

    def trigger_search(self, search_term: str, case_sensitive: bool, whole_word: bool, regex: bool) -> None:
        if not search_term:
            self._controller.perform_end_search()
            return
        self._controller.perform_manual_search(
            search_options={
                "search_term": search_term,
                "case_sensitive": case_sensitive,
                "whole_word": whole_word,
                "regex": regex,
            },
            caller_mode=self.root_view_id,
            caller_id=self.search_id,
        )

    def previous_result(self) -> None:
        self._controller.perform_previous_suggestion(caller_id=self.search_id)

    def next_result(self) -> None:
        self._controller.perform_next_suggestion(caller_id=self.search_id)

from __future__ import annotations

from typing import Any, Callable

from viewmodel.base_view_model import BaseObserverViewModel
from viewmodel.ports import ObserverStatePort


class ComparisonHeaderViewModel(BaseObserverViewModel):
    observer_id = "comparison_header"

    def __init__(self, controller: ObserverStatePort, on_change: Callable[[], None] | None = None, auto_register: bool = True) -> None:
        super().__init__(controller, self.observer_id, False, on_change, auto_register)
        self.num_files: int = 0
        self.current_sentence_index: int = 0
        self.num_sentences: int = 0

    def apply_state(self, state: dict[str, Any], publisher: Any = None) -> None:
        if "num_sentences" in state:
            self.num_sentences = state["num_sentences"]
        if "current_sentence_index" in state:
            self.current_sentence_index = state["current_sentence_index"]
        if "file_names" in state:
            self.num_files = len(state["file_names"])

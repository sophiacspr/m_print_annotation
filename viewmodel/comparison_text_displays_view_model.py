from __future__ import annotations

from typing import Any, Callable

from viewmodel.base_view_model import BaseObserverViewModel
from viewmodel.ports import ObserverStatePort


class ComparisonTextDisplaysViewModel(BaseObserverViewModel):
    observer_id = "comparison_text_displays"

    def __init__(self, controller: ObserverStatePort, on_change: Callable[[], None] | None = None, auto_register: bool = True) -> None:
        super().__init__(controller, self.observer_id, False, on_change, auto_register)
        self.num_comparison_displays: int = 0
        self.file_names: list[str] = []
        self.displays_changed: bool = False

    def apply_state(self, state: dict[str, Any], publisher: Any = None) -> None:
        self.displays_changed = False
        if "num_comparison_displays" in state:
            new_num = state["num_comparison_displays"]
            if new_num != self.num_comparison_displays:
                self.num_comparison_displays = new_num
                self.displays_changed = True
        if "file_names" in state:
            self.file_names = state["file_names"]

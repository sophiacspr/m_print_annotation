from __future__ import annotations

from typing import Any, Callable

from viewmodel.base_view_model import BaseObserverViewModel
from viewmodel.ports import ObserverStatePort


class MainWindowViewModel(BaseObserverViewModel):
    observer_id = "main_window"

    def __init__(self, controller: ObserverStatePort, on_change: Callable[[], None] | None = None, auto_register: bool = True) -> None:
        super().__init__(controller, self.observer_id, False, on_change, auto_register)
        self.project_name: str = ""
        self.active_notebook_index: int = 0

    def apply_state(self, state: dict[str, Any], publisher: Any = None) -> None:
        if "project_name" in state:
            self.project_name = state["project_name"]
        if "active_notebook_index" in state:
            self.active_notebook_index = state["active_notebook_index"]

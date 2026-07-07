from __future__ import annotations

from typing import Any, Callable

from viewmodel.base_view_model import BaseObserverViewModel
from viewmodel.ports import ObserverStatePort


class LoadProjectWindowViewModel(BaseObserverViewModel):
    observer_id = "load_project"

    def __init__(self, controller: ObserverStatePort, on_change: Callable[[], None] | None = None, auto_register: bool = True) -> None:
        super().__init__(controller, self.observer_id, False, on_change, auto_register)
        self.project_names: list[str] = []

    def apply_state(self, state: dict[str, Any], publisher: Any = None) -> None:
        projects = state.get("projects", [])
        self.project_names = [project["name"] for project in projects if "name" in project]

    def load_project(self, project_name: str) -> None:
        self._controller.perform_project_load_project(project_name=project_name, reload=True)

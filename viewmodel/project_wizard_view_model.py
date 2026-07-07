from __future__ import annotations

from typing import Any, Callable

from viewmodel.base_view_model import BaseObserverViewModel
from viewmodel.ports import ObserverStatePort


class ProjectWizardViewModel(BaseObserverViewModel):
    observer_id = "new_project_wizard"

    def __init__(self, controller: ObserverStatePort, observer_id: str | None = None, on_change: Callable[[], None] | None = None, auto_register: bool = True) -> None:
        super().__init__(controller, observer_id or self.observer_id, False, on_change, auto_register)
        self.project_data: dict[str, Any] = {}

    def apply_state(self, state: dict[str, Any], publisher: Any = None) -> None:
        self.project_data = dict(state)

    def update_project_data(self, data: dict[str, Any]) -> None:
        self.project_data.update(data)
        self._controller.perform_project_update_project_data(data)

    def add_tag_group(self, tag_group_file_name: str, tag_group: dict[str, Any]) -> None:
        self._controller.perform_project_add_tag_group(tag_group_file_name, tag_group)

    def remove_tag_group(self, group_name: str) -> None:
        self._controller.perform_project_remove_tag_group(group_name)

    def add_tags(self, tags: list[str]) -> None:
        self._controller.perform_project_add_tags(tags)

    def remove_tags(self, selected_indices: list[int]) -> None:
        self._controller.perform_project_remove_tags(selected_indices)

    def create_new_project(self) -> bool:
        return self._controller.perform_project_create_new_project()

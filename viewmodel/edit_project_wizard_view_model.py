from __future__ import annotations

from typing import Any, Callable

from viewmodel.project_wizard_view_model import ProjectWizardViewModel
from viewmodel.ports import ObserverStatePort


class EditProjectWizardViewModel(ProjectWizardViewModel):
    observer_id = "edit_project_wizard"

    def __init__(self, controller: ObserverStatePort, on_change: Callable[[], None] | None = None, auto_register: bool = True) -> None:
        super().__init__(controller, self.observer_id, on_change, auto_register)
        self.available_projects: list[str] = []
        self.selected_project: str | None = None

    def apply_state(self, state: dict[str, Any], publisher: Any = None) -> None:
        super().apply_state(state, publisher)
        projects = state.get("projects", [])
        self.available_projects = [project["name"] for project in projects if "name" in project]

    def choose_project(self, project_name: str) -> None:
        self.selected_project = project_name
        self._controller.perform_load_project_data_for_editing(project_name)

    def edit_project(self, selected_project: str | None, project_data: dict[str, Any]) -> None:
        self._controller.perform_project_edit_project(selected_project, project_data)

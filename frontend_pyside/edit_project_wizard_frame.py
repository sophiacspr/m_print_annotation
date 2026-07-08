from __future__ import annotations

from typing import Any

from PySide6.QtWidgets import QLabel, QListWidget, QMessageBox, QPushButton, QVBoxLayout, QWidget

from controller.interfaces import IController
from enums.menu_pages import MenuSubpage
from frontend_pyside.project_wizard_frame import NewProjectWizardFrame
from viewmodel.edit_project_wizard_view_model import EditProjectWizardViewModel


class EditProjectWizardFrame(QWidget):
    observer_id = "edit_project_wizard"

    def __init__(self, controller: IController, master: QWidget | None = None, parent_window: QWidget | None = None) -> None:
        super().__init__(master)
        self._controller = controller
        self._parent_window = parent_window
        self._view_model = EditProjectWizardViewModel(controller=controller, on_change=self._render_from_view_model, auto_register=False)
        self._controller.add_observer(self._view_model)
        self._selected_project: str | None = None
        self._project_data: dict[str, Any] = {}

        layout = QVBoxLayout(self)
        self._listbox_projects = QListWidget()
        choose_button = QPushButton("Choose project")
        choose_button.clicked.connect(self._choose_project)
        layout.addWidget(QLabel("Select project to edit"))
        layout.addWidget(self._listbox_projects)
        layout.addWidget(choose_button)

        self._wizard = NewProjectWizardFrame(
            controller=controller,
            parent_window=parent_window,
            master=self,
            register_as_observer=False,
        )
        self._wizard._finish_button.setText("Edit project")
        try:
            self._wizard._finish_button.clicked.disconnect()
        except RuntimeError:
            pass
        self._wizard._finish_button.clicked.connect(self._on_button_pressed_edit_project)
        layout.addWidget(self._wizard, 1)

    def update(self, publisher: Any) -> None:
        self._view_model.update(publisher)

    def select_subtab(self, subtab: MenuSubpage) -> None:
        self._wizard.select_subtab(subtab)

    def get_observer_id(self) -> str:
        return self._view_model.get_observer_id()

    def is_static_observer(self) -> bool:
        return self._view_model.is_static_observer()

    def _choose_project(self) -> None:
        items = self._listbox_projects.selectedItems()
        if not items:
            QMessageBox.warning(self, "Error", "Please select a project.")
            return
        self._selected_project = items[0].text()
        self._view_model.choose_project(self._selected_project)

    def _render_from_view_model(self) -> None:
        self._project_data = dict(self._view_model.project_data)
        self._wizard.apply_state(self._view_model.project_data)
        self._populate_projects_listbox(self._view_model.available_projects)

    def _populate_projects_listbox(self, projects: list[str]) -> None:
        current = self._selected_project
        self._listbox_projects.clear()
        self._listbox_projects.addItems([str(project) for project in projects])
        if projects and current is None:
            self._listbox_projects.setCurrentRow(0)

    def _on_button_pressed_edit_project(self) -> None:
        current_page_data = self._wizard._collect_current_page_data()
        self._view_model.update_project_data(current_page_data)
        self._view_model.edit_project(self._selected_project, self._view_model.project_data)

    def closeEvent(self, event) -> None:  # noqa: N802 - Qt API
        self._view_model.dispose()
        super().closeEvent(event)

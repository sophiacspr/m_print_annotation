from __future__ import annotations

from typing import Any

from PySide6.QtWidgets import (
    QDialog,
    QLabel,
    QListWidget,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from controller.interfaces import IController
from viewmodel.load_project_window_view_model import LoadProjectWindowViewModel


class LoadProjectWindow(QDialog):
    """
    Dialog for selecting and loading an existing project.

    The dialog observes the shared LoadProjectWindowViewModel. It explicitly
    refreshes the project list after the widgets have been created, so projects
    that already exist in the ProjectWizardModel are shown immediately when the
    dialog opens.
    """

    observer_id = "load_project"

    def __init__(self, controller: IController, master: QWidget | None = None) -> None:
        super().__init__(master)

        self._controller = controller
        self._is_disposed = False
        self._view_model = LoadProjectWindowViewModel(
            controller=controller,
            on_change=self._render_from_view_model,
            auto_register=False,
        )

        self.setWindowTitle("Load project")
        self.resize(420, 360)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Select project"))

        self._project_list = QListWidget()
        layout.addWidget(self._project_list, 1)

        load_button = QPushButton("Load project")
        load_button.clicked.connect(self._on_load_project)
        layout.addWidget(load_button)

        self._controller.add_observer(self._view_model)
        self._refresh_projects()

    def _refresh_projects(self) -> None:
        """
        Refreshes available projects and renders the current view model state.

        `perform_project_update_projects` updates the ProjectWizardModel and
        normally triggers observer notifications. The explicit view-model update
        afterward is a safe fallback for controllers/publishers that do not emit
        a notification when the data is unchanged.
        """
        self._controller.perform_project_update_projects()
        self._view_model.update(None)

    def update(self, publisher: Any) -> None:
        """
        Legacy forwarding method. The dialog itself should not be registered as
        observer, but keeping this method preserves compatibility with older code.
        """
        self._view_model.update(publisher)

    def get_observer_id(self) -> str:
        """
        Returns the stable observer identifier used by the source mapping.
        """
        return self._view_model.get_observer_id()

    def _render_from_view_model(self) -> None:
        """
        Renders the project names exposed by the framework-independent view model.
        """
        self._project_list.clear()
        self._project_list.addItems(self._view_model.project_names)
        if self._view_model.project_names:
            self._project_list.setCurrentRow(0)

    def _on_load_project(self) -> None:
        """
        Loads the currently selected project.
        """
        selected = self._project_list.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Error", "Please select a project.")
            return

        self._view_model.load_project(selected[0].text())
        self.accept()

    def _dispose_view_model(self) -> None:
        """
        Deregisters the view model exactly once.
        """
        if self._is_disposed:
            return
        self._view_model.dispose()
        self._is_disposed = True

    def done(self, result: int) -> None:
        """
        Ensures observer cleanup for accept(), reject(), and close().
        """
        self._dispose_view_model()
        super().done(result)

    def closeEvent(self, event) -> None:  # noqa: N802 - Qt API
        """
        Ensures observer cleanup when the native window close button is used.
        """
        self._dispose_view_model()
        super().closeEvent(event)

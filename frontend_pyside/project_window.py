from __future__ import annotations

from PySide6.QtWidgets import QDialog, QTabWidget, QVBoxLayout, QWidget

from controller.interfaces import IController
from enums.menu_pages import MenuPage, MenuSubpage
from frontend_pyside.edit_project_wizard_frame import EditProjectWizardFrame
from frontend_pyside.project_wizard_frame import NewProjectWizardFrame
from frontend_pyside.settings_views import ProjectSettings


class ProjectWindow(QDialog):
    def __init__(self, controller: IController, master: QWidget | None = None, *args, **kwargs) -> None:
        super().__init__(master, *args, **kwargs)
        self._controller = controller
        self.setWindowTitle("Project")
        self.resize(1100, 720)
        layout = QVBoxLayout(self)
        self._notebook = QTabWidget()
        layout.addWidget(self._notebook)
        self._new_project_frame = NewProjectWizardFrame(controller=self._controller, master=self._notebook, parent_window=self)
        self._edit_project_frame = EditProjectWizardFrame(controller=self._controller, master=self._notebook, parent_window=self)
        self._project_settings_frame = ProjectSettings(controller=self._controller, master=self._notebook)
        self._notebook.addTab(self._new_project_frame, "New Project")
        self._notebook.addTab(self._edit_project_frame, "Edit Project")
        self._notebook.addTab(self._project_settings_frame, "Project Settings")

    def select_tab(self, tab: MenuPage, subtab: MenuSubpage | None = None) -> None:
        mapping = {
            MenuPage.NEW_PROJECT: self._new_project_frame,
            MenuPage.EDIT_PROJECT: self._edit_project_frame,
            MenuPage.PROJECT_SETTINGS: self._project_settings_frame,
        }
        widget = mapping.get(tab)
        if widget is None:
            raise ValueError(f"Unknown tab: {tab}")
        self._notebook.setCurrentWidget(widget)
        if subtab and hasattr(widget, "select_subtab"):
            widget.select_subtab(subtab)

from __future__ import annotations

from PySide6.QtWidgets import QDialog, QTabWidget, QVBoxLayout, QWidget

from controller.interfaces import IController
from enums.menu_pages import MenuPage
from frontend_pyside.settings_views import GlobalSettings, ProjectSettings


class SettingsWindow(QDialog):
    def __init__(self, controller: IController, master: QWidget | None = None, *args, **kwargs) -> None:
        super().__init__(master, *args, **kwargs)
        self._controller = controller
        self.setWindowTitle("Settings")
        self.resize(1000, 600)
        layout = QVBoxLayout(self)
        self._notebook = QTabWidget()
        layout.addWidget(self._notebook)
        self._global_settings = GlobalSettings(controller=self._controller, master=self._notebook)
        self._project_settings = ProjectSettings(controller=self._controller, master=self._notebook)
        self._notebook.addTab(self._global_settings, "Global Settings")
        self._notebook.addTab(self._project_settings, "Project Settings")

    def select_tab(self, tab: MenuPage) -> None:
        mapping = {
            MenuPage.GLOBAL_SETTINGS: self._global_settings,
            MenuPage.PROJECT_SETTINGS: self._project_settings,
        }
        widget = mapping.get(tab)
        if widget is None:
            raise ValueError(f"Unknown tab name: {tab}")
        self._notebook.setCurrentWidget(widget)

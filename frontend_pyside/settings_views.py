from __future__ import annotations

from typing import Any

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from controller.interfaces import IController
from viewmodel.settings_view_models import GlobalSettingsViewModel, ProjectSettingsViewModel


class GlobalSettings(QWidget):
    observer_id = "global_settings"

    def __init__(self, controller: IController, master: QWidget | None = None) -> None:
        super().__init__(master)
        self._view_model = GlobalSettingsViewModel(controller=controller, on_change=self._render_from_view_model, auto_register=False)
        controller.add_observer(self._view_model)
        layout = QVBoxLayout(self)
        self._label = QLabel("Global settings")
        layout.addWidget(self._label)
        layout.addStretch(1)

    def update(self, publisher: Any) -> None:
        self._view_model.update(publisher)

    def get_observer_id(self) -> str:
        return self._view_model.get_observer_id()

    def _render_from_view_model(self) -> None:
        self._label.setText("Global settings")


class ProjectSettings(QWidget):
    observer_id = "project_settings"

    def __init__(self, controller: IController, master: QWidget | None = None) -> None:
        super().__init__(master)
        self._view_model = ProjectSettingsViewModel(controller=controller, on_change=self._render_from_view_model, auto_register=False)
        controller.add_observer(self._view_model)
        layout = QVBoxLayout(self)
        self._label = QLabel("Project settings")
        layout.addWidget(self._label)
        layout.addStretch(1)

    def update(self, publisher: Any) -> None:
        self._view_model.update(publisher)

    def get_observer_id(self) -> str:
        return self._view_model.get_observer_id()

    def _render_from_view_model(self) -> None:
        self._label.setText("Project settings")

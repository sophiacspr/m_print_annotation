from __future__ import annotations

from typing import Any

from PySide6.QtWidgets import QVBoxLayout, QWidget

from controller.interfaces import IController
from frontend_pyside.text_display_widget import TextDisplayWidget
from viewmodel.preview_text_display_view_model import PreviewTextDisplayViewModel


class PreviewTextDisplayFrame(QWidget):
    """Editable preview text display backed by PreviewTextDisplayViewModel."""

    observer_id = "preview_text_display"

    def __init__(self, parent: QWidget | None, controller: IController, editable: bool = True) -> None:
        super().__init__(parent)
        self._controller = controller
        self._view_model = PreviewTextDisplayViewModel(
            controller=controller,
            on_change=self._render_from_view_model,
            auto_register=False,
        )
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self._text_display = TextDisplayWidget(self, self._view_model, editable=editable)
        self.text_widget = self._text_display.text_widget
        layout.addWidget(self._text_display)
        self._controller.add_observer(self._view_model)

    def get_view_model(self) -> PreviewTextDisplayViewModel:
        return self._view_model

    def dispose(self) -> None:
        self._view_model.dispose()

    def update(self, publisher: Any) -> None:
        self._view_model.update(publisher)

    def get_observer_id(self) -> str:
        return self._view_model.get_observer_id()

    def is_static_observer(self) -> bool:
        return self._view_model.is_static_observer()

    def disable_selection(self) -> None:
        self._text_display.disable_selection()

    def _render_from_view_model(self) -> None:
        self._text_display.render_text(self._view_model.text)

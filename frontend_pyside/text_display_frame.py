from __future__ import annotations

from typing import Any

from PySide6.QtWidgets import QWidget

from controller.interfaces import IController
from frontend_pyside.text_display_widget import TextDisplayWidget
from viewmodel.text_display_view_model import TextDisplayViewModel


class TextDisplayFrame(TextDisplayWidget):
    """Compatibility wrapper for the old TextDisplayFrame class name."""

    observer_id = "text_display"

    def __init__(
        self,
        parent: QWidget | None,
        controller: IController,
        editable: bool = False,
        is_static_observer: bool = False,
        height: int | None = None,
    ) -> None:
        self._view_model = TextDisplayViewModel(
            controller=controller,
            observer_id=self.observer_id,
            is_static_observer=is_static_observer,
            auto_register=False,
        )
        super().__init__(parent, self._view_model, editable=editable, height=height)
        self._controller = controller
        if is_static_observer:
            self._controller.add_observer(self._view_model)

    def update(self, publisher: Any) -> None:
        self._view_model.update(publisher)

    def get_observer_id(self) -> str:
        return self._view_model.get_observer_id()

    def is_static_observer(self) -> bool:
        return self._view_model.is_static_observer()

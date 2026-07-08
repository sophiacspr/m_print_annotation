from __future__ import annotations

from typing import Any

from PySide6.QtGui import QColor, QTextCharFormat, QTextCursor
from PySide6.QtWidgets import QVBoxLayout, QWidget

from controller.interfaces import IController
from frontend_pyside.text_display_widget import TextDisplayWidget
from viewmodel.annotation_text_display_view_model import AnnotationTextDisplayViewModel


class AnnotationTextDisplayFrame(QWidget):
    """Read-only text display for annotation mode, including tag/search highlights."""

    observer_id = "annotation_text_display"

    def __init__(
        self,
        parent: QWidget | None,
        controller: IController,
        is_static_observer: bool = False,
        height: int | None = None,
    ) -> None:
        super().__init__(parent)
        self._controller = controller
        self._view_model = AnnotationTextDisplayViewModel(
            controller=controller,
            is_static_observer=is_static_observer,
            on_change=self._render_from_view_model,
            auto_register=False,
        )
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self._text_display = TextDisplayWidget(self, self._view_model, editable=False, height=height)
        self.text_widget = self._text_display.text_widget
        layout.addWidget(self._text_display)
        if is_static_observer:
            self._controller.add_observer(self._view_model)

    def get_view_model(self) -> AnnotationTextDisplayViewModel:
        return self._view_model

    def dispose(self) -> None:
        self._view_model.dispose()

    def get_observer_id(self) -> str:
        return self._view_model.get_observer_id()

    def is_static_observer(self) -> bool:
        return self._view_model.is_static_observer()

    def update(self, publisher: Any) -> None:
        self._view_model.update(publisher)

    def disable_selection(self) -> None:
        self._text_display.disable_selection()

    def _render_from_view_model(self) -> None:
        self._text_display.render_text(self._view_model.text)
        self._apply_highlights(self._view_model.tag_highlight_data)
        self._apply_highlights(self._view_model.search_highlight_data)

    def _apply_highlights(self, highlight_data: list[tuple[str, str, int, int]]) -> None:
        cursor = self.text_widget.textCursor()
        cursor.select(QTextCursor.SelectionType.Document)
        clear_format = QTextCharFormat()
        cursor.mergeCharFormat(clear_format)

        document = self.text_widget.document()
        for background, foreground, start, end in highlight_data:
            cursor = QTextCursor(document)
            cursor.setPosition(max(0, start))
            cursor.setPosition(max(0, end), QTextCursor.MoveMode.KeepAnchor)
            text_format = QTextCharFormat()
            text_format.setBackground(QColor(background))
            text_format.setForeground(QColor(foreground))
            cursor.mergeCharFormat(text_format)

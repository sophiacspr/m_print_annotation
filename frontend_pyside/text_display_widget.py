from __future__ import annotations

from typing import Any

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QPlainTextEdit, QVBoxLayout, QWidget

from viewmodel.text_display_view_model import TextDisplayViewModel


class TextDisplayWidget(QWidget):
    """Qt text widget wrapper used by preview and annotation displays."""

    DEBOUNCE_DELAY_MS = 300

    def __init__(
        self,
        parent: QWidget | None,
        view_model: TextDisplayViewModel,
        *,
        editable: bool = False,
        height: int | None = None,
    ) -> None:
        super().__init__(parent)
        self._view_model = view_model
        self._editable = editable
        self._internal_update = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.text_edit = QPlainTextEdit()
        self.text_edit.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)
        self.text_edit.setReadOnly(not editable)
        if height is not None:
            # Height is deliberately approximate; the PySide frontend uses a more regular layout.
            self.text_edit.setMinimumHeight(max(80, height * 22))
        layout.addWidget(self.text_edit)

        self._debounce_timer = QTimer(self)
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.timeout.connect(self._finalize_update)

        self.text_edit.textChanged.connect(self._on_text_changed)
        self.text_edit.selectionChanged.connect(self._on_selection_changed)

    @property
    def text_widget(self) -> QPlainTextEdit:
        return self.text_edit

    def render_text(self, text: str) -> None:
        cursor_position = self.text_edit.textCursor().position()
        self._internal_update = True
        self.text_edit.setPlainText(text or "")
        cursor = self.text_edit.textCursor()
        cursor.setPosition(min(cursor_position, len(self.text_edit.toPlainText())))
        self.text_edit.setTextCursor(cursor)
        self._internal_update = False

    def disable_selection(self) -> None:
        self.text_edit.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)

    def update_for_observer(self, observer: Any, publisher: Any) -> None:
        if self._view_model.is_typing:
            return
        self._view_model.update_for_observer(observer, publisher)
        self.render_text(self._view_model.text)

    def _on_text_changed(self) -> None:
        if self._internal_update or not self._editable:
            return
        self._view_model.is_typing = True
        self._view_model.update_preview_text(self.text_edit.toPlainText().strip())
        self._debounce_timer.start(self.DEBOUNCE_DELAY_MS)

    def _finalize_update(self) -> None:
        self._view_model.is_typing = False
        self._view_model.update_preview_text(self.text_edit.toPlainText().strip())

    def _on_selection_changed(self) -> None:
        cursor = self.text_edit.textCursor()
        if not cursor.hasSelection():
            return
        selected_text = cursor.selectedText().replace("\u2029", "\n")
        self._view_model.select_text(selected_text=selected_text, position=cursor.selectionStart())

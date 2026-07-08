from __future__ import annotations

from typing import Any

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QTextCharFormat, QTextCursor
from PySide6.QtWidgets import QPlainTextEdit, QScrollBar, QVBoxLayout, QWidget

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

    def render_text(self, text: str, *, preserve_scroll: bool | None = None) -> None:
        """
        Renders text while optionally preserving the current viewport position.

        Args:
            text: Text to display.
            preserve_scroll: If True, keep the current vertical/horizontal scroll position.
                If False, reset the viewport to the top. If None, the decision is read
                from the view model.
        """
        new_text = text or ""
        if self.text_edit.toPlainText() == new_text:
            return

        should_preserve_scroll = (
            self._view_model.should_preserve_scroll
            if preserve_scroll is None
            else preserve_scroll
        )

        vertical_bar = self.text_edit.verticalScrollBar()
        horizontal_bar = self.text_edit.horizontalScrollBar()
        old_vertical_value = vertical_bar.value()
        old_horizontal_value = horizontal_bar.value()
        old_cursor_position = self.text_edit.textCursor().position()

        self._internal_update = True
        previous_signal_state = self.text_edit.blockSignals(True)

        try:
            self._clear_text_formatting()
            self.text_edit.setPlainText(new_text)
            self._clear_text_formatting()

            cursor = self.text_edit.textCursor()
            if should_preserve_scroll:
                cursor.setPosition(min(old_cursor_position, len(new_text)))
            else:
                cursor.setPosition(0)
            self.text_edit.setTextCursor(cursor)

            if should_preserve_scroll:
                self._set_scrollbar_value(vertical_bar, old_vertical_value)
                self._set_scrollbar_value(horizontal_bar, old_horizontal_value)
                QTimer.singleShot(
                    0,
                    lambda: self._restore_scroll_position(
                        vertical_bar,
                        old_vertical_value,
                        horizontal_bar,
                        old_horizontal_value,
                    ),
                )
            else:
                self._set_scrollbar_value(vertical_bar, 0)
                self._set_scrollbar_value(horizontal_bar, 0)
                QTimer.singleShot(0, lambda: self._restore_scroll_position(vertical_bar, 0, horizontal_bar, 0))
        finally:
            self.text_edit.blockSignals(previous_signal_state)
            self._internal_update = False


    def _clear_text_formatting(self) -> None:
        """Clears embedded QTextDocument formatting and transient selections."""
        self.text_edit.setExtraSelections([])
        cursor = QTextCursor(self.text_edit.document())
        cursor.select(QTextCursor.SelectionType.Document)
        cursor.setCharFormat(QTextCharFormat())
        cursor.clearSelection()
        self.text_edit.setTextCursor(cursor)

    def disable_selection(self) -> None:
        self.text_edit.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)

    def update_for_observer(self, observer: Any, publisher: Any) -> None:
        if self._view_model.is_typing:
            return
        self._view_model.update_for_observer(observer, publisher)
        self.render_text(
            self._view_model.text,
            preserve_scroll=self._view_model.should_preserve_scroll,
        )

    def _restore_scroll_position(
        self,
        vertical_bar: QScrollBar,
        vertical_value: int,
        horizontal_bar: QScrollBar,
        horizontal_value: int,
    ) -> None:
        """Restores scrollbars after Qt has recalculated the document layout."""
        self._set_scrollbar_value(vertical_bar, vertical_value)
        self._set_scrollbar_value(horizontal_bar, horizontal_value)

    def _set_scrollbar_value(self, scrollbar: QScrollBar, value: int) -> None:
        """Sets a scrollbar value clamped to its current valid range."""
        scrollbar.setValue(max(scrollbar.minimum(), min(value, scrollbar.maximum())))

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

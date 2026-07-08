from __future__ import annotations

from PySide6.QtGui import QColor, QTextCharFormat, QTextCursor
from PySide6.QtWidgets import QPlainTextEdit, QTextEdit

HighlightData = tuple[str, str, int, int]


class PySideHighlightRenderer:
    """Renders highlight data into a QPlainTextEdit using ExtraSelections."""

    def __init__(self) -> None:
        self._format_cache: dict[tuple[str, str], QTextCharFormat] = {}

    def render(
        self,
        *,
        text_widget: QPlainTextEdit,
        tag_highlight_data: list[HighlightData],
        search_highlight_data: list[HighlightData],
    ) -> None:
        """
        Render tag and search highlights.

        Args:
            text_widget: The target text widget.
            tag_highlight_data: Styled tag highlights.
            search_highlight_data: Styled search highlights.
        """
        selections: list[QTextEdit.ExtraSelection] = []
        document = text_widget.document()
        max_position = max(0, document.characterCount() - 1)

        for background, foreground, start, end in [
            *tag_highlight_data,
            *search_highlight_data,
        ]:
            start_position = max(0, min(start, max_position))
            end_position = max(start_position, min(end, max_position))

            if start_position == end_position:
                continue

            cursor = QTextCursor(document)
            cursor.setPosition(start_position)
            cursor.setPosition(end_position, QTextCursor.MoveMode.KeepAnchor)

            selection = QTextEdit.ExtraSelection()
            selection.cursor = cursor
            selection.format = self._get_format(background, foreground)
            selections.append(selection)

        text_widget.setExtraSelections(selections)

    def _get_format(self, background: str, foreground: str) -> QTextCharFormat:
        """
        Return a cached QTextCharFormat for one color pair.

        Args:
            background: Background color.
            foreground: Foreground color.

        Returns:
            A QTextCharFormat instance.
        """
        key = (background, foreground)
        if key not in self._format_cache:
            text_format = QTextCharFormat()
            text_format.setBackground(QColor(background))
            text_format.setForeground(QColor(foreground))
            self._format_cache[key] = text_format

        return self._format_cache[key]
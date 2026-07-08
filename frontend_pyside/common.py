from __future__ import annotations

from typing import Any, Iterable

from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLayout,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


MARGIN = 12
SPACING = 8


def clear_layout(layout: QLayout) -> None:
    """Remove all items and child widgets from a Qt layout."""
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        child_layout = item.layout()
        if widget is not None:
            widget.setParent(None)
            widget.deleteLater()
        elif child_layout is not None:
            clear_layout(child_layout)


def make_vbox(parent: QWidget | None = None, *, margin: int = MARGIN, spacing: int = SPACING) -> QVBoxLayout:
    layout = QVBoxLayout(parent)
    layout.setContentsMargins(margin, margin, margin, margin)
    layout.setSpacing(spacing)
    return layout


def make_hbox(parent: QWidget | None = None, *, margin: int = MARGIN, spacing: int = SPACING) -> QHBoxLayout:
    layout = QHBoxLayout(parent)
    layout.setContentsMargins(margin, margin, margin, margin)
    layout.setSpacing(spacing)
    return layout


class Section(QFrame):
    """Small visual container used to make the PySide frontend look consistent."""

    def __init__(self, title: str | None = None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("section")
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.layout = make_vbox(self)
        if title:
            label = QLabel(title)
            label.setObjectName("sectionTitle")
            self.layout.addWidget(label)


class ScrollContainer(QWidget):
    """Reusable scroll area with a vertical inner layout."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        outer = make_vbox(self, margin=0, spacing=0)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.content = QWidget()
        self.content_layout = make_vbox(self.content)
        self.scroll_area.setWidget(self.content)
        outer.addWidget(self.scroll_area)

    def addWidget(self, widget: QWidget) -> None:  # noqa: N802 - Qt naming convention
        self.content_layout.addWidget(widget)

    def clear(self) -> None:
        clear_layout(self.content_layout)

    def addStretch(self) -> None:  # noqa: N802 - Qt naming convention
        self.content_layout.addStretch(1)


def set_combo_values(combo: Any, values: Iterable[str]) -> None:
    current = combo.currentText() if hasattr(combo, "currentText") else ""
    combo.clear()
    combo.addItems([str(value) for value in values])
    index = combo.findText(current)
    if index >= 0:
        combo.setCurrentIndex(index)


def selected_list_items(list_widget: Any) -> list[str]:
    return [item.text() for item in list_widget.selectedItems()]


def selected_list_indices(list_widget: Any) -> list[int]:
    selected = []
    for item in list_widget.selectedItems():
        selected.append(list_widget.row(item))
    return selected


def elide(text: str, limit: int = 60) -> str:
    return text if len(text) <= limit else text[: limit - 3] + "..."


def add_button_row(layout: QVBoxLayout, buttons: list[QPushButton]) -> None:
    row = QHBoxLayout()
    row.setContentsMargins(0, 0, 0, 0)
    row.setSpacing(SPACING)
    row.addStretch(1)
    for button in buttons:
        row.addWidget(button)
    layout.addLayout(row)

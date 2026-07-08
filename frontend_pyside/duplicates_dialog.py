from __future__ import annotations

from typing import Any

from PySide6.QtWidgets import QDialog, QDialogButtonBox, QLabel, QListWidget, QVBoxLayout, QWidget


class DuplicatesDialog(QDialog):
    """Dialog for choosing duplicate tag definitions to keep."""

    def __init__(self, duplicates: dict[str, list[dict[str, Any]]], master: QWidget | None = None) -> None:
        super().__init__(master)
        self._duplicates = duplicates
        self._result: list[dict[str, Any]] | None = None
        self.setWindowTitle("Duplicate tags")
        self.resize(560, 420)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Select entries to keep."))
        self._list = QListWidget()
        self._items: list[dict[str, Any]] = []
        for tag_type, items in duplicates.items():
            for item in items:
                self._items.append(item)
                self._list.addItem(f"{tag_type}: {item}")
        self._list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        layout.addWidget(self._list, 1)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self._on_button_pressed_ok)
        buttons.rejected.connect(self._on_button_pressed_cancel)
        layout.addWidget(buttons)

    def show(self) -> list[dict[str, Any]] | None:  # type: ignore[override]
        return self._result if self.exec() == QDialog.DialogCode.Accepted else None

    def _on_button_pressed_ok(self) -> None:
        self._result = [self._items[self._list.row(item)] for item in self._list.selectedItems()]
        self.accept()

    def _on_button_pressed_cancel(self) -> None:
        self._result = None
        self.reject()

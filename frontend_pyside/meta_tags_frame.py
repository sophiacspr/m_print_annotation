from __future__ import annotations

from typing import Any

from PySide6.QtWidgets import QFormLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget

from controller.interfaces import IController
from viewmodel.meta_tags_view_model import MetaTagsViewModel


class MetaTagsFrame(QWidget):
    observer_id = "meta_tags"

    def __init__(self, parent: QWidget | None, controller: IController) -> None:
        super().__init__(parent)
        self._controller = controller
        self._view_model = MetaTagsViewModel(controller=controller, on_change=self._render_from_view_model, auto_register=False)
        self._controller.add_observer(self._view_model)
        self._tag_types: list[str] = []
        self._entries: dict[str, QLineEdit] = {}
        self._render()

    def _render(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        header = QHBoxLayout()
        header.addWidget(QLabel("Document"))
        self._file_name_label = QLabel("")
        self._file_name_label.setObjectName("fileNameLabel")
        header.addWidget(self._file_name_label, 1)
        self._update_button = QPushButton("Update meta tags")
        self._update_button.clicked.connect(self._button_pressed_update_meta_tags)
        header.addWidget(self._update_button)
        layout.addLayout(header)
        self._form = QFormLayout()
        layout.addLayout(self._form)

    def _rebuild_entries(self) -> None:
        while self._form.rowCount():
            self._form.removeRow(0)
        self._entries.clear()
        for tag_type in self._tag_types:
            entry = QLineEdit()
            self._entries[tag_type] = entry
            self._form.addRow(tag_type, entry)

    def get_meta_tag_labels(self) -> list[str]:
        return list(self._entries.keys())

    def set_meta_tag_labels(self, labels: list[str]) -> None:
        self._tag_types = list(labels)
        self._rebuild_entries()

    def update(self, publisher: Any) -> None:
        self._view_model.update(publisher)

    def finalize_view(self) -> None:
        self._view_model.finalize_view()

    def get_observer_id(self) -> str:
        return self._view_model.get_observer_id()

    def _render_from_view_model(self) -> None:
        if self._view_model.tag_types != self._tag_types:
            self._tag_types = list(self._view_model.tag_types)
            self._rebuild_entries()
        if self._view_model.file_name:
            self._file_name_label.setText(self._view_model.file_name)
        for tag_type, tags in self._view_model.meta_tags.items():
            entry = self._entries.get(tag_type)
            if entry is not None:
                entry.setText(", ".join(str(tag) for tag in tags) if isinstance(tags, list) else str(tags))

    def _button_pressed_update_meta_tags(self) -> None:
        meta_tags = {tag_type: entry.text().strip() for tag_type, entry in self._entries.items()}
        self._view_model.update_meta_tags(meta_tags)

from __future__ import annotations

from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QCheckBox, QHBoxLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget

from controller.interfaces import IController
from viewmodel.search_frame_view_model import SearchFrameViewModel


class SearchFrame(QWidget):
    observer_id = "search"

    def __init__(self, parent: QWidget | None, controller: IController, root_view_id: str) -> None:
        super().__init__(parent)
        self._controller = controller
        self._view_model = SearchFrameViewModel(
            controller=controller,
            root_view_id=root_view_id,
            on_change=self._render_from_view_model,
            auto_register=False,
        )
        self._root_view_id = self._view_model.root_view_id
        self._view_id = self._view_model.view_id
        self._search_id = self._view_model.search_id
        self._controller.add_observer(self._view_model)
        self._controller.register_view(self._view_id, self)
        self._render()

    def _render(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        top = QHBoxLayout()
        self.search_entry = QLineEdit()
        self.search_entry.setPlaceholderText("Search text")
        self.search_entry.returnPressed.connect(self._trigger_search)
        self.case_sensitive_checkbox = QCheckBox("Case")
        self.whole_word_checkbox = QCheckBox("Whole word")
        self.regex_checkbox = QCheckBox("Regex")
        search_button = QPushButton("Search")
        search_button.clicked.connect(self._trigger_search)
        top.addWidget(self.search_entry, 1)
        top.addWidget(self.case_sensitive_checkbox)
        top.addWidget(self.whole_word_checkbox)
        top.addWidget(self.regex_checkbox)
        top.addWidget(search_button)
        layout.addLayout(top)

        bottom = QHBoxLayout()
        self.previous_button = QPushButton("<")
        self.next_button = QPushButton(">")
        self.previous_button.clicked.connect(self._view_model.previous_result)
        self.next_button.clicked.connect(self._view_model.next_result)
        self.info_label = QLabel("0 / 0")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        bottom.addStretch(1)
        bottom.addWidget(self.previous_button)
        bottom.addWidget(self.info_label)
        bottom.addWidget(self.next_button)
        layout.addLayout(bottom)

    def _trigger_search(self) -> None:
        self._view_model.trigger_search(
            self.search_entry.text().strip(),
            self.case_sensitive_checkbox.isChecked(),
            self.whole_word_checkbox.isChecked(),
            self.regex_checkbox.isChecked(),
        )

    def reset_entry(self) -> None:
        self.search_entry.clear()

    def update(self, publisher: Any) -> None:
        self._view_model.update(publisher)

    def get_observer_id(self) -> str:
        return self._view_model.get_observer_id()

    def _render_from_view_model(self) -> None:
        current = self._view_model.index + 1 if self._view_model.num_results else 0
        self.info_label.setText(f"{current} / {self._view_model.num_results}")

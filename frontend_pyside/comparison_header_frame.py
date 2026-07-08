from __future__ import annotations

from typing import Any

from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QSpinBox, QWidget

from controller.interfaces import IController
from viewmodel.comparison_header_view_model import ComparisonHeaderViewModel


class ComparisonHeaderFrame(QWidget):
    observer_id = "comparison_header"

    def __init__(self, parent: QWidget | None, controller: IController) -> None:
        super().__init__(parent)
        self._controller = controller
        self._view_model = ComparisonHeaderViewModel(controller=controller, on_change=self._render_from_view_model, auto_register=False)
        self._controller.add_observer(self._view_model)
        self._render()

    def _render(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        self.info_label = QLabel("Sentence 0 / 0")
        layout.addWidget(self.info_label, 1)
        previous_button = QPushButton("Previous sentence")
        previous_button.clicked.connect(self._controller.perform_prev_sentence)
        next_button = QPushButton("Next sentence")
        next_button.clicked.connect(self._controller.perform_next_sentence)
        self.adoption_index = QSpinBox()
        self.adoption_index.setMinimum(1)
        self.adoption_index.setMaximum(1)
        adopt_button = QPushButton("Adopt annotation")
        adopt_button.clicked.connect(self._on_button_pressed_adopt)
        layout.addWidget(previous_button)
        layout.addWidget(next_button)
        layout.addWidget(QLabel("Source"))
        layout.addWidget(self.adoption_index)
        layout.addWidget(adopt_button)

    def update(self, publisher: Any) -> None:
        self._view_model.update(publisher)

    def finalize_view(self) -> None:
        self._view_model.finalize_view()

    def get_observer_id(self) -> str:
        return self._view_model.get_observer_id()

    def _render_from_view_model(self) -> None:
        current = self._view_model.current_sentence_index + 1 if self._view_model.num_sentences else 0
        self.info_label.setText(f"Sentence {current} / {self._view_model.num_sentences}")
        self.adoption_index.setMaximum(max(1, self._view_model.num_files - 1))

    def _on_button_pressed_adopt(self) -> None:
        self._controller.perform_adopt_annotation(self.adoption_index.value())

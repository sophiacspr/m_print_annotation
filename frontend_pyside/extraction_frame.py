from __future__ import annotations

from typing import Any

from PySide6.QtWidgets import QFileDialog, QFormLayout, QLineEdit, QPushButton, QVBoxLayout, QWidget

from controller.interfaces import IController
from viewmodel.extraction_frame_view_model import ExtractionFrameViewModel


class ExtractionFrame(QWidget):
    observer_id = "extraction"

    def __init__(self, parent: QWidget | None, controller: IController) -> None:
        super().__init__(parent)
        self._controller = controller
        self._view_model = ExtractionFrameViewModel(controller=controller, on_change=self._render_from_view_model, auto_register=False)
        self._controller.add_observer(self._view_model)
        self._render()

    def _render(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        form = QFormLayout()
        self.pdf_path_entry = QLineEdit()
        choose_button = QPushButton("Choose file")
        choose_button.clicked.connect(self._on_button_pressed_choose_file)
        self.page_range_entry = QLineEdit()
        self.page_range_entry.setPlaceholderText("e.g. 1-3, 5, 9-12")
        self.page_margins_entry = QLineEdit()
        self.page_margins_entry.setPlaceholderText("optional")
        form.addRow("PDF path", self.pdf_path_entry)
        form.addRow("", choose_button)
        form.addRow("Page ranges", self.page_range_entry)
        form.addRow("Page margins", self.page_margins_entry)
        layout.addLayout(form)
        self.button_extract = QPushButton("Extract pages")
        self.button_extract.clicked.connect(self._on_button_pressed_extract_pages)
        self.button_adopt_text = QPushButton("Adopt text")
        self.button_adopt_text.clicked.connect(self._on_button_pressed_adopt_text)
        layout.addWidget(self.button_extract)
        layout.addWidget(self.button_adopt_text)
        layout.addStretch(1)

    def _on_button_pressed_choose_file(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(self, "Select PDF file", "", "PDF Files (*.pdf);;All Files (*)")
        if file_path:
            self.pdf_path_entry.setText(file_path)

    def update(self, publisher: Any) -> None:
        self._view_model.update(publisher)

    def get_observer_id(self) -> str:
        return self._view_model.get_observer_id()

    def _render_from_view_model(self) -> None:
        self.pdf_path_entry.setText(self._view_model.file_path)

    def _on_button_pressed_extract_pages(self) -> None:
        self._view_model.extract_pages(self.pdf_path_entry.text(), self.page_range_entry.text(), self.page_margins_entry.text())

    def _on_button_pressed_adopt_text(self) -> None:
        self._view_model.adopt_text()

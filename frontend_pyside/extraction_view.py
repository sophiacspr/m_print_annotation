from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QSplitter, QVBoxLayout, QWidget

from controller.interfaces import IController
from frontend_pyside.base_view import ViewBehavior
from frontend_pyside.extraction_frame import ExtractionFrame
from frontend_pyside.meta_tags_frame import MetaTagsFrame
from frontend_pyside.preview_text_display import PreviewTextDisplayFrame
from frontend_pyside.search_frame import SearchFrame


class ExtractionView(QWidget):
    observer_id = "extraction_view"

    def __init__(self, parent: QWidget | None, controller: IController) -> None:
        super().__init__(parent)
        self._controller = controller
        self._view_id = "extraction"
        self._behavior = ViewBehavior(self, controller, self._view_id, self.observer_id)
        self._controller.register_view(self._view_id)
        self._render()

    def _render(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)

        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 0, 0)
        self.upper_frame = MetaTagsFrame(left, self._controller)
        self.lower_frame = PreviewTextDisplayFrame(left, self._controller, editable=True)
        self.search_frame = SearchFrame(left, self._controller, root_view_id=self._view_id)
        left_layout.addWidget(self.upper_frame, 0)
        left_layout.addWidget(self.lower_frame, 1)
        left_layout.addWidget(self.search_frame, 0)

        self.right_frame = ExtractionFrame(self, self._controller)
        splitter.addWidget(left)
        splitter.addWidget(self.right_frame)
        splitter.setStretchFactor(0, 6)
        splitter.setStretchFactor(1, 2)

    def enable_shortcuts(self) -> None:
        pass

    def disable_shortcuts(self) -> None:
        pass

    def get_view_id(self) -> str:
        return self._behavior.get_view_id()

    def get_observer_id(self) -> str:
        return self._behavior.get_observer_id()

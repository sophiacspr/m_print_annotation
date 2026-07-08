from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QPushButton, QSplitter, QVBoxLayout, QWidget

from controller.interfaces import IController
from frontend_pyside.annotation_menu import AnnotationMenuFrame
from frontend_pyside.base_view import ViewBehavior, configure_main_horizontal_splitter
from frontend_pyside.comparison_header_frame import ComparisonHeaderFrame
from frontend_pyside.comparison_text_displays import ComparisonTextDisplays
from frontend_pyside.search_frame import SearchFrame


class ComparisonView(QWidget):
    observer_id = "comparison_view"

    def __init__(self, parent: QWidget | None, controller: IController) -> None:
        super().__init__(parent)
        self._controller = controller
        self._view_id = "comparison"
        self._behavior = ViewBehavior(self, controller, self._view_id, self.observer_id)
        self._controller.register_view(self._view_id, self)
        self._text_displays: ComparisonTextDisplays | None = None
        self._render()

    def _render(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)

        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(8, 8, 8, 8)
        self.header_frame = ComparisonHeaderFrame(left, self._controller)
        self._text_displays = ComparisonTextDisplays(left, self._controller)
        self.search_frame = SearchFrame(left, self._controller, root_view_id=self._view_id)
        export_button = QPushButton("Export merged document")
        export_button.clicked.connect(self._controller.perform_export)
        left_layout.addWidget(self.header_frame, 0)
        left_layout.addWidget(self._text_displays, 1)
        left_layout.addWidget(self.search_frame, 0)
        left_layout.addWidget(export_button, 0)

        self.right_frame = AnnotationMenuFrame(self, self._controller, root_view_id=self._view_id)
        splitter.addWidget(left)
        splitter.addWidget(self.right_frame)
        configure_main_horizontal_splitter(splitter)

    def get_comparison_displays(self) -> list[QWidget]:
        return self._text_displays.get_displays() if self._text_displays is not None else []

    def enable_shortcuts(self) -> None:
        pass

    def disable_shortcuts(self) -> None:
        pass

    def get_view_id(self) -> str:
        return self._behavior.get_view_id()

    def get_observer_id(self) -> str:
        return self._behavior.get_observer_id()

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import QSplitter, QVBoxLayout, QWidget

from controller.interfaces import IController
from frontend_pyside.annotation_menu import AnnotationMenuFrame
from frontend_pyside.annotation_text_display import AnnotationTextDisplayFrame
from frontend_pyside.base_view import ViewBehavior, configure_main_horizontal_splitter
from frontend_pyside.meta_tags_frame import MetaTagsFrame
from frontend_pyside.search_frame import SearchFrame


class AnnotationView(QWidget):
    observer_id = "annotation_view"

    def __init__(self, parent: QWidget | None, controller: IController) -> None:
        super().__init__(parent)
        self._controller = controller
        self._view_id = "annotation"
        self._behavior = ViewBehavior(self, controller, self._view_id, self.observer_id)
        self._controller.register_view(self._view_id)
        self._shortcuts: list[QShortcut] = []
        self._render()

    def _render(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)

        left_splitter = QSplitter(Qt.Orientation.Vertical)
        self.upper_frame = MetaTagsFrame(left_splitter, self._controller)
        self.lower_frame = AnnotationTextDisplayFrame(left_splitter, self._controller, is_static_observer=True)
        search_wrapper = QWidget()
        search_layout = QVBoxLayout(search_wrapper)
        search_layout.setContentsMargins(8, 8, 8, 8)
        self.search_frame = SearchFrame(search_wrapper, self._controller, root_view_id=self._view_id)
        search_layout.addWidget(self.search_frame)
        left_splitter.addWidget(self.upper_frame)
        left_splitter.addWidget(self.lower_frame)
        left_splitter.addWidget(search_wrapper)
        left_splitter.setStretchFactor(0, 0)
        left_splitter.setStretchFactor(1, 4)
        left_splitter.setStretchFactor(2, 0)

        self._right_frame = AnnotationMenuFrame(self, self._controller, root_view_id=self._view_id)
        splitter.addWidget(left_splitter)
        splitter.addWidget(self._right_frame)
        configure_main_horizontal_splitter(splitter)

    def enable_shortcuts(self) -> None:
        if self._shortcuts:
            return
        for index in range(4):
            shortcut = QShortcut(QKeySequence(f"Ctrl+{index + 1}"), self)
            shortcut.activated.connect(lambda idx=index: self._right_frame.trigger_add_tag(idx))
            self._shortcuts.append(shortcut)

    def disable_shortcuts(self) -> None:
        for shortcut in self._shortcuts:
            shortcut.setParent(None)
        self._shortcuts.clear()

    def get_view_id(self) -> str:
        return self._behavior.get_view_id()

    def get_observer_id(self) -> str:
        return self._behavior.get_observer_id()

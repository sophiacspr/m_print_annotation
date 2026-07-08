from __future__ import annotations

from typing import Any

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from controller.interfaces import IController
from frontend_pyside.annotation_text_display import AnnotationTextDisplayFrame
from frontend_pyside.common import ScrollContainer
from viewmodel.comparison_text_displays_view_model import ComparisonTextDisplaysViewModel


class ComparisonTextDisplays(QWidget):
    observer_id = "comparison_text_displays"

    def __init__(self, parent: QWidget | None, controller: IController) -> None:
        super().__init__(parent)
        self._controller = controller
        self._view_model = ComparisonTextDisplaysViewModel(controller=controller, on_change=self._render_from_view_model, auto_register=False)
        self._controller.add_observer(self._view_model)
        self._num_comparison_displays = 0
        self._comparison_display_height = 8
        self._file_names: list[str] = []
        self._widget_structure: list[tuple[QLabel, AnnotationTextDisplayFrame]] = []
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self._scroll = ScrollContainer()
        layout.addWidget(self._scroll)

    def get_observer_id(self) -> str:
        return self._view_model.get_observer_id()

    def is_static_observer(self) -> bool:
        return self._view_model.is_static_observer()

    def update(self, publisher: Any) -> None:
        self._view_model.update(publisher)

    def finalize_view(self) -> None:
        self._view_model.finalize_view()

    def dispose(self) -> None:
        self._view_model.dispose()
        for _label, display in self._widget_structure:
            display.dispose()

    def _reset_widgets(self) -> None:
        for _label, display in self._widget_structure:
            display.dispose()
        self._scroll.clear()
        self._widget_structure = []
        for index in range(self._num_comparison_displays):
            label = QLabel("Original text:" if index == 0 else "Filename:")
            display = AnnotationTextDisplayFrame(self._scroll.content, self._controller, height=self._comparison_display_height)
            if index > 0:
                display.disable_selection()
            self._scroll.addWidget(label)
            self._scroll.addWidget(display)
            self._widget_structure.append((label, display))
        self._scroll.addStretch()

    def _render_from_view_model(self) -> None:
        if self._view_model.displays_changed:
            self._num_comparison_displays = self._view_model.num_comparison_displays
            self._reset_widgets()
        self._file_names = self._view_model.file_names
        for index, (file_name, (label, _display)) in enumerate(zip(self._file_names, self._widget_structure)):
            label.setText("Original text:" if index == 0 else f"Filename: {file_name}")

    def get_displays(self) -> list[QWidget]:
        return [display for _label, display in self._widget_structure]

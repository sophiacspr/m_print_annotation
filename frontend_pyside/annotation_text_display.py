from __future__ import annotations

from PySide6.QtWidgets import QVBoxLayout, QWidget

from controller.interfaces import IController
from frontend_pyside.highlight_renderer import PySideHighlightRenderer
from frontend_pyside.text_display_widget import TextDisplayWidget
from observer.interfaces import IPublisher
from viewmodel.annotation_text_display_view_model import AnnotationTextDisplayViewModel


class AnnotationTextDisplayFrame(QWidget):
    """Read-only text display for annotation mode, including tag/search highlights."""

    observer_id = "annotation_text_display"

    def __init__(
        self,
        parent: QWidget | None,
        controller: IController,
        is_static_observer: bool = False,
        height: int | None = None,
    ) -> None:
        super().__init__(parent)
        self._controller = controller
        self._view_model = AnnotationTextDisplayViewModel(
            controller=controller,
            is_static_observer=is_static_observer,
            on_change=self._render_from_view_model,
            auto_register=False,
        )

        self._highlight_renderer = PySideHighlightRenderer()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self._text_display = TextDisplayWidget(
            self,
            self._view_model,
            editable=False,
            height=height,
        )
        self.text_widget = self._text_display.text_widget
        layout.addWidget(self._text_display)
        if is_static_observer:
            self._controller.add_observer(self._view_model)

    def get_view_model(self) -> AnnotationTextDisplayViewModel:
        return self._view_model

    def dispose(self) -> None:
        self._view_model.dispose()

    def get_observer_id(self) -> str:
        return self._view_model.get_observer_id()

    def is_static_observer(self) -> bool:
        return self._view_model.is_static_observer()

    def update(self, publisher: IPublisher) -> None:
        self._view_model.update(publisher)

    def disable_selection(self) -> None:
        self._text_display.disable_selection()

    def _render_from_view_model(self) -> None:
        self._text_display.render_text(
            self._view_model.text,
            preserve_scroll=self._view_model.should_preserve_scroll,
        )
        self._apply_highlights(
            tag_highlight_data=self._view_model.tag_highlight_data,
            search_highlight_data=self._view_model.search_highlight_data,
        )

    def _apply_highlights(
        self,
        *,
        tag_highlight_data: list[tuple[str, str, int, int]],
        search_highlight_data: list[tuple[str, str, int, int]],
    ) -> None:
        """Applies highlights without writing formatting into the document text."""
        self._highlight_renderer.render(
            text_widget=self.text_widget,
            tag_highlight_data=tag_highlight_data,
            search_highlight_data=search_highlight_data,
        )
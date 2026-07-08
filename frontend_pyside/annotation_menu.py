from __future__ import annotations

from typing import Any

from PySide6.QtWidgets import QTabWidget, QVBoxLayout, QWidget

from controller.interfaces import IController
from frontend_pyside.annotation_tag_frame import AnnotationTagFrame
from frontend_pyside.common import ScrollContainer
from viewmodel.annotation_menu_view_model import AnnotationMenuViewModel


class AnnotationMenuFrame(QWidget):
    """Tabbed annotation menu generated from project template groups."""

    observer_id = "annotation_menu"

    def __init__(self, parent: QWidget | None, controller: IController, root_view_id: str) -> None:
        super().__init__(parent)
        self._controller = controller
        self._root_view_id = root_view_id
        self._view_model = AnnotationMenuViewModel(
            controller=controller,
            on_change=self._render_from_view_model,
            auto_register=False,
        )
        self._template_groups: list[dict[str, Any]] = []
        self._tag_frames: dict[str, AnnotationTagFrame] = {}
        self._tag_frames_list: list[AnnotationTagFrame] = []
        self._layout_rendered = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self._notebook = QTabWidget()
        layout.addWidget(self._notebook)

        self._controller.add_observer(self._view_model)

    def update(self, publisher: Any) -> None:
        self._view_model.update(publisher)

    def finalize_view(self) -> None:
        self._view_model.finalize_view()

    def finalize_observers(self) -> None:
        self._controller.add_observer(self._view_model)

    def get_observer_id(self) -> str:
        return self._view_model.get_observer_id()

    def trigger_add_tag(self, tag_type_index: int) -> None:
        self._tag_frames_list[tag_type_index].trigger_add_tag()

    def _render_layout(self) -> None:
        self._notebook.clear()
        self._tag_frames.clear()
        self._tag_frames_list.clear()

        for group in self._template_groups:
            group_name = str(group.get("group_name", "Group"))
            group_templates = group.get("templates", [])
            page = ScrollContainer()
            for template in group_templates:
                tag_type = template.get("type")
                if tag_type in self._tag_frames:
                    continue
                tag_frame = AnnotationTagFrame(page.content, self._controller, template, self._root_view_id)
                page.addWidget(tag_frame)
                self._tag_frames[tag_frame.get_name()] = tag_frame
                self._tag_frames_list.append(tag_frame)
            page.addStretch()
            self._notebook.addTab(page, group_name[:1].upper() + group_name[1:])
        self._layout_rendered = True

    def _ensure_layout(self) -> None:
        if not self._layout_rendered and self._template_groups:
            self._render_layout()

    def _render_from_view_model(self) -> None:
        if self._view_model.template_groups != self._template_groups:
            self._template_groups = self._view_model.template_groups
            self._layout_rendered = False
        self._ensure_layout()
        if not self._layout_rendered:
            return

        for tag_frame in self._tag_frames.values():
            tag_frame.set_selected_text(self._view_model.selected_text)

        for tag_type, tag_frame in self._tag_frames.items():
            tag_frame.set_attributes(self._view_model.suggestions.get(tag_type, {}))
            tag_frame.set_idref_list(self._view_model.idrefs_by_tag_type.get(tag_type, [""]))

        tag_type = self._view_model.current_db_search_tag_type
        if tag_type is not None and tag_type in self._tag_frames:
            self._tag_frames[tag_type].set_search_result(self._view_model.current_search_result)

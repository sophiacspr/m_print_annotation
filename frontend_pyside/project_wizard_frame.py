from __future__ import annotations

from typing import Any

from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from controller.interfaces import IController
from enums.menu_pages import MenuSubpage
from frontend_pyside.common import selected_list_indices, selected_list_items
from viewmodel.project_wizard_view_model import ProjectWizardViewModel


class NewProjectWizardFrame(QWidget):
    observer_id = "new_project_wizard"

    def __init__(
        self,
        controller: IController,
        parent_window: QWidget | None = None,
        master: QWidget | None = None,
        project_data: dict[str, Any] | None = None,
        register_as_observer: bool = True,
    ) -> None:
        super().__init__(master)
        self._parent_window = parent_window
        self._controller = controller
        self._view_model = ProjectWizardViewModel(controller=controller, on_change=self._render_from_view_model, auto_register=False)
        self._registered_as_observer = register_as_observer
        if register_as_observer:
            self._controller.add_observer(self._view_model)

        self._notebook = QTabWidget()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._notebook)

        self._init_page_project_name()
        self._init_page_tag_selection()
        self._init_page_tag_groups()
        if project_data:
            self.apply_state(project_data)
        self._notebook.setCurrentWidget(self._page_project_name)
        self._set_focus_on_default_widget()

    def _init_page_project_name(self) -> None:
        self._page_project_name = QWidget()
        layout = QVBoxLayout(self._page_project_name)
        layout.addWidget(QLabel("Project name"))
        self._entry_project_name = QLineEdit()
        layout.addWidget(self._entry_project_name)
        layout.addStretch(1)
        next_button = QPushButton("Next")
        next_button.clicked.connect(self._on_button_pressed_next_tab)
        layout.addWidget(next_button)
        self._notebook.addTab(self._page_project_name, "Project Name")

    def _init_page_tag_selection(self) -> None:
        self._page_tag_selection = QWidget()
        layout = QVBoxLayout(self._page_tag_selection)
        row = QHBoxLayout()
        left = QVBoxLayout()
        left.addWidget(QLabel("Available tags"))
        self._listbox_available_tags = QListWidget()
        self._listbox_available_tags.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        left.addWidget(self._listbox_available_tags)
        add_button = QPushButton("Add tags")
        add_button.clicked.connect(self._on_button_pressed_add_selected_tags)
        left.addWidget(add_button)
        right = QVBoxLayout()
        right.addWidget(QLabel("Selected tags"))
        self._listbox_selected_tags = QListWidget()
        self._listbox_selected_tags.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        right.addWidget(self._listbox_selected_tags)
        remove_button = QPushButton("Remove tags")
        remove_button.clicked.connect(self._on_button_pressed_remove_selected_tags)
        right.addWidget(remove_button)
        row.addLayout(left)
        row.addLayout(right)
        layout.addLayout(row, 1)
        nav = QHBoxLayout()
        back_button = QPushButton("Back")
        back_button.clicked.connect(self._on_button_pressed_previous_tab)
        next_button = QPushButton("Next")
        next_button.clicked.connect(self._on_button_pressed_next_tab)
        nav.addWidget(back_button)
        nav.addStretch(1)
        nav.addWidget(next_button)
        layout.addLayout(nav)
        self._notebook.addTab(self._page_tag_selection, "Select Tags")

    def _init_page_tag_groups(self) -> None:
        self._page_tag_groups = QWidget()
        layout = QVBoxLayout(self._page_tag_groups)
        self._entry_tag_group_file_name = QLineEdit()
        self._entry_tag_group_name = QLineEdit()
        layout.addWidget(QLabel("Tag group file name"))
        layout.addWidget(self._entry_tag_group_file_name)
        layout.addWidget(QLabel("Tag group name"))
        layout.addWidget(self._entry_tag_group_name)
        row = QHBoxLayout()
        left = QVBoxLayout()
        left.addWidget(QLabel("Select tags for group"))
        self._listbox_tags_for_group = QListWidget()
        self._listbox_tags_for_group.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        left.addWidget(self._listbox_tags_for_group)
        add_group_button = QPushButton("Add tag group")
        add_group_button.clicked.connect(self._on_button_pressed_add_tag_group)
        left.addWidget(add_group_button)
        right = QVBoxLayout()
        right.addWidget(QLabel("Created tag groups"))
        self._tree_created_groups = QTreeWidget()
        self._tree_created_groups.setHeaderHidden(True)
        right.addWidget(self._tree_created_groups)
        group_buttons = QHBoxLayout()
        tag_up = QPushButton("Tag up")
        tag_up.clicked.connect(self._on_button_pressed_tag_up)
        tag_down = QPushButton("Tag down")
        tag_down.clicked.connect(self._on_button_pressed_tag_down)
        delete_group = QPushButton("Delete tag group")
        delete_group.clicked.connect(self._on_button_pressed_delete_tag_group)
        group_buttons.addWidget(tag_up)
        group_buttons.addWidget(tag_down)
        group_buttons.addWidget(delete_group)
        right.addLayout(group_buttons)
        row.addLayout(left)
        row.addLayout(right)
        layout.addLayout(row, 1)
        nav = QHBoxLayout()
        back_button = QPushButton("Back")
        back_button.clicked.connect(self._on_button_pressed_previous_tab)
        self._finish_button = QPushButton("Finish")
        self._finish_button.clicked.connect(self._on_button_pressed_finish)
        nav.addWidget(back_button)
        nav.addStretch(1)
        nav.addWidget(self._finish_button)
        layout.addLayout(nav)
        self._notebook.addTab(self._page_tag_groups, "Tag Groups")

    def update(self, publisher: Any) -> None:
        self._view_model.update(publisher)

    def apply_state(self, state: dict[str, Any]) -> None:
        self._view_model.apply_state(state)
        self._render_from_view_model()

    def _render_from_view_model(self) -> None:
        state = self._view_model.project_data
        self._entry_project_name.setText(str(state.get("project_name", "")))
        self._populate_listbox(self._listbox_available_tags, state.get("locally_available_tags", []))
        self._populate_listbox(self._listbox_selected_tags, state.get("selected_tags", []))
        self._populate_listbox(self._listbox_tags_for_group, state.get("selected_tags", []))
        self._populate_tag_group_tree(state.get("tag_groups", {}))
        self._entry_tag_group_file_name.setText(str(state.get("tag_group_file_name", "")))

    def _populate_listbox(self, listbox: QListWidget, items: list[str]) -> None:
        listbox.clear()
        listbox.addItems([str(item) for item in items])

    def _populate_tag_group_tree(self, groups: dict[str, list[str]]) -> None:
        self._tree_created_groups.clear()
        for group_name, tag_list in groups.items():
            parent = QTreeWidgetItem([str(group_name)])
            for tag in tag_list:
                parent.addChild(QTreeWidgetItem([str(tag)]))
            self._tree_created_groups.addTopLevelItem(parent)
            parent.setExpanded(True)

    def _collect_current_page_data(self) -> dict[str, Any]:
        current = self._notebook.currentWidget()
        if current is self._page_project_name:
            return {"project_name": self._entry_project_name.text().strip()}
        if current is self._page_tag_selection:
            return {"selected_tags": [self._listbox_selected_tags.item(i).text() for i in range(self._listbox_selected_tags.count())]}
        if current is self._page_tag_groups:
            return {
                "tag_group_file_name": self._entry_tag_group_file_name.text().strip(),
                "tag_groups": self._build_tag_groups_from_tree(),
            }
        return {}

    def _on_button_pressed_add_tag_group(self) -> None:
        group_name = self._entry_tag_group_name.text().strip()
        if not group_name:
            QMessageBox.warning(self, "Error", "Tag group name cannot be empty.")
            return
        selected_tags = selected_list_items(self._listbox_tags_for_group)
        if not selected_tags:
            QMessageBox.warning(self, "Error", "No tags selected for the group.")
            return
        self._view_model.add_tag_group(self._entry_tag_group_file_name.text().strip(), {"name": group_name, "tags": selected_tags})

    def _on_button_pressed_delete_tag_group(self) -> None:
        item = self._tree_created_groups.currentItem()
        if item is None:
            QMessageBox.warning(self, "Error", "No tag group selected for deletion.")
            return
        if item.parent() is None:
            self._view_model.remove_tag_group(item.text(0))

    def _on_button_pressed_add_selected_tags(self) -> None:
        self._view_model.add_tags(selected_list_items(self._listbox_available_tags))

    def _on_button_pressed_remove_selected_tags(self) -> None:
        self._view_model.remove_tags(selected_list_indices(self._listbox_selected_tags))

    def _on_button_pressed_finish(self) -> None:
        self._view_model.update_project_data(self._collect_current_page_data())
        if self._view_model.create_new_project() and self._parent_window is not None:
            self._parent_window.close()

    def _on_button_pressed_next_tab(self) -> None:
        self._view_model.update_project_data(self._collect_current_page_data())
        self._notebook.setCurrentIndex(min(self._notebook.currentIndex() + 1, self._notebook.count() - 1))
        self._set_focus_on_default_widget()

    def _on_button_pressed_previous_tab(self) -> None:
        self._view_model.update_project_data(self._collect_current_page_data())
        self._notebook.setCurrentIndex(max(self._notebook.currentIndex() - 1, 0))
        self._set_focus_on_default_widget()

    def select_subtab(self, subtab: MenuSubpage) -> None:
        mapping = {
            MenuSubpage.PROJECT_NAME: self._page_project_name,
            MenuSubpage.PROJECT_TAGS: self._page_tag_selection,
            MenuSubpage.PROJECT_TAG_GROUPS: self._page_tag_groups,
        }
        widget = mapping.get(subtab)
        if widget is None:
            raise ValueError(f"Unknown subtab: {subtab}")
        self._notebook.setCurrentWidget(widget)
        self._set_focus_on_default_widget()

    def _set_focus_on_default_widget(self) -> None:
        current = self._notebook.currentWidget()
        if current is self._page_project_name:
            self._entry_project_name.setFocus()
        elif current is self._page_tag_selection:
            self._listbox_available_tags.setFocus()
        elif current is self._page_tag_groups:
            self._entry_tag_group_file_name.setFocus()

    def _build_tag_groups_from_tree(self) -> dict[str, list[str]]:
        groups: dict[str, list[str]] = {}
        for row in range(self._tree_created_groups.topLevelItemCount()):
            parent = self._tree_created_groups.topLevelItem(row)
            groups[parent.text(0)] = [parent.child(i).text(0) for i in range(parent.childCount())]
        return groups

    def _on_button_pressed_tag_up(self) -> None:
        self._move_selected_tag(-1)

    def _on_button_pressed_tag_down(self) -> None:
        self._move_selected_tag(1)

    def _move_selected_tag(self, direction: int) -> None:
        item = self._tree_created_groups.currentItem()
        if item is None or item.parent() is None:
            return
        parent = item.parent()
        index = parent.indexOfChild(item)
        new_index = index + direction
        if not 0 <= new_index < parent.childCount():
            return
        parent.takeChild(index)
        parent.insertChild(new_index, item)
        self._tree_created_groups.setCurrentItem(item)
        self._view_model.update_project_data({"tag_groups": self._build_tag_groups_from_tree()})

    def closeEvent(self, event) -> None:  # noqa: N802 - Qt API
        if self._registered_as_observer:
            self._view_model.dispose()
        super().closeEvent(event)

    def get_observer_id(self) -> str:
        return self._view_model.get_observer_id()

    def is_static_observer(self) -> bool:
        return self._view_model.is_static_observer()

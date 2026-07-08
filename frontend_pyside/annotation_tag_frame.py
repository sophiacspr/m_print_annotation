from __future__ import annotations

import uuid
from typing import Any

from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from controller.interfaces import IController
from frontend_pyside.common import SPACING, elide, set_combo_values


class AnnotationTagFrame(QGroupBox):
    """Dynamic tag form generated from one tag template."""

    def __init__(self, parent: QWidget | None, controller: IController, template: dict[str, Any], root_view_id: str) -> None:
        tag_name = template.get("type", "Tag")
        super().__init__(f"{str(tag_name).capitalize()} tag", parent)
        self._root_view_id = root_view_id
        self._controller = controller
        self._template = template
        self._name = str(template.get("type", "Tag"))
        self._data_widgets: dict[str, QLineEdit | QComboBox] = {}
        self._idref_widgets: list[QComboBox] = []
        self._idref_attributes: dict[str, QComboBox] = {}
        self._current_search_result: Any = None
        self._db_id: str | None = None
        self._selected_text_entry: QLineEdit | None = None
        self._output_widget: QLineEdit | None = None
        self._display_widget: QComboBox | None = None
        self.edit_id_combobox: QComboBox | None = None
        self.delete_id_combobox: QComboBox | None = None
        self._render()

    def _render(self) -> None:
        outer = QVBoxLayout(self)
        outer.setSpacing(SPACING)

        is_db = bool(self._template.get("has_database", False))
        if is_db:
            self._db_id = uuid.uuid4().hex
            button_row = QHBoxLayout()
            start_button = QPushButton(f"Start {self._name} annotation")
            start_button.clicked.connect(self._on_button_pressed_start_db_annotation)
            start_button.setToolTip(f"Sequentially suggests all {self._name} expressions found in the text.")
            end_button = QPushButton(f"End {self._name} annotation")
            end_button.clicked.connect(self._on_button_pressed_end_db_annotation)
            end_button.setToolTip(f"Ends the {self._name} annotation mode.")
            button_row.addWidget(start_button)
            button_row.addWidget(end_button)
            outer.addLayout(button_row)

            navigation_row = QHBoxLayout()
            previous_button = QPushButton("Previous")
            previous_button.clicked.connect(self._on_button_pressed_previous_db_suggestion_button)
            next_button = QPushButton("Next")
            next_button.clicked.connect(self._on_button_pressed_next_db_suggestion_button)
            navigation_row.addWidget(previous_button)
            navigation_row.addWidget(next_button)
            outer.addLayout(navigation_row)

        form = QFormLayout()
        self._selected_text_entry = QLineEdit()
        self._selected_text_entry.setReadOnly(True)
        form.addRow("Selected text", self._selected_text_entry)

        for attribute_name, attribute_data in self._template.get("attributes", {}).items():
            attribute_type = str(attribute_data.get("type", "CDATA")).upper()
            widget: QLineEdit | QComboBox
            field_name = attribute_name

            if attribute_type in {"CDATA", "ID", "UNION"}:
                widget = QLineEdit()
            elif attribute_type == "OUTPUT":
                widget = QLineEdit()
                widget.setReadOnly(True)
                self._output_widget = widget
            elif attribute_type == "DISPLAY":
                widget = QComboBox()
                self._display_widget = widget
                widget.currentTextChanged.connect(lambda _text: self._update_output_widget())
            else:
                widget = QComboBox()
                allowed_values = [""] + [str(value) for value in attribute_data.get("allowedValues", [])]
                widget.addItems(allowed_values)
                default = attribute_data.get("default")
                if default is not None:
                    index = widget.findText(str(default))
                    if index >= 0:
                        widget.setCurrentIndex(index)

            if attribute_type == "ID":
                field_name = "id"
            if attribute_type != "DISPLAY":
                self._data_widgets[field_name] = widget
            if attribute_type == "IDREF" and isinstance(widget, QComboBox):
                self._idref_attributes[field_name] = widget
                self._idref_widgets.append(widget)

            form.addRow(str(attribute_name), widget)
        outer.addLayout(form)

        add_button = QPushButton("Add tag")
        add_button.clicked.connect(self._on_button_pressed_add_tag)
        outer.addWidget(add_button)

        if not is_db:
            edit_row = QHBoxLayout()
            self.edit_id_combobox = QComboBox()
            self.edit_id_combobox.addItem("")
            self._idref_widgets.append(self.edit_id_combobox)
            edit_button = QPushButton("Edit tag")
            edit_button.clicked.connect(self._on_button_pressed_edit_tag)
            edit_row.addWidget(QLabel("ID to edit"))
            edit_row.addWidget(self.edit_id_combobox)
            edit_row.addWidget(edit_button)
            outer.addLayout(edit_row)

        delete_row = QHBoxLayout()
        self.delete_id_combobox = QComboBox()
        self.delete_id_combobox.addItem("")
        self._idref_widgets.append(self.delete_id_combobox)
        delete_button = QPushButton("Delete tag")
        delete_button.clicked.connect(self._on_button_pressed_delete_tag)
        delete_row.addWidget(QLabel("ID to delete"))
        delete_row.addWidget(self.delete_id_combobox)
        delete_row.addWidget(delete_button)
        outer.addLayout(delete_row)

    def get_name(self) -> str:
        return self._name

    def set_selected_text(self, text: str) -> None:
        if self._selected_text_entry is not None:
            self._selected_text_entry.setText(elide(text or "", 50))

    def set_attributes(self, attribute_data: dict[str, str]) -> None:
        for widget in self._data_widgets.values():
            self._set_widget_text(widget, "")
        for attribute_name, attribute_value in attribute_data.items():
            widget = self._data_widgets.get(attribute_name)
            if widget is not None:
                self._set_widget_text(widget, str(attribute_value))

    def set_idref_list(self, idrefs: list[str]) -> None:
        for widget in self._idref_widgets:
            set_combo_values(widget, idrefs)

    def set_search_result(self, search_result: Any) -> None:
        self._current_search_result = search_result
        display_values = search_result.get_display_list() if search_result else []
        if self._display_widget is not None:
            set_combo_values(self._display_widget, display_values)
            if display_values:
                self._display_widget.setCurrentIndex(0)
            self._update_output_widget()

    def trigger_add_tag(self) -> None:
        self._on_button_pressed_add_tag()

    def _collect_tag_data(self) -> dict[str, Any]:
        selected_text_data = self._controller.get_selected_text_data()
        selected_text = selected_text_data["selected_text"]
        position = selected_text_data["position"]
        if not selected_text:
            raise ValueError("No text is currently selected.")

        attributes = {
            attribute_name: self._get_widget_text(widget).strip()
            for attribute_name, widget in self._data_widgets.items()
            if self._get_widget_text(widget).strip()
        }
        references = {
            attribute_name: self._get_widget_text(widget).strip()
            for attribute_name, widget in self._idref_attributes.items()
            if self._get_widget_text(widget).strip()
        }
        return {
            "tag_type": self._template.get("type", "Tag"),
            "attributes": attributes,
            "position": position,
            "text": selected_text,
            "references": references,
        }

    def _on_button_pressed_add_tag(self) -> None:
        self._controller.perform_add_tag(self._collect_tag_data(), caller_id=self._root_view_id)

    def _on_button_pressed_edit_tag(self) -> None:
        if self.edit_id_combobox is None:
            return
        self._controller.perform_edit_tag(
            tag_id=self.edit_id_combobox.currentText(),
            tag_data=self._collect_tag_data(),
            caller_id=self._root_view_id,
        )

    def _on_button_pressed_delete_tag(self) -> None:
        if self.delete_id_combobox is None:
            return
        self._controller.perform_delete_tag(tag_id=self.delete_id_combobox.currentText(), caller_id=self._root_view_id)

    def _on_button_pressed_start_db_annotation(self) -> None:
        self._controller.perform_start_db_search(tag_type=self._name, caller_mode=self._root_view_id, caller_id=self._db_id or "")

    def _on_button_pressed_end_db_annotation(self) -> None:
        self._controller.perform_end_search()

    def _on_button_pressed_previous_db_suggestion_button(self) -> None:
        self._controller.perform_previous_suggestion(caller_id=self._db_id)

    def _on_button_pressed_next_db_suggestion_button(self) -> None:
        self._controller.perform_next_suggestion(caller_id=self._db_id)

    def _on_button_pressed_mark_wrong_db_suggestion(self) -> None:
        self._controller.perform_mark_wrong_db_suggestion(tag_type=self._name)

    def _update_output_widget(self) -> None:
        if self._output_widget is None:
            return
        output_value = ""
        if self._current_search_result is not None and self._display_widget is not None:
            output_value = self._current_search_result.get_output_for_display(self._display_widget.currentText()) or ""
        self._output_widget.setText(str(output_value))

    def _get_widget_text(self, widget: QLineEdit | QComboBox) -> str:
        return widget.currentText() if isinstance(widget, QComboBox) else widget.text()

    def _set_widget_text(self, widget: QLineEdit | QComboBox, text: str) -> None:
        if isinstance(widget, QComboBox):
            index = widget.findText(text)
            if index < 0:
                widget.addItem(text)
                index = widget.findText(text)
            widget.setCurrentIndex(index)
        else:
            widget.setText(text)

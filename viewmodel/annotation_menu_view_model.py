from __future__ import annotations

from typing import Any, Callable

from viewmodel.base_view_model import BaseObserverViewModel
from viewmodel.ports import ObserverStatePort


class AnnotationMenuViewModel(BaseObserverViewModel):
    """Framework-independent state for the annotation menu.

    Data contracts:
    - template_groups: list[dict[str, Any]]
    - selected_text: str
    - suggestions: dict[str, dict[str, str]]
      Maps tag type -> attribute name -> suggested value. This mirrors the
      existing AnnotationTagFrame.set_attributes(attribute_data) contract.
    - idrefs_by_tag_type: dict[str, list[str]]
      Maps tag type -> combobox values. The empty string is always included.
    """

    observer_id = "annotation_menu"

    def __init__(
        self,
        controller: ObserverStatePort,
        on_change: Callable[[], None] | None = None,
        auto_register: bool = True,
    ) -> None:
        super().__init__(controller, self.observer_id, False, on_change, auto_register)
        self.template_groups: list[dict[str, Any]] = []
        self.selected_text: str = ""
        self.suggestions: dict[str, dict[str, str]] = {}
        self.idrefs_by_tag_type: dict[str, list[str]] = {}
        self.current_search_result: Any = None
        self.current_db_search_tag_type: str | None = None

    def apply_state(self, state: dict[str, Any], publisher: Any = None) -> None:
        if "template_groups" in state:
            self.template_groups = self._require_template_groups(state["template_groups"])
        if "selected_text" in state:
            self.selected_text = str(state["selected_text"] or "")
        if "suggestions" in state:
            self.suggestions = self._require_suggestions(state.get("suggestions", {}))
        if "tags" in state:
            self.idrefs_by_tag_type = self._build_idrefs_by_tag_type(state.get("tags", []))
        if "current_search_result" in state:
            self._apply_search_result(state["current_search_result"])

    def _require_template_groups(self, value: Any) -> list[dict[str, Any]]:
        if not isinstance(value, list):
            raise TypeError(
                f"template_groups must be list[dict[str, Any]], got {type(value).__name__}"
            )
        for index, group in enumerate(value):
            if not isinstance(group, dict):
                raise TypeError(
                    f"template_groups[{index}] must be dict[str, Any], got {type(group).__name__}"
                )
        return value

    def _require_suggestions(self, value: Any) -> dict[str, dict[str, str]]:
        """Validate suggestions as tag_type -> attribute_name -> value.

        This intentionally rejects list values. Lists would mean multiple
        alternative suggestions per tag type, but the current Tkinter form has no
        selection UI for alternatives. The old form contract is one dictionary
        per tag type.
        """
        if value is None:
            return {}
        if not isinstance(value, dict):
            raise TypeError(
                f"suggestions must be dict[str, dict[str, str]], got {type(value).__name__}"
            )

        validated: dict[str, dict[str, str]] = {}
        for tag_type, attributes in value.items():
            if not isinstance(tag_type, str):
                raise TypeError(
                    f"suggestion tag type keys must be str, got {type(tag_type).__name__}"
                )
            if attributes is None:
                validated[tag_type] = {}
                continue
            if not isinstance(attributes, dict):
                raise TypeError(
                    f"suggestions[{tag_type!r}] must be dict[str, str], got {type(attributes).__name__}"
                )
            validated[tag_type] = {
                str(attribute_name): str(attribute_value)
                for attribute_name, attribute_value in attributes.items()
                if attribute_value is not None
            }
        return validated

    def _build_idrefs_by_tag_type(self, tags: Any) -> dict[str, list[str]]:
        if tags is None:
            return {}
        if not isinstance(tags, list):
            raise TypeError(f"tags must be list, got {type(tags).__name__}")

        idrefs_by_tag_type: dict[str, list[str]] = {}
        for tag in tags:
            tag_type = tag.get_tag_type()
            tag_id = tag.get_id()
            idrefs_by_tag_type.setdefault(tag_type, [""])
            if tag_id not in idrefs_by_tag_type[tag_type]:
                idrefs_by_tag_type[tag_type].append(tag_id)
        return idrefs_by_tag_type

    def _apply_search_result(self, search_result: Any) -> None:
        self.current_search_result = search_result
        search_type = getattr(search_result, "search_type", None)
        search_type_name = getattr(search_type, "name", str(search_type))
        if search_type_name == "DB" or str(search_type).endswith("DB"):
            self.current_db_search_tag_type = getattr(search_result, "tag_type", None)
        else:
            self.current_db_search_tag_type = None

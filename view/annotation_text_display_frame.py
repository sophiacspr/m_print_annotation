import tkinter as tk
from typing import List, Tuple

from controller.interfaces import IController
from model.highlight_model import HighlightModel
from observer.interfaces import IPublisher
from view.text_display_frame import TextDisplayFrame


class AnnotationTextDisplayFrame(tk.Frame):
    """
    A specialized annotation text display that composes TextDisplayFrame.
    """

    observer_id: str = "annotation_text_display"

    def __init__(
        self,
        parent: tk.Widget,
        controller: IController,
        is_static_observer: bool = False,
        height: int = None,
    ) -> None:
        super().__init__(parent)
        self._controller: IController = controller
        self._is_static_observer: bool = is_static_observer

        self._text_display = TextDisplayFrame(
            parent=self,
            controller=controller,
            editable=False,
            is_static_observer=False,
            height=height,
        )
        self._text_display.pack(fill=tk.BOTH, expand=True)
        self.text_widget = self._text_display.text_widget

        if is_static_observer:
            self._controller.add_observer(self)

    def get_observer_id(self) -> str:
        """
        Returns the stable observer identifier used by the source mapping.

        Returns:
            str: The observer identifier.
        """
        return self.observer_id

    def update(self, publisher: IPublisher) -> None:
        """
        Updates the displayed text and refreshes text highlighting.

        Args:
            publisher (IPublisher): The publisher that triggered the update.
        """
        self._text_display.update_for_observer(observer=self, publisher=publisher)

        if isinstance(publisher, HighlightModel):
            highlight_data = self._controller.get_observer_state(self, publisher)

            self.unhighlight_text()
            self._apply_highlights(
                highlight_data.get("tag_highlight_data", []), prefix="tag"
            )
            self._apply_highlights(
                highlight_data.get("search_highlight_data", []), prefix="search"
            )

    def disable_selection(self) -> None:
        """
        Disables selection in the composed text display.
        """
        self._text_display.disable_selection()

    def is_static_observer(self) -> bool:
        """
        Checks whether this view is a static observer.

        Returns:
            bool: True if this view is static, False otherwise.
        """
        return self._is_static_observer

    def _apply_highlights(
        self, highlight_data: List[Tuple[str, str, int, int]], prefix: str
    ) -> None:
        """
        Applies text highlighting based on the provided highlight data.

        Args:
            highlight_data (List[Tuple[str, str, int, int]]): Highlight tuples containing
                background color, font color, start position, and end position.
            prefix (str): A prefix to differentiate highlight types.
        """
        for bg_color, font_color, start, end in highlight_data:
            tag_name = f"highlight_{prefix}_{bg_color}"
            self.text_widget.tag_configure(
                tag_name, background=bg_color, foreground=font_color
            )
            start_index = f"1.0+{start}c"
            end_index = f"1.0+{end}c"
            self.text_widget.tag_add(tag_name, start_index, end_index)
            if prefix == "search":
                self.text_widget.tag_raise(tag_name)
            else:
                self.text_widget.tag_lower(tag_name)

    def unhighlight_text(self) -> None:
        """
        Removes all existing text highlights.
        """
        for tag in self.text_widget.tag_names():
            if tag.startswith("highlight_"):
                self.text_widget.tag_remove(tag, "1.0", "end")

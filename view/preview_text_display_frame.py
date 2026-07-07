import tkinter as tk

from controller.interfaces import IController
from observer.interfaces import IPublisher
from view.text_display_frame import TextDisplayFrame
from viewmodel.preview_text_display_view_model import PreviewTextDisplayViewModel


class PreviewTextDisplayFrame(tk.Frame):
    """
    A specialized preview text display that composes TextDisplayFrame.
    """

    observer_id: str = "preview_text_display"

    def __init__(
        self,
        parent: tk.Widget,
        controller: IController,
        editable: bool = True,
    ) -> None:
        super().__init__(parent)
        self._controller: IController = controller
        self._view_model = PreviewTextDisplayViewModel(
            controller=controller,
            on_change=self._render_from_view_model,
            auto_register=False,
        )

        self._text_display = TextDisplayFrame(
            parent=self,
            controller=controller,
            editable=editable,
            is_static_observer=False,
        )
        self._text_display.pack(fill=tk.BOTH, expand=True)
        self.text_widget = self._text_display.text_widget

        self._controller.add_observer(self._view_model)

    def get_view_model(self):
        """Returns the framework-independent view model owned by this view."""
        return self._view_model

    def dispose(self) -> None:
        """Deregisters this view's view model from the controller."""
        self._view_model.dispose()

    def get_observer_id(self) -> str:
        """
        Returns the stable observer identifier used by the source mapping.

        Returns:
            str: The observer identifier.
        """
        return self._view_model.get_observer_id()

    def update(self, publisher: IPublisher) -> None:
        """
        Updates the preview text display.

        Args:
            publisher (IPublisher): The publisher that triggered the update.
        """
        self._view_model.update(publisher)

    def disable_selection(self) -> None:
        """
        Disables selection in the composed text display.
        """
        self._text_display.disable_selection()

    def _render_from_view_model(self) -> None:
        """Renders the current view-model state."""
        self._text_display.render_text(self._view_model.text)

    def is_static_observer(self) -> bool:
        """
        Checks whether this view is a static observer.

        Returns:
            bool: Always True for the preview text display.
        """
        return self._view_model.is_static_observer()

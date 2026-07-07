import tkinter as tk
from typing import Any

from controller.interfaces import IController
from model.interfaces import IDocumentModel
from observer.interfaces import IPublisher


class TextDisplayFrame(tk.Frame):
    """
    A reusable Tkinter frame that displays text and owns the concrete text widget.

    This class is now a composable UI component. Specialized views should contain a
    TextDisplayFrame instance instead of inheriting from it.
    """

    observer_id: str = "text_display"
    DEBOUNCE_DELAY = 300  # milliseconds

    def __init__(
        self,
        parent: tk.Widget,
        controller: IController,
        editable: bool = False,
        is_static_observer: bool = False,
        height: int = None,
    ) -> None:
        """
        Initializes the TextDisplayFrame with a text widget and scrollbar.

        Args:
            parent (tk.Widget): The parent tkinter container for this frame.
            controller (IController): The controller managing interactions.
            editable (bool, optional): Whether the text can be edited. Defaults to False.
            is_static_observer (bool, optional): Whether this component should register itself
                as an observer. Specialized wrapper views should normally pass False and
                register the wrapper instead. Defaults to False.
            height (int, optional): The text widget height. Defaults to None.
        """
        super().__init__(parent)

        self._controller: IController = controller
        self.text_widget: tk.Text = None
        self._editable: bool = editable

        self._debounce_job = None
        self._is_typing = False
        self._internal_update = False
        self._cursor_position: str = None
        self._is_static_observer: bool = is_static_observer
        self._height = height

        self._render()

        if is_static_observer:
            self._controller.add_observer(self)

    def get_observer_id(self) -> str:
        """
        Returns the stable observer identifier used by the source mapping.

        Returns:
            str: The observer identifier.
        """
        return self.observer_id

    def _render(self) -> None:
        """
        Sets up and arranges the text widget and scrollbar within the frame.
        """
        scrollbar = tk.Scrollbar(self, orient="vertical")

        self.text_widget = tk.Text(
            self, wrap="word", yscrollcommand=scrollbar.set, state="disabled"
        )
        scrollbar.config(command=self.text_widget.yview)

        if self._editable:
            self.text_widget.config(state="normal")
            self.text_widget.bind("<KeyRelease>", self._on_text_change)

        self.text_widget.bind("<ButtonRelease-1>", self._on_selection)

        if self._height is not None:
            self.text_widget.config(height=self._height)

        self.text_widget.pack(
            side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=(5, 5)
        )
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def _on_selection(self, event: tk.Event) -> None:
        """
        Handles text selection events and forwards the selection to the controller.

        Args:
            event (tk.Event): The event triggered by text selection.
        """
        try:
            selected_text = self.text_widget.selection_get()
            start_index = self.text_widget.index(tk.SEL_FIRST)
            line, col = map(int, start_index.split("."))

            lines_before = sum(
                len(self.text_widget.get(f"{i}.0", f"{i}.end")) + 1
                for i in range(1, line)
            )
            start_position = lines_before + col

            selection_data = {
                "position": start_position,
                "selected_text": selected_text,
            }
            self._controller.perform_text_selected(selection_data)
        except tk.TclError:
            pass

    def _on_text_change(self, event: tk.Event) -> None:
        """
        Handles text change events to implement debouncing and optimistic updates.

        Args:
            event (tk.Event): The event triggered by text input.
        """
        if self._debounce_job:
            self.after_cancel(self._debounce_job)

        self._is_typing = True

        new_text = self.text_widget.get("1.0", tk.END).strip()
        self._controller.perform_update_preview_text(new_text)

        self._cursor_position = self.text_widget.index(tk.INSERT)
        self._debounce_job = self.after(self.DEBOUNCE_DELAY, self._finalize_update)

    def _finalize_update(self) -> None:
        """
        Finalizes updates to the model after debouncing.
        """
        self._is_typing = False
        new_text = self.text_widget.get("1.0", tk.END).strip()
        self._controller.perform_update_preview_text(new_text)
        self._debounce_job = None

    def disable_selection(self) -> None:
        """
        Disables text selection in the text widget.
        """
        self.text_widget.bind("<Button-1>", lambda e: "break")
        self.text_widget.bind("<B1-Motion>", lambda e: "break")
        self.text_widget.bind("<Double-1>", lambda e: "break")
        self.text_widget.bind("<Triple-1>", lambda e: "break")

    def update(self, publisher: IPublisher) -> None:
        """
        Observer-compatible update method for direct TextDisplayFrame usage.

        Args:
            publisher (IPublisher): The publisher that triggered the update.
        """
        self.update_for_observer(observer=self, publisher=publisher)

    def update_for_observer(self, observer: Any, publisher: IPublisher) -> None:
        """
        Updates the displayed text using state resolved for the provided observer.

        Args:
            observer (Any): The registered observer whose source-mapping state should be used.
            publisher (IPublisher): The publisher that triggered the update.
        """
        if self._is_typing:
            return

        if not isinstance(publisher, IDocumentModel):
            return

        self._internal_update = True

        text = self._controller.get_observer_state(observer, publisher).get(
            "text", "NOTEXT"
        )

        self.text_widget.config(state="normal")
        self.text_widget.delete("1.0", tk.END)
        self.text_widget.insert("1.0", text)
        self.text_widget.update_idletasks()
        self.text_widget.update()

        if self._cursor_position:
            self.text_widget.mark_set(tk.INSERT, self._cursor_position)

        if not self._editable:
            self.text_widget.config(state="disabled")

        self._cursor_position = None
        self._internal_update = False

    def is_static_observer(self) -> bool:
        """
        Checks whether this component is registered as a static observer.

        Returns:
            bool: True if this component is static, False otherwise.
        """
        return self._is_static_observer

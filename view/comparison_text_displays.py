import tkinter as tk
from tkinter import ttk
from typing import List

from controller.interfaces import IController
from observer.interfaces import IPublisher
from view.annotation_text_display_frame import AnnotationTextDisplayFrame


class ComparisonTextDisplays(tk.Frame):
    """
    Displays the comparison text widgets and observes comparison layout changes.
    """

    observer_id: str = "comparison_text_displays"

    def __init__(self, parent: tk.Widget, controller: IController) -> None:
        """
        Initializes the ComparisonTextDisplays with a reference to the parent widget and controller.

        Args:
            parent (tk.Widget): The parent widget where this frame will be placed.
            controller (IController): The controller managing actions for this view.
        """
        super().__init__(parent)
        self._controller: IController = controller

        self._num_comparison_displays: int = 0
        self._comparison_display_height = 8
        self._file_names: List[str] = []
        self._widget_structure: List[tuple[tk.Widget, AnnotationTextDisplayFrame]] = []
        self._is_static_observer: bool = False

        self._controller.add_observer(self)

        canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        self.scrollable_frame = tk.Frame(canvas)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
        )
        canvas.bind(
            "<Configure>",
            lambda e: canvas.itemconfig(
                "scrollable_window", width=canvas.winfo_width()
            ),
        )
        canvas.create_window(
            (0, 0), window=self.scrollable_frame, anchor="nw", tags="scrollable_window"
        )

        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def get_observer_id(self) -> str:
        """
        Returns the stable observer identifier used by the source mapping.

        Returns:
            str: The observer identifier.
        """
        return self.observer_id

    def is_static_observer(self) -> bool:
        """
        Checks whether this view is a static observer.

        Returns:
            bool: False for this dynamic comparison display container.
        """
        return self._is_static_observer

    def _render(self) -> None:
        """
        Clears all existing widgets and updates the layout with the new ones.
        """
        for index, (label, text_display_frame) in enumerate(self._widget_structure):
            row = index * 2
            label.grid(row=row, column=0, sticky="w", pady=(2, 0))
            text_display_frame.grid(row=row + 1, column=0, sticky="ew", pady=(0, 0))
            text_display_frame.grid_propagate(False)

        self.scrollable_frame.grid_columnconfigure(0, weight=1)

        for i in range(len(self._widget_structure) * 2):
            self.scrollable_frame.grid_rowconfigure(i, weight=0)

    def _reset_widgets(self) -> None:
        """
        Clears existing widgets, deregisters observers, and recreates the layout.
        """
        for widget in self.scrollable_frame.winfo_children():
            if isinstance(widget, AnnotationTextDisplayFrame):
                self._controller.remove_observer(widget)
            widget.destroy()

        self._widget_structure = []

        for index in range(self._num_comparison_displays):
            text_display_frame = AnnotationTextDisplayFrame(
                parent=self.scrollable_frame,
                controller=self._controller,
                height=self._comparison_display_height,
            )
            text_display_frame.grid_propagate(False)
            if index > 0:
                text_display_frame.disable_selection()
            self._widget_structure.append(
                (tk.Label(self.scrollable_frame), text_display_frame)
            )

    def update(self, publisher: IPublisher) -> None:
        """
        Retrieves updated data and layout information from the controller.

        Args:
            publisher (IPublisher): The publisher that triggered the update.
        """
        state = self._controller.get_observer_state(self, publisher)

        if "num_comparison_displays" in state:
            new_num = state["num_comparison_displays"]
            if new_num != self._num_comparison_displays:
                self._num_comparison_displays = new_num
                self._reset_widgets()
                self._render()

        if "file_names" in state:
            self._file_names = state["file_names"]
            for index, (file_name, (label, _)) in enumerate(
                zip(self._file_names, self._widget_structure)
            ):
                if index == 0:
                    label.config(text="Original Text:")
                else:
                    label.config(text=f"Filename: {file_name}")

    def finalize_view(self) -> None:
        """
        Retrieves the layout state and updates the file names before rendering the view.
        """
        layout = self._controller.get_observer_state(self)
        self._file_names = layout["file_names"]
        self._render()

    def get_displays(self) -> List[tk.Widget]:
        """
        Returns all text display widgets.

        Returns:
            List[tk.Widget]: The display widgets.
        """
        return [widget for _, widget in self._widget_structure]

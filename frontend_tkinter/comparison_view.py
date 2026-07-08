from typing import List
import tkinter as tk
from tkinter import ttk

from controller.interfaces import IController
from frontend_tkinter.annotation_menu_frame import AnnotationMenuFrame
from frontend_tkinter.comparison_header_frame import ComparisonHeaderFrame
from frontend_tkinter.comparison_text_displays import ComparisonTextDisplays
from frontend_tkinter.interfaces import IComparisonView
from frontend_tkinter.view import ViewBehavior


class ComparisonView(tk.Frame, IComparisonView):
    """
    Top-level comparison view.

    This class keeps the required Tkinter frame inheritance, but uses composition
    for shared project-specific view behavior instead of inheriting from View.
    """

    observer_id: str = "comparison_view"

    def __init__(self, parent: tk.Widget, controller: IController) -> None:
        """
        Initializes the ComparisonView with a reference to the parent widget and controller.

        Args:
            parent (tk.Widget): The parent widget where this frame will be placed.
            controller (IController): The controller managing actions for this view.
        """
        super().__init__(parent)

        self._controller: IController = controller
        self._view_id: str = "comparison"
        self._view_behavior = ViewBehavior(
            owner=self,
            controller=self._controller,
            view_id=self._view_id,
            observer_id=self.observer_id,
        )

        self._controller.register_view(view_id=self._view_id, view=self)
        self._text_displays: ComparisonTextDisplays | None = None
        self._render()

    def _render(self) -> None:
        """
        Sets up the layout for the ComparisonView.
        """
        # Create the main horizontal PanedWindow for the layout
        self.paned_window = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True)

        # Center frame containing upper and lower frames for text and metadata display
        self.left_frame = tk.Frame(self.paned_window)

        header_frame = ComparisonHeaderFrame(
            self.left_frame, controller=self._controller)
        header_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        self._text_displays = ComparisonTextDisplays(
            self.left_frame, self._controller)
        self._text_displays.pack(side=tk.TOP, fill=tk.BOTH,
                                 expand=True, padx=10, pady=5)

        # Frame containing the export button
        self.export_frame = tk.Frame(self.left_frame)
        self.export_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        # Export button placed on the left side
        self.export_button = tk.Button(
            self.export_frame,
            text="Export Merged Document",
            command=self._controller.perform_export
        )
        self.export_button.pack(side=tk.LEFT)

        # Now pack left_frame itself in the paned_window
        self.left_frame.pack(fill="both", expand=True)

        # Right frame for the tagging menu
        self.right_frame = AnnotationMenuFrame(
            self, controller=self._controller, root_view_id=self._view_id)

        # Add frames to the PanedWindow with weights
        self.paned_window.add(self.left_frame, weight=6)
        self.paned_window.add(self.right_frame, weight=1)

        # Set initial sash positions
        self.old_sash = self.paned_window.sashpos(0)

    def get_comparison_displays(self) -> List[tk.Widget]:
        """
        Returns a list of all text display widgets managed by this view.

        Returns:
            List[tk.Widget]: A list of widgets representing the text displays.
        """
        if self._text_displays is None:
            return []
        return self._text_displays.get_displays()

    def enable_shortcuts(self) -> None:
        """
        Enables shortcuts.
        """
        pass

    def disable_shortcuts(self) -> None:
        """
        Disables shortcuts.
        """
        pass

    def get_view_id(self) -> str | None:
        """
        Returns the logical view identifier.

        Returns:
            str | None: The logical view identifier.
        """
        return self._view_behavior.get_view_id()

    def get_observer_id(self) -> str:
        """
        Returns the stable observer identifier used by the source mapping.

        Returns:
            str: The observer identifier.
        """
        return self._view_behavior.get_observer_id()

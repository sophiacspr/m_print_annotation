import tkinter as tk
from tkinter import ttk
from controller.interfaces import IController
from view.annotation_text_display_frame import AnnotationTextDisplayFrame
from view.meta_tags_frame import MetaTagsFrame
from view.annotation_menu_frame import AnnotationMenuFrame
from view.search_frame import SearchFrame
from view.view import View


class AnnotationView(View):
    def __init__(self, parent: tk.Widget, controller: IController) -> None:
        """
        Initializes the AnnotationView with a reference to the parent widget and controller.

        Args:
            parent (tk.Widget): The parent widget where this frame will be placed.
            controller (IController): The controller managing actions for this view.
        """
        super().__init__(parent, controller)
        self._view_id = "annotation"
        self._controller.register_view(self._view_id)
        self._render()

    def _render(self) -> None:
        """
        Sets up the layout for the AnnotationView, allowing resizing between 
        the text display frames on the left, a center frame, and the tagging menu frame on the right.
        """
        # Create the main horizontal PanedWindow for the layout
        self.paned_window = ttk.PanedWindow(
            self, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True)

        # Left frame with another vertical PanedWindow
        self._left_paned = ttk.PanedWindow(
            self.paned_window, orient=tk.VERTICAL)

        # Upper frame for meta tags
        self.upper_frame = MetaTagsFrame(
            self._left_paned, controller=self._controller)

        # Lower frame for text annotation display
        self.lower_frame = AnnotationTextDisplayFrame(
            self._left_paned, controller=self._controller, is_static_observer=True)

        # Add both frames to the vertical PanedWindow inside left_frame
        # MetaTagsFrame gets less space
        self._left_paned.add(self.upper_frame, weight=0)
        # AnnotationTextDisplayFrame gets more space
        self._left_paned.add(self.lower_frame, weight=4)
        # SearchFrame gets a small space at the bottom
        wrapper = ttk.Frame(self._left_paned, padding=(10, 5))  # (padx, pady)
        self.search_frame = SearchFrame(
            wrapper, controller=self._controller, root_view_id=self._view_id)
        self.search_frame.pack(fill="both", expand=True)
        self._left_paned.add(wrapper, weight=0)

        # Right frame for the tagging menu
        self._right_frame = AnnotationMenuFrame(
            self, controller=self._controller, root_view_id=self._view_id)

        # Add the left PanedWindow and the right frame to the main PanedWindow
        self.paned_window.add(self._left_paned, weight=6)
        self.paned_window.add(self._right_frame, weight=1)

    def enable_shortcuts(self) -> None:
        """
        Enables Ctrl+1..4 shortcuts for adding tag types.
        """
        self.bind_all("<Control-Key-1>", self._on_shortcut_tag_1)
        self.bind_all("<Control-Key-2>", self._on_shortcut_tag_2)
        self.bind_all("<Control-Key-3>", self._on_shortcut_tag_3)
        self.bind_all("<Control-Key-4>", self._on_shortcut_tag_4)


    def disable_shortcuts(self) -> None:
        """
        Disables Ctrl+1..4 shortcuts for adding tag types.
        """
        self.unbind_all("<Control-Key-1>")
        self.unbind_all("<Control-Key-2>")
        self.unbind_all("<Control-Key-3>")
        self.unbind_all("<Control-Key-4>")


    # --- Shortcut handlers ---

    def _on_shortcut_tag_1(self, event=None) -> None:
        self._right_frame.trigger_add_tag(0)

    def _on_shortcut_tag_2(self, event=None) -> None:
        self._right_frame.trigger_add_tag(1)

    def _on_shortcut_tag_3(self, event=None) -> None:
        self._right_frame.trigger_add_tag(2)

    def _on_shortcut_tag_4(self, event=None) -> None:
        self._right_frame.trigger_add_tag(3)
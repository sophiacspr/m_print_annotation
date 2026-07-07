import tkinter as tk
from tkinter import ttk
from typing import Dict, List
from controller.interfaces import IController
from observer.interfaces import IPublisher
from view.annotation_tag_frame import AnnotationTagFrame
from view.interfaces import IAnnotationMenuFrame
from viewmodel.annotation_menu_view_model import AnnotationMenuViewModel


class AnnotationMenuFrame(tk.Frame, IAnnotationMenuFrame):
    """
    A tkinter Frame that contains a Notebook with pages representing template groups.
    This frame acts as an observer and updates the layout and content of annotation widgets
    based on data from the controller.
    """

    def __init__(self, parent: tk.Widget, controller: IController, root_view_id: str) -> None:
        """
        Initializes the AnnotationMenuFrame with a Notebook containing pages for each template group.

        Args:
            parent (tk.Widget): The parent tkinter container (e.g., Tk, Frame) for this TaggingMenuFrame.
            controller (IController): The controller that provides template groups and state updates.
            root_view_id (str): The identifier of the parent view or notebook page.
        """
        super().__init__(parent)

        self.observer_id: str = "annotation_menu"

        self._controller = controller
        self._view_model = AnnotationMenuViewModel(
            controller=controller,
            on_change=self._render_from_view_model,
            auto_register=False,
        )
        self._template_groups: List[Dict] = []

        # Create the internal notebook to hold group pages
        self._notebook = ttk.Notebook(self)
        self._notebook.pack(fill="both", expand=True)

        # Subscribe to state updates
        self._controller.add_observer(self._view_model)

        # Dictionary of tag frames keyed by tag type
        self._tag_frames: Dict[str, AnnotationTagFrame] = {}
        self._tag_frames_list: List[AnnotationTagFrame] = []

        self._root_view_id = root_view_id
        # Flag to indicate if initial layout is already rendered
        self._layout_rendered = False
        self._observers_registered = False

    def _render(self) -> None:
        """
        Renders pages in the notebook for each template group.
        This method should only be called once after layout data is available.
        """
        for group in self._template_groups:
            group_name = group["group_name"]
            group_name = group_name[0].upper() + group_name[1:]
            group_templates = group["templates"]
            page_frame = self._render_single_page(group_templates)
            self._notebook.add(page_frame, text=group_name)

        self._layout_rendered = True

    def _render_single_page(self, group_templates: List[Dict]) -> tk.Frame:
        """
        Renders a scrollable page with TagFrames based on the provided templates.

        Args:
            group_templates (List[Dict]): A list of templates to be displayed in the page.

        Returns:
            tk.Frame: A scrollable frame with TagFrames for each template.
        """
        container_frame = tk.Frame(self)

        canvas = tk.Canvas(container_frame)
        scrollbar = ttk.Scrollbar(
            container_frame, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.bind(
            "<Configure>",
            lambda e: canvas.itemconfig(
                "scrollable_window", width=canvas.winfo_width())
        )

        canvas.create_window((0, 0), window=scrollable_frame,
                             anchor="nw", tags="scrollable_window")

        for template in group_templates:
            tag_type = template.get("type")
            if tag_type in self._tag_frames:
                continue  # Avoid adding the same frame multiple times

            tag_frame = AnnotationTagFrame(
                parent=scrollable_frame,
                controller=self._controller,
                template=template,
                root_view_id=self._root_view_id
            )
            self._tag_frames_list.append(tag_frame)
            tag_frame.pack(fill="x", padx=5, pady=5, anchor="n", expand=True)
            self._tag_frames[tag_frame.get_name()] = tag_frame

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        return container_frame

    def _ensure_layout(self) -> None:
        """
        Ensures that the layout is rendered once template groups are available.
        This method avoids repeated rendering by checking an internal flag.
        """
        if not self._layout_rendered and self._template_groups:
            self._render()

    def update(self, publisher: IPublisher) -> None:
        """
        Updates the observer based on the state changes from the given publisher.

        This method retrieves the updated state from the controller and processes both 
        data-related and layout-related changes in a unified way.

        Args:
            publisher (IPublisher): The publisher that triggered the update.
        """
        self._view_model.update(publisher)

    def _render_from_view_model(self) -> None:
        """Renders state from the framework-independent view model."""
        self._template_groups = self._view_model.template_groups
        self._ensure_layout()

        if not self._layout_rendered:
            return

        for _, tag_frame in self._tag_frames.items():
            tag_frame.set_selected_text(self._view_model.selected_text)

        for tag_type, tag_frame in self._tag_frames.items():
            tag_frame.set_attributes(self._view_model.suggestions.get(tag_type, {}))
            tag_frame.set_idref_list(self._view_model.idrefs_by_tag_type.get(tag_type, [""]))

        tag_type = self._view_model.current_db_search_tag_type
        if tag_type is not None:
            if tag_type in self._tag_frames:
                self._tag_frames[tag_type].set_search_result(self._view_model.current_search_result)
            else:
                raise ValueError(f"Tag type '{tag_type}' not found in tag frames.")

    def finalize_view(self) -> None:
        """
        Retrieves the layout state and triggers the initial layout rendering.
        This method should be called once when the view is initialized.
        """
        self._view_model.finalize_view()

    def finalize_observers(self) -> None:
        """
        Finalizes the observer registration process.
        This method should be called once to ensure observers are registered correctly.
        """
        self._controller.add_observer(self._view_model)
        self._observers_registered = True

    def trigger_add_tag(self, tag_type_index: int) -> None:
        """
        Triggers the add tag action for the specified tag type index.
        This method is called by the shortcut handlers to add a tag of the corresponding type.
        Args:
            tag_type_index (int): The index of the tag type to add (0-based).
        """
        self._tag_frames_list[tag_type_index].trigger_add_tag()

    def get_observer_id(self) -> str:
        """
        Returns the stable observer identifier used by the source mapping.

        Returns:
            str: The observer identifier.
        """
        return self._view_model.get_observer_id()
from typing import List
import tkinter as tk
from tkinter import ttk

from controller.interfaces import IController
from enums.menu_pages import MenuSubpage
from observer.interfaces import IPublisher
from view.new_project_wizard_frame import NewProjectWizardFrame
from viewmodel.edit_project_wizard_view_model import EditProjectWizardViewModel


class EditProjectWizardFrame(ttk.Frame):
    """
    A project wizard used for editing existing projects.

    This class composes NewProjectWizardFrame for the shared wizard pages and
    adds one extra page for selecting the project to edit.
    """

    observer_id = "edit_project_wizard"

    def __init__(self, controller: IController, master=None, parent_window: tk.Toplevel = None) -> None:
        super().__init__(master)
        self._controller = controller
        self._view_model = EditProjectWizardViewModel(
            controller=controller,
            on_change=self._render_from_view_model,
            auto_register=False,
        )
        self._parent_window = parent_window
        self._available_projects: List[str] = []
        self._selected_project: str | None = None
        self._project_data: dict = {}

        self._wizard = NewProjectWizardFrame(
            controller=controller,
            master=self,
            parent_window=parent_window,
            register_as_observer=False,
        )
        self._wizard.pack(expand=True, fill="both")

        # Keep local aliases for the composed wizard internals that this wrapper customizes.
        self._notebook = self._wizard._notebook

        self._init_page_project_selection()
        self._notebook.insert(
            0, self._page_project_selection, text="Choose Project")
        self._notebook.select(0)

        self._notebook.tab(1, text="Edit Project Name")
        self._notebook.tab(2, text="Edit Tags")
        self._notebook.tab(3, text="Edit Tag Groups")

        self._replace_finish_button()
        self._controller.add_observer(self._view_model)

    def _init_page_project_selection(self) -> None:
        """Initializes the first page for selecting an existing project."""
        self._page_project_selection = ttk.Frame(self._notebook)

        ttk.Label(self._page_project_selection, text="Select project to edit:").pack(
            anchor="w", padx=10, pady=10
        )

        self._listbox_projects = tk.Listbox(
            self._page_project_selection, exportselection=False)
        self._listbox_projects.pack(fill="both", expand=True, padx=10, pady=5)

        for project in self._available_projects:
            self._listbox_projects.insert(tk.END, project)

        ttk.Button(
            self._page_project_selection,
            text="Choose Project",
            command=self._choose_project
        ).pack(anchor="e", padx=10, pady=10)

    def _choose_project(self) -> None:
        """Handles selection of a project and loads its data into the wizard."""
        selected = self._listbox_projects.curselection()
        if not selected:
            tk.messagebox.showerror(
                "Error", "Please select a project.", parent=self)
            return

        self._selected_project = self._listbox_projects.get(selected[0])
        self._view_model.choose_project(self._selected_project)
        self._notebook.select(1)

    def _replace_finish_button(self) -> None:
        """Replaces the 'Finish' button on the last page with 'Edit Project'."""
        last_page = self._notebook.nametowidget(self._notebook.tabs()[-1])
        for child in last_page.winfo_children():
            if isinstance(child, ttk.Button) and child.cget("text") == "Finish":
                child.config(text="Edit Project",
                             command=self._on_button_pressed_edit_project)

    def _populate_projects_listbox(self, projects: List[str]) -> None:
        """Populates the projects listbox with the given project names.

        Args:
            projects (List[str]): List of project names to display.
        """
        self._listbox_projects.delete(0, tk.END)
        for project in projects:
            self._listbox_projects.insert(tk.END, project)
        if projects:
            self._listbox_projects.selection_set(0)

    def update(self, publisher: IPublisher) -> None:
        """
        Updates the wizard state based on the current project data.

        Args:
            publisher (IPublisher): The publisher notifying about the update.
        """
        self._view_model.update(publisher)

    def _render_from_view_model(self) -> None:
        """Renders state from the framework-independent view model."""
        self._project_data = dict(self._view_model.project_data)
        self._wizard.apply_state(self._view_model.project_data)
        self._populate_projects_listbox(self._view_model.available_projects)

    def select_subtab(self, subtab: MenuSubpage) -> None:
        """
        Selects a project-editing subtab on the composed wizard.

        Args:
            subtab (MenuSubpage): The subtab to select.
        """
        self._wizard.select_subtab(subtab)

    def _on_button_pressed_edit_project(self) -> None:
        """
        Handles the 'Edit Project' button press.
        """
        current_page_data = self._wizard._collect_current_page_data()
        self._project_data.update(current_page_data)
        self._view_model.update_project_data(current_page_data)
        self._view_model.edit_project(self._selected_project, self._project_data)

    def destroy(self) -> None:
        """
        Cleans up the observer before destroying the widget.
        """
        self._view_model.dispose()
        super().destroy()

    def get_observer_id(self) -> str:
        """
        Returns the stable observer identifier used by the source mapping.

        Returns:
            str: The observer identifier.
        """
        return self._view_model.get_observer_id()

    def is_static_observer(self) -> bool:
        """
        Returns whether this observer must resolve state from static controller sources.

        Returns:
            bool: False for the edit project wizard.
        """
        return False

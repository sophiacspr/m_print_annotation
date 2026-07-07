from typing import List
import tkinter as tk
from tkinter import ttk

from controller.interfaces import IController
from enums.menu_pages import MenuSubpage
from observer.interfaces import IPublisher
from viewmodel.project_wizard_view_model import ProjectWizardViewModel


class NewProjectWizardFrame(ttk.Frame):
    """
    A multi-step wizard widget used to create or edit a project.

    This widget is intended to be embedded in a parent container such as a notebook tab.
    It consists of three pages:
        1. Project name entry.
        2. Tag selection and creation.
        3. Tag group definition.

    Optionally, initial project data can be passed during construction or later via `set_project_data`.
    """

    observer_id = "new_project_wizard"

    def __init__(
        self,
        controller: IController,
        parent_window: tk.Toplevel = None,
        master=None,
        project_data: dict = None,
        register_as_observer: bool = True,
    ) -> None:
        super().__init__(master)
        self._parent_window = parent_window
        self._controller = controller
        self._register_as_observer = register_as_observer
        self._view_model = ProjectWizardViewModel(
            controller=controller,
            observer_id=self.observer_id,
            on_change=self._render_from_view_model,
            auto_register=False,
        )

        if self._register_as_observer:
            self._controller.add_observer(self._view_model)

        self._notebook = ttk.Notebook(self)
        self._notebook.pack(expand=True, fill="both")

        self._init_page_project_name()
        self._init_page_tag_selection()
        self._init_page_tag_groups()

        if project_data:
            self.set_project_data(project_data)

        self._notebook.select(self._page_project_name)
        self._set_focus_on_default_widget()

    def _init_page_project_name(self) -> None:
        """Initializes the first wizard page for entering the project name."""
        self._page_project_name = ttk.Frame(self._notebook)
        self._notebook.add(self._page_project_name, text="Project Name")

        ttk.Label(self._page_project_name, text="Project Name:").grid(
            row=0, column=0, padx=10, pady=10, sticky="w")
        self._entry_project_name = tk.Entry(self._page_project_name)
        self._entry_project_name.grid(
            row=0, column=1, padx=10, pady=10, sticky="ew")
        self._page_project_name.columnconfigure(1, weight=1)
        self._page_project_name.rowconfigure(1, weight=1)

        ttk.Button(self._page_project_name, text="Next", command=self._on_button_pressed_next_tab).grid(
            row=2, column=1, sticky="e", padx=10, pady=10
        )

    def _init_page_tag_selection(self) -> None:
        """Initializes the second wizard page for selecting tags and creating new ones."""
        self._page_tag_selection = ttk.Frame(self._notebook)
        self._notebook.add(self._page_tag_selection, text="Select Tags")

        content_frame = ttk.Frame(self._page_tag_selection)
        content_frame.grid(row=0, column=0, columnspan=3,
                           sticky="nsew", padx=10, pady=5)
        content_frame.columnconfigure(0, weight=1)
        content_frame.columnconfigure(1, weight=1)
        content_frame.rowconfigure(0, weight=1)

        tag_select_frame = ttk.Frame(content_frame)
        tag_select_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        ttk.Label(tag_select_frame, text="Available Tags:").pack(anchor="w")
        self._listbox_available_tags = tk.Listbox(
            tag_select_frame, selectmode=tk.MULTIPLE)
        self._listbox_available_tags.pack(fill="both", expand=True)
        ttk.Button(tag_select_frame, text="Add Tags", command=self._on_button_pressed_add_selected_tags).pack(
            anchor="w", pady=5
        )

        selected_tag_frame = ttk.Frame(content_frame)
        selected_tag_frame.grid(row=0, column=1, sticky="nsew")
        ttk.Label(selected_tag_frame, text="Selected Tags:").pack(anchor="w")
        self._listbox_selected_tags = tk.Listbox(selected_tag_frame)
        self._listbox_selected_tags.pack(fill="both", expand=True)
        ttk.Button(selected_tag_frame, text="Remove Tags", command=self._on_button_pressed_remove_selected_tags).pack(
            anchor="e", pady=5
        )

        ttk.Button(self._page_tag_selection, text="Back", command=self._on_button_pressed_previous_tab).grid(
            row=1, column=0, sticky="w", padx=10, pady=10
        )
        ttk.Button(self._page_tag_selection, text="Next", command=self._on_button_pressed_next_tab).grid(
            row=1, column=2, sticky="e", padx=10, pady=10
        )

        self._page_tag_selection.columnconfigure(0, weight=1)
        self._page_tag_selection.columnconfigure(1, weight=1)
        self._page_tag_selection.columnconfigure(2, weight=1)
        self._page_tag_selection.rowconfigure(0, weight=1)

    def _init_page_tag_groups(self) -> None:
        """Initializes the third wizard page for creating tag groups."""
        self._page_tag_groups = ttk.Frame(self._notebook)
        self._notebook.add(self._page_tag_groups, text="Tag Groups")

        entry_frame = ttk.Frame(self._page_tag_groups)
        entry_frame.grid(row=0, column=0, columnspan=3,
                         sticky="ew", padx=10, pady=5)
        entry_frame.columnconfigure(1, weight=1)

        ttk.Label(entry_frame, text="Tag Group File Name:").grid(
            row=0, column=0, sticky="w", padx=5, pady=2)
        self._entry_tag_group_file_name = tk.Entry(entry_frame)
        self._entry_tag_group_file_name.grid(
            row=0, column=1, sticky="ew", padx=5, pady=2)

        ttk.Label(entry_frame, text="Tag Group Name:").grid(
            row=1, column=0, sticky="w", padx=5, pady=2)
        self._entry_tag_group_name = tk.Entry(entry_frame)
        self._entry_tag_group_name.grid(
            row=1, column=1, sticky="ew", padx=5, pady=2)

        content_frame = ttk.Frame(self._page_tag_groups)
        content_frame.grid(row=1, column=0, columnspan=3,
                           sticky="nsew", padx=10, pady=5)
        content_frame.columnconfigure(0, weight=1)
        content_frame.columnconfigure(1, weight=1)
        content_frame.rowconfigure(0, weight=1)

        tag_select_frame = ttk.Frame(content_frame)
        tag_select_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        ttk.Label(tag_select_frame, text="Select Tags for Group:").pack(
            anchor="w")
        self._listbox_tags_for_group = tk.Listbox(
            tag_select_frame, selectmode=tk.MULTIPLE)
        self._listbox_tags_for_group.pack(fill="both", expand=True)

        group_display_frame = ttk.Frame(content_frame)
        group_display_frame.grid(row=0, column=1, sticky="nsew")
        ttk.Label(group_display_frame,
                  text="Created Tag Groups:").pack(anchor="w")
        self._tree_created_groups = ttk.Treeview(
            group_display_frame, show="tree")
        self._tree_created_groups.pack(fill="both", expand=True)

        ttk.Button(self._page_tag_groups, text="Add Tag Group", command=self._on_button_pressed_add_tag_group).grid(
            row=2, column=0, sticky="w", padx=10, pady=5)
        right_action_frame = ttk.Frame(self._page_tag_groups)
        right_action_frame.grid(row=2, column=2, sticky="e", padx=10, pady=5)
        ttk.Button(right_action_frame, text="Tag up", command=self._on_button_pressed_tag_up).pack(side="left")
        ttk.Button(right_action_frame, text="Tag down", command=self._on_button_pressed_tag_down).pack(side="left")
        ttk.Button(right_action_frame, text="Delete Tag Group", command=self._on_button_pressed_delete_tag_group).pack(side="left")

        ttk.Button(self._page_tag_groups, text="Back", command=self._on_button_pressed_previous_tab).grid(
            row=3, column=0, sticky="w", padx=10, pady=10)
        ttk.Button(self._page_tag_groups, text="Finish", command=self._on_button_pressed_finish).grid(
            row=3, column=2, sticky="e", padx=10, pady=10)

        self._page_tag_groups.columnconfigure(0, weight=1)
        self._page_tag_groups.columnconfigure(1, weight=1)
        self._page_tag_groups.columnconfigure(2, weight=1)
        self._page_tag_groups.rowconfigure(1, weight=1)

    def update(self, publisher: IPublisher) -> None:
        """
        Populates the wizard fields with existing project data.

        Args:
            publisher (IPublisher): The publisher notifying about the update.
        """
        self._view_model.update(publisher)

    def apply_state(self, state: dict) -> None:
        """
        Applies project wizard state to the widget without requesting it from the controller.

        This allows wrapper widgets, such as EditProjectWizardFrame, to compose this
        class while remaining the registered observer themselves.
        """
        self._view_model.apply_state(state)
        self._entry_project_name.delete(0, tk.END)
        self._entry_project_name.insert(0, state.get("project_name", ""))

        self._populate_listbox(
            listbox=self._listbox_available_tags, items=state.get("locally_available_tags", []))
        self._populate_listbox(
            listbox=self._listbox_selected_tags, items=state.get("selected_tags", []))
        self._populate_listbox(
            listbox=self._listbox_tags_for_group, items=state.get("selected_tags", []))

        tag_groups = state.get("tag_groups", {})
        self._populate_tag_group_tree(tag_groups)

        self._entry_tag_group_file_name.delete(0, tk.END)
        self._entry_tag_group_file_name.insert(
            0, state.get("tag_group_file_name", ""))

    def _render_from_view_model(self) -> None:
        """Renders state from the framework-independent view model."""
        self.apply_state(self._view_model.project_data)

    def _populate_listbox(self, listbox: tk.Listbox, items: List[str]) -> None:
        """Fills a listbox with the given items."""
        listbox.delete(0, tk.END)
        for item in items:
            listbox.insert(tk.END, item)

    def _populate_tag_group_tree(self, groups: dict[str, list[str]]) -> None:
        """Fills the treeview with tag group categories as parents and tag names as children."""
        self._tree_created_groups.delete(
            *self._tree_created_groups.get_children())
        for group_name, tag_list in groups.items():
            parent_id = self._tree_created_groups.insert(
                "", "end", text=group_name)
            for tag in tag_list:
                self._tree_created_groups.insert(parent_id, "end", text=tag)

    def _collect_current_page_data(self) -> dict:
        """
        Collects data from the current page to update the model.
        """
        current_tab = self._notebook.select()
        data = {}
        if current_tab == str(self._page_project_name):
            data["project_name"] = self._entry_project_name.get().strip()
        elif current_tab == str(self._page_tag_selection):
            selected_tags = [self._listbox_selected_tags.get(i)
                             for i in range(self._listbox_selected_tags.size())]
            data["selected_tags"] = selected_tags
        elif current_tab == str(self._page_tag_groups):
            data["tag_group_file_name"] = self._entry_tag_group_file_name.get().strip()
            tag_groups = {}
            for parent_id in self._tree_created_groups.get_children():
                group_name = self._tree_created_groups.item(parent_id, "text")
                tags = [self._tree_created_groups.item(
                    child_id, "text") for child_id in self._tree_created_groups.get_children(parent_id)]
                tag_groups[group_name] = tags
            data["tag_groups"] = tag_groups
        return data

    def _on_button_pressed_add_tag_group(self) -> None:
        """
        Adds a new tag group based on the current entries and selected tags.
        """
        tag_group_file_name = self._entry_tag_group_file_name.get().strip()
        group_name = self._entry_tag_group_name.get().strip()
        if not group_name:
            tk.messagebox.showerror(
                "Error", "Tag group name cannot be empty.", parent=self)
            return

        selected_tags = [self._listbox_tags_for_group.get(i)
                         for i in self._listbox_tags_for_group.curselection()]
        if not selected_tags:
            tk.messagebox.showerror(
                "Error", "No tags selected for the group.", parent=self)
            return

        new_group = {"name": group_name, "tags": selected_tags}
        self._view_model.add_tag_group(tag_group_file_name, new_group)

    def _on_button_pressed_delete_tag_group(self) -> None:
        """
        Deletes the currently selected tag group from the list.
        """
        selected_ids = self._tree_created_groups.selection()
        if not selected_ids:
            tk.messagebox.showerror(
                "Error", "No tag group selected for deletion.", parent=self)
            self._notebook.select(-1)
            return

        for item_id in selected_ids:
            parent_id = self._tree_created_groups.parent(item_id)
            if parent_id == "":
                group_name = self._tree_created_groups.item(item_id, "text")
                self._view_model.remove_tag_group(group_name)

    def _on_button_pressed_add_selected_tags(self) -> None:
        """
        Adds selected tags from the available tags listbox to the selected tags listbox.
        """
        selected_indices = self._listbox_available_tags.curselection()
        if not selected_indices:
            return

        tags = []
        for index in selected_indices:
            tags.append(self._listbox_available_tags.get(index))
        self._view_model.add_tags(tags)

    def _on_button_pressed_remove_selected_tags(self) -> None:
        """
        Removes selected tags from the selected tags listbox back to the available tags listbox.
        """
        selected_indices = self._listbox_selected_tags.curselection()
        if not selected_indices:
            return
        self._view_model.remove_tags(selected_indices)

    def _on_button_pressed_finish(self) -> None:
        """
        Finalizes the project creation process.
        """
        current_page_data = self._collect_current_page_data()
        self._view_model.update_project_data(current_page_data)
        success = self._view_model.create_new_project()
        if success and self._parent_window:
            self._parent_window.destroy()

    def _on_button_pressed_next_tab(self) -> None:
        """
        Switches to the next tab in the notebook.
        """
        current_page_data = self._collect_current_page_data()
        self._view_model.update_project_data(current_page_data)
        index = self._notebook.index(self._notebook.select())
        self._notebook.select(index + 1)
        self._set_focus_on_default_widget()

    def _on_button_pressed_previous_tab(self) -> None:
        """
        Switches to the previous tab in the notebook.
        """
        current_page_data = self._collect_current_page_data()
        self._view_model.update_project_data(current_page_data)
        index = self._notebook.index(self._notebook.select())
        self._notebook.select(index - 1)
        self._set_focus_on_default_widget()

    def select_subtab(self, subtab: MenuSubpage) -> None:
        """
        Selects a subtab within the current tab.

        Args:
            subtab (MenuSubpage): The subtab to select.
        """
        notebook_page = {
            MenuSubpage.PROJECT_NAME: self._page_project_name,
            MenuSubpage.PROJECT_TAGS: self._page_tag_selection,
            MenuSubpage.PROJECT_TAG_GROUPS: self._page_tag_groups
        }.get(subtab)
        if notebook_page is not None:
            self._notebook.select(notebook_page)
            self._set_focus_on_default_widget()
        else:
            raise ValueError(f"Unknown subtab: {subtab}")

    def _set_focus_on_default_widget(self) -> None:
        """
        Sets focus on the default widget of the current page.
        """
        current_tab = self._notebook.select()
        if current_tab == str(self._page_project_name):
            self._entry_project_name.focus_set()
        elif current_tab == str(self._page_tag_selection):
            self._listbox_available_tags.focus_set()
        elif current_tab == str(self._page_tag_groups):
            self._entry_tag_group_file_name.focus_set()

    def _on_button_pressed_tag_up(self) -> None:
        """
        Moves the selected tag up within its group.
        """
        selected_ids = self._tree_created_groups.selection()
        if not selected_ids:
            return
        item_id = selected_ids[0]
        parent_id = self._tree_created_groups.parent(item_id)
        if parent_id == "":
            return
        siblings = list(self._tree_created_groups.get_children(parent_id))
        idx = siblings.index(item_id)
        if idx == 0:
            return
        group_name = self._tree_created_groups.item(parent_id, "text")
        tag_text = self._tree_created_groups.item(item_id, "text")
        new_idx = idx - 1
        self._tree_created_groups.move(item_id, parent_id, new_idx)
        tag_groups = self._build_tag_groups_from_tree()
        self._view_model.update_project_data({"tag_groups": tag_groups})
        self._try_restore_tree_selection(group_name, tag_text)

    def _on_button_pressed_tag_down(self) -> None:
        """
        Moves the selected tag down within its group.
        """
        selected_ids = self._tree_created_groups.selection()
        if not selected_ids:
            return
        item_id = selected_ids[0]
        parent_id = self._tree_created_groups.parent(item_id)
        if parent_id == "":
            return
        siblings = list(self._tree_created_groups.get_children(parent_id))
        idx = siblings.index(item_id)
        if idx == len(siblings) - 1:
            return
        group_name = self._tree_created_groups.item(parent_id, "text")
        tag_text = self._tree_created_groups.item(item_id, "text")
        new_idx = idx + 1
        self._tree_created_groups.move(item_id, parent_id, new_idx)
        tag_groups = self._build_tag_groups_from_tree()
        self._view_model.update_project_data({"tag_groups": tag_groups})
        self._try_restore_tree_selection(group_name, tag_text)

    def _build_tag_groups_from_tree(self) -> dict[str, list[str]]:
        """
        Builds the tag_groups dict from the current Treeview structure.

        Returns:
            dict[str, list[str]]: Group names to list of tag texts.
        """
        tag_groups = {}
        for p_id in self._tree_created_groups.get_children():
            group_name = self._tree_created_groups.item(p_id, "text")
            tags = [self._tree_created_groups.item(c_id, "text") for c_id in self._tree_created_groups.get_children(p_id)]
            tag_groups[group_name] = tags
        return tag_groups

    def _try_restore_tree_selection(self, group_name: str, tag_text: str) -> None:
        """
        Attempts to restore selection to the tag with given group_name and tag_text.

        Args:
            group_name: The name of the group.
            tag_text: The text of the tag.
        """
        try:
            for p_id in self._tree_created_groups.get_children():
                if self._tree_created_groups.item(p_id, "text") == group_name:
                    for c_id in self._tree_created_groups.get_children(p_id):
                        if self._tree_created_groups.item(c_id, "text") == tag_text:
                            self._tree_created_groups.selection_set(c_id)
                            self._tree_created_groups.see(c_id)
                            return
        except tk.TclError:
            pass

    def destroy(self) -> None:
        """
        Cleans up the observer before destroying the window.
        """
        if self._register_as_observer:
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
            bool: False for the project wizard.
        """
        return False

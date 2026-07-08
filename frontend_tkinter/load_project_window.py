import tkinter as tk
from tkinter import ttk
from controller.interfaces import IController
from observer.interfaces import IObserver, IPublisher
from viewmodel.load_project_window_view_model import LoadProjectWindowViewModel


class LoadProjectWindow(tk.Toplevel, IObserver):
    """
    A window for selecting and loading a project.

    This window observes the controller for available projects and allows the user
    to select one from a dropdown and trigger its loading.
    """

    def __init__(self, controller: IController, master: tk.Tk, *args, **kwargs) -> None:
        """
        Initializes the LoadProjectWindow.

        Args:
            controller (IController): The controller providing project data and actions.
            master (tk.Tk): The parent application window.
        """
        super().__init__(master, *args, **kwargs)

        self.observer_id: str = "load_project"

        self._controller = controller
        self._view_model = LoadProjectWindowViewModel(
            controller=controller,
            on_change=self._render_from_view_model,
            auto_register=False,
        )
        self._controller.add_observer(self._view_model)
        self.title("Load Project")
        self.geometry("600x200")
        self.resizable(False, False)

        # Combobox for selecting a project
        ttk.Label(self, text="Select Project:").pack(
            anchor="w", padx=10, pady=(10, 0))
        self._combo_projects = ttk.Combobox(self, state="readonly")
        self._combo_projects.pack(fill="x", padx=10, pady=5)

        # Button to trigger loading
        ttk.Button(self, text="Load Project", command=self._on_load_project).pack(
            anchor="e", padx=10, pady=10)

    def update(self, publisher: IPublisher) -> None:
        """
        Called by the controller to update this observer with new data.

        Args:
            publisher (IPublisher): The publisher that triggered the update.
        """
        self._view_model.update(publisher)

    def _render_from_view_model(self) -> None:
        """Renders state from the framework-independent view model."""
        self._combo_projects["values"] = self._view_model.project_names
        if self._view_model.project_names:
            self._combo_projects.current(0)

    def _on_load_project(self) -> None:
        """
        Loads the selected project via the controller.
        """
        selected = self._combo_projects.get()
        if selected:
            self._view_model.load_project(selected)
            self.destroy()

    def destroy(self) -> None:
        """
        Cleans up the observer before destroying the window.
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
import tkinter as tk
from controller.interfaces import IController
from view.interfaces import IView


class ViewBehavior:
    """
    Reusable behavior for top-level view frames.

    This helper centralizes focus handling and global undo/redo shortcut binding
    without requiring concrete views to inherit from the project-specific View
    base class. The owning widget remains a normal Tkinter frame.
    """

    def __init__(
        self,
        owner: tk.Widget,
        controller: IController,
        view_id: str | None = None,
        observer_id: str = "view",
    ) -> None:
        """
        Initializes shared view behavior for the given owner widget.

        Args:
            owner (tk.Widget): The Tkinter widget that owns this behavior.
            controller (IController): The controller managing actions for this view.
            view_id (str | None): The unique logical view identifier.
            observer_id (str): The stable observer identifier used by the source mapping.
        """
        self._owner: tk.Widget = owner
        self._controller: IController = controller
        self._view_id: str | None = view_id
        self._observer_id: str = observer_id

        self._bind_shortcuts()
        self._owner.bind("<FocusIn>", self._on_focus)
        self._owner.configure(takefocus=True)

    def set_view_id(self, view_id: str) -> None:
        """
        Sets the logical view identifier used for focus and shortcut routing.

        Args:
            view_id (str): The logical view identifier.
        """
        self._view_id = view_id

    def set_observer_id(self, observer_id: str) -> None:
        """
        Sets the stable observer identifier used by the source mapping.

        Args:
            observer_id (str): The observer identifier.
        """
        self._observer_id = observer_id

    def _bind_shortcuts(self) -> None:
        """
        Globally binds the keyboard shortcuts for undo (Ctrl+Z) and redo (Ctrl+Y).
        These events are routed to the controller, which delegates them to the active view.
        """
        self._owner.bind_all("<Control-z>", self._global_undo_handler)
        self._owner.bind_all("<Control-y>", self._global_redo_handler)

    def _global_undo_handler(self, event: tk.Event) -> None:
        """
        Handles the global undo action by delegating it to the controller.

        Args:
            event (tk.Event): The keyboard event that triggered this action.
        """
        self._controller.undo_command(self._controller.get_active_view())

    def _global_redo_handler(self, event: tk.Event) -> None:
        """
        Handles the global redo action by delegating it to the controller.

        Args:
            event (tk.Event): The keyboard event that triggered this action.
        """
        self._controller.redo_command(self._controller.get_active_view())

    def _on_focus(self, event: tk.Event) -> None:
        """
        Updates the controller with the active view when the owner gains focus.

        Args:
            event (tk.Event): The event triggered when this view gains focus.
        """
        self._owner.focus_set()
        if self._view_id is not None:
            self._controller.set_active_view(self._view_id)

    def get_view_id(self) -> str | None:
        """
        Returns the logical view identifier.

        Returns:
            str | None: The logical view identifier.
        """
        return self._view_id

    def get_observer_id(self) -> str:
        """
        Returns the stable observer identifier used by the source mapping.

        Returns:
            str: The observer identifier.
        """
        return self._observer_id


class View(tk.Frame, IView):
    """
    Backward-compatible Tkinter base class for views.

    New concrete views should prefer composing ViewBehavior instead of inheriting
    from this project-specific base class. This class is kept for compatibility
    with still-unmigrated views.
    """

    observer_id: str = "view"

    def __init__(self, parent: tk.Widget, controller: IController) -> None:
        """
        Initializes the View with a reference to the parent widget and controller.

        Args:
            parent (tk.Widget): The parent widget where this frame will be placed.
            controller (IController): The controller managing actions for this view.
        """
        super().__init__(parent)

        self._controller = controller
        self._view_id: str | None = None
        self._view_behavior = ViewBehavior(
            owner=self,
            controller=controller,
            view_id=self._view_id,
            observer_id=self.observer_id,
        )

    def get_view_id(self) -> str | None:
        """
        Returns the logical view identifier.

        Returns:
            str | None: The logical view identifier.
        """
        return self._view_id

    def get_observer_id(self) -> str:
        """
        Returns the stable observer identifier used by the source mapping.

        Returns:
            str: The observer identifier.
        """
        return self.observer_id

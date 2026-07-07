from __future__ import annotations

from typing import Any, Callable

from viewmodel.ports import ObserverStatePort


class BaseObserverViewModel:
    """Framework-independent base class for observer-backed view models."""

    observer_id: str = "base_observer"

    def __init__(
        self,
        controller: ObserverStatePort,
        observer_id: str | None = None,
        is_static_observer: bool = False,
        on_change: Callable[[], None] | None = None,
        auto_register: bool = True,
    ) -> None:
        self._controller = controller
        self._observer_id = observer_id or self.observer_id
        self._is_static_observer = is_static_observer
        self._on_change = on_change
        if auto_register:
            self._controller.add_observer(self)

    def get_observer_id(self) -> str:
        return self._observer_id

    def is_static_observer(self) -> bool:
        return self._is_static_observer

    def update(self, publisher: Any) -> None:
        state = self._controller.get_observer_state(self, publisher)
        self.apply_state(state, publisher)
        self.notify_change()

    def finalize_view(self) -> None:
        state = self._controller.get_observer_state(self)
        self.apply_state(state, None)
        self.notify_change()

    def finalize_observers(self) -> None:
        self._controller.add_observer(self)

    def dispose(self) -> None:
        self._controller.remove_observer(self)

    def apply_state(self, state: dict[str, Any], publisher: Any = None) -> None:
        """Update internal state from observer state. Subclasses may override."""

    def notify_change(self) -> None:
        if self._on_change is not None:
            self._on_change()

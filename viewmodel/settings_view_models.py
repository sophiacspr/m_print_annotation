from __future__ import annotations

from viewmodel.base_view_model import BaseObserverViewModel
from viewmodel.ports import ObserverStatePort


class GlobalSettingsViewModel(BaseObserverViewModel):
    observer_id = "global_settings"

    def __init__(self, controller: ObserverStatePort, on_change=None, auto_register: bool = True) -> None:
        super().__init__(controller, self.observer_id, False, on_change, auto_register)


class ProjectSettingsViewModel(BaseObserverViewModel):
    observer_id = "project_settings"

    def __init__(self, controller: ObserverStatePort, on_change=None, auto_register: bool = True) -> None:
        super().__init__(controller, self.observer_id, False, on_change, auto_register)

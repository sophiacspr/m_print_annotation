from __future__ import annotations

from typing import Any, Callable

from viewmodel.base_view_model import BaseObserverViewModel
from viewmodel.ports import ObserverStatePort


class ExtractionFrameViewModel(BaseObserverViewModel):
    observer_id = "extraction"

    def __init__(self, controller: ObserverStatePort, on_change: Callable[[], None] | None = None, auto_register: bool = True) -> None:
        super().__init__(controller, self.observer_id, False, on_change, auto_register)
        self.file_path: str = ""
        self.page_range: str = ""
        self.page_margins: str = ""

    def apply_state(self, state: dict[str, Any], publisher: Any = None) -> None:
        if "file_path" in state:
            self.file_path = state["file_path"]

    def extract_pages(self, pdf_path: str, page_range: str, page_margins: str) -> None:
        self.file_path = pdf_path
        self.page_range = page_range
        self.page_margins = page_margins
        self._controller.perform_pdf_extraction(
            {"pdf_path": pdf_path, "page_range": page_range, "page_margins": page_margins}
        )

    def adopt_text(self) -> None:
        self._controller.perform_text_adoption()

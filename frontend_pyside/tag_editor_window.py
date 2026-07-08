from __future__ import annotations

from PySide6.QtWidgets import QLabel, QDialog, QTabWidget, QVBoxLayout, QWidget

from enums.menu_pages import MenuPage


class TagEditorWindow(QDialog):
    """Placeholder-compatible tag editor window for the PySide frontend."""

    def __init__(self, master: QWidget | None = None) -> None:
        super().__init__(master)
        self.setWindowTitle("Tag Editor")
        self.resize(900, 600)
        layout = QVBoxLayout(self)
        self._notebook = QTabWidget()
        self._new_tag_page = QLabel("New tag type editor is not implemented yet.")
        self._edit_tag_page = QLabel("Edit tag type editor is not implemented yet.")
        self._notebook.addTab(self._new_tag_page, "New Tag")
        self._notebook.addTab(self._edit_tag_page, "Edit Tag")
        layout.addWidget(self._notebook)

    def select_tab(self, tab: MenuPage) -> None:
        mapping = {
            MenuPage.NEW_TAG: self._new_tag_page,
            MenuPage.EDIT_TAG: self._edit_tag_page,
        }
        widget = mapping.get(tab)
        if widget is None:
            raise ValueError(f"Unknown tab: {tab}")
        self._notebook.setCurrentWidget(widget)

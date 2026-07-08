from __future__ import annotations

from typing import Any

from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QFileDialog,
    QMainWindow,
    QMessageBox,
    QTabWidget,
)

from controller.interfaces import IController
from enums.export_formats import ExportFormat
from enums.menu_pages import MenuPage, MenuSubpage
from frontend_pyside.annotation_view import AnnotationView
from frontend_pyside.comparison_view import ComparisonView
from frontend_pyside.duplicates_dialog import DuplicatesDialog
from frontend_pyside.extraction_view import ExtractionView
from frontend_pyside.load_project_window import LoadProjectWindow
from frontend_pyside.project_window import ProjectWindow
from frontend_pyside.settings_window import SettingsWindow
from frontend_pyside.tag_editor_window import TagEditorWindow
from viewmodel.main_window_view_model import MainWindowViewModel


class MainWindow(QMainWindow):
    """PySide6 main window using the framework-independent ViewModel layer."""

    observer_id = "main_window"
    DEFAULT_NOTEBOOK_INDEX = 1

    def __init__(self, controller: IController) -> None:
        super().__init__()
        self._controller = controller
        self._view_model = MainWindowViewModel(controller=controller, on_change=self._render_from_view_model, auto_register=False)
        self._controller.register_view("main_window", self)
        self._annotation_view: AnnotationView | None = None
        self._extraction_view: ExtractionView | None = None
        self._comparison_view: ComparisonView | None = None
        self._project_window: ProjectWindow | None = None
        self._tag_editor_window: TagEditorWindow | None = None
        self._settings_window: SettingsWindow | None = None
        self.setWindowTitle("Text Annotation Tool")
        self.resize(1400, 900)
        self._create_menu()
        self._render_views()
        self._controller.add_observer(self._view_model)
        self._bind_global_shortcuts()

    def _create_menu(self) -> None:
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("File")
        self._add_action(file_menu, "Open File", self._on_open, "Ctrl+O")
        self._add_action(file_menu, "Save File", self._on_save, "Ctrl+S")
        self._add_action(file_menu, "Save as...", self._on_save_as, "Ctrl+Shift+S")
        export_menu = file_menu.addMenu("Export")
        self._add_action(export_menu, "Inline tags", self._on_export_inline_tags)
        self._add_action(export_menu, "Tag list / Plain text", self._on_export_tag_list_plain_text)
        file_menu.addSeparator()
        self._add_action(file_menu, "Exit", self.close)

        project_menu = menu_bar.addMenu("Project")
        self._add_action(project_menu, "New Project", self._on_new_project)
        self._add_action(project_menu, "Open Project", self._on_open_project)
        self._add_action(project_menu, "Edit Project", self._on_edit_project)
        self._add_action(project_menu, "Project Settings", self._on_project_settings)

        settings_menu = menu_bar.addMenu("Settings")
        self._add_action(settings_menu, "Global Settings", self._on_settings)

        help_menu = menu_bar.addMenu("Help")
        self._add_action(help_menu, "About", self._on_about)
        self._add_action(help_menu, "Help", self._on_help)

    def _add_action(self, menu, text: str, callback, shortcut: str | None = None) -> QAction:
        action = QAction(text, self)
        if shortcut:
            action.setShortcut(QKeySequence(shortcut))
        action.triggered.connect(callback)
        menu.addAction(action)
        return action

    def _render_views(self) -> None:
        self._notebook = QTabWidget()
        self.setCentralWidget(self._notebook)
        self._extraction_view = ExtractionView(self._notebook, self._controller)
        self._annotation_view = AnnotationView(self._notebook, self._controller)
        self._comparison_view = ComparisonView(self._notebook, self._controller)
        self._notebook.addTab(self._extraction_view, "PDF Extraction")
        self._notebook.addTab(self._annotation_view, "Text Annotation")
        self._notebook.addTab(self._comparison_view, "Text Comparison")
        self._notebook.setCurrentIndex(self.DEFAULT_NOTEBOOK_INDEX)
        self._controller.set_active_view(["extraction", "annotation", "comparison"][self.DEFAULT_NOTEBOOK_INDEX])
        self._notebook.currentChanged.connect(lambda _index: self._on_notebook_tab_changed())
        self._update_mode_shortcuts()

    def _destroy_views(self) -> None:
        old = self.centralWidget()
        if old is not None:
            old.setParent(None)
            old.deleteLater()
        self._extraction_view = None
        self._annotation_view = None
        self._comparison_view = None

    def reload_views_for_new_project(self) -> None:
        self._controller.cleanup_observers_for_reload()
        self._destroy_views()
        self._render_views()

    def _on_notebook_tab_changed(self) -> None:
        mapping = {0: "extraction", 1: "annotation", 2: "comparison"}
        active_view = mapping.get(self._notebook.currentIndex())
        if active_view:
            self._controller.set_active_view(active_view)
        self._update_mode_shortcuts()

    def _update_mode_shortcuts(self) -> None:
        active_view = self._controller.get_active_view()
        if self._annotation_view:
            (self._annotation_view.enable_shortcuts if active_view == "annotation" else self._annotation_view.disable_shortcuts)()
        if self._extraction_view:
            (self._extraction_view.enable_shortcuts if active_view == "extraction" else self._extraction_view.disable_shortcuts)()
        if self._comparison_view:
            (self._comparison_view.enable_shortcuts if active_view == "comparison" else self._comparison_view.disable_shortcuts)()

    def _bind_global_shortcuts(self) -> None:
        # QAction shortcuts already cover open/save. Keep method for API symmetry with Tk frontend.
        pass

    def _on_open(self) -> None:
        self._controller.perform_open_file()

    def _on_save(self) -> None:
        self._controller.perform_save()

    def _on_save_as(self) -> None:
        self._controller.perform_save_as()

    def _on_export_inline_tags(self) -> None:
        self._controller.perform_export_document(ExportFormat.INLINE)

    def _on_export_tag_list_plain_text(self) -> None:
        self._controller.perform_export_document(ExportFormat.SPLIT)

    def _on_new_project(self) -> None:
        self._controller.perform_menu_new_project()

    def _on_edit_project(self) -> None:
        self._controller.perform_menu_edit_project()

    def _on_project_settings(self) -> None:
        self._controller.perform_menu_project_settings()

    def _on_open_project(self) -> None:
        self._controller.perform_menu_load_project()

    def _on_settings(self) -> None:
        self._controller.perform_menu_global_settings()

    def _on_help(self) -> None:
        self._controller.perform_menu_help()

    def _on_about(self) -> None:
        self._controller.perform_menu_about()

    def open_project_window(self, tab: MenuPage = MenuPage.NEW_PROJECT, subtab: MenuSubpage | None = None) -> None:
        if self._project_window is None:
            self._project_window = ProjectWindow(self._controller, self)
        self._project_window.select_tab(tab, subtab)
        self._project_window.show()
        self._project_window.raise_()
        self._project_window.activateWindow()

    def open_settings_window(self, tab: MenuPage = MenuPage.GLOBAL_SETTINGS) -> None:
        if self._settings_window is None:
            self._settings_window = SettingsWindow(self._controller, self)
        self._settings_window.select_tab(tab)
        self._settings_window.show()
        self._settings_window.raise_()
        self._settings_window.activateWindow()

    def open_tag_editor(self, tab: MenuPage) -> None:
        if self._tag_editor_window is None:
            self._tag_editor_window = TagEditorWindow(self)
        self._tag_editor_window.select_tab(tab)
        self._tag_editor_window.show()
        self._tag_editor_window.raise_()
        self._tag_editor_window.activateWindow()

    def open_load_project_dialog(self) -> None:
        dialog = LoadProjectWindow(self._controller, self)
        dialog.exec()

    def focus_project_window(self) -> None:
        if self._project_window is not None:
            self._project_window.raise_()
            self._project_window.activateWindow()

    def ask_user_for_file_paths(self, load_config: dict[str, Any] | None = None) -> list[str]:
        config = (load_config or {}).get("config", {})
        mode = (load_config or {}).get("mode", "single")
        title = config.get("title", "Open file")
        initial_dir = config.get("initialdir", "")
        file_filter = self._qt_file_filter(config.get("filetypes", []))
        if mode == "multiple":
            files, _ = QFileDialog.getOpenFileNames(self, title, initial_dir, file_filter)
            return files
        file_path, _ = QFileDialog.getOpenFileName(self, title, initial_dir, file_filter)
        return [file_path] if file_path else []

    def ask_user_for_save_path(self, initial_dir: str = "") -> str:
        file_path, _ = QFileDialog.getSaveFileName(self, "Save file", initial_dir)
        return file_path

    def ask_user_for_overwrite_confirmation(self, path: str) -> bool:
        response = QMessageBox.question(self, "Overwrite file?", f"Overwrite existing file?\n{path}")
        return response == QMessageBox.StandardButton.Yes

    def ask_user_for_tag_duplicates(self, duplicates: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]] | None:
        return DuplicatesDialog(duplicates, self).show()

    def ask_user_for_save(self, view_id: str) -> bool:
        response = QMessageBox.question(self, "Unsaved changes", f"Save changes in {view_id}?")
        return response == QMessageBox.StandardButton.Yes

    def show_error_message(self, message: str) -> None:
        QMessageBox.critical(self, "Error", message)

    def set_project_manager_to(self, tab: MenuPage, subtab: MenuSubpage | None = None) -> None:
        self.open_project_window(tab, subtab)

    def finalize_view(self) -> None:
        self._view_model.finalize_view()

    def update(self, publisher: Any) -> None:
        self._view_model.update(publisher)

    def get_observer_id(self) -> str:
        return self._view_model.get_observer_id()

    def _render_from_view_model(self) -> None:
        if self._view_model.project_name:
            self.setWindowTitle(f"Text Annotation Tool - {self._view_model.project_name}")
        if hasattr(self, "_notebook"):
            index = self._view_model.active_notebook_index
            if 0 <= index < self._notebook.count() and self._notebook.currentIndex() != index:
                self._notebook.setCurrentIndex(index)

    def closeEvent(self, event) -> None:  # noqa: N802 - Qt API
        self._controller.check_for_saving(enforce_check=True)
        event.accept()

    def _qt_file_filter(self, filetypes: list[tuple[str, str]]) -> str:
        if not filetypes:
            return "All Files (*)"
        filters = []
        for label, pattern in filetypes:
            filters.append(f"{label} ({pattern})")
        return ";;".join(filters)

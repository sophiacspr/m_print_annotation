from __future__ import annotations

from typing import cast

from input_output.file_handler import FileHandler
from services.highlighting.color_scheme_types import HighlightTheme, ProjectColorScheme


class JsonHighlightThemeRepository:
    """Loads predefined highlight themes from JSON files."""

    def __init__(self, file_handler: FileHandler) -> None:
        self._file_handler = file_handler

    def load_theme(self, theme_name: str) -> HighlightTheme:
        theme_data = self._file_handler.read_file(
            "highlight_theme_directory",
            theme_name,
        )
        return cast(HighlightTheme, theme_data)


class JsonProjectColorSchemeRepository:
    """Stores project-specific color schemes."""

    def __init__(self, file_handler: FileHandler) -> None:
        self._file_handler = file_handler

    def save_color_scheme(
        self,
        color_scheme: ProjectColorScheme,
        file_name: str,
    ) -> None:
        self._file_handler.write_file(
            "project_color_scheme_directory",
            color_scheme,
            file_name,
        )
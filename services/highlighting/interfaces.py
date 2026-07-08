from __future__ import annotations

from typing import Protocol

from services.highlighting.color_scheme_types import HighlightTheme, ProjectColorScheme


class IHighlightThemeRepository(Protocol):
    def load_theme(self, theme_name: str) -> HighlightTheme:
        ...


class IProjectColorSchemeRepository(Protocol):
    def save_color_scheme(
        self,
        color_scheme: ProjectColorScheme,
        file_name: str,
    ) -> None:
        ...
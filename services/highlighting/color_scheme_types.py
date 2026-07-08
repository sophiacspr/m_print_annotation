from __future__ import annotations

from typing import TypedDict


class HighlightColor(TypedDict):
    background_color: str
    font_color: str


class HighlightTheme(TypedDict):
    search: HighlightColor
    current_search: HighlightColor
    colors: dict[str, HighlightColor]
    recommended_sets: dict[str, list[str]]
    fallback_order: list[str]


class ProjectColorScheme(TypedDict):
    tags: dict[str, HighlightColor]
    search: HighlightColor
    current_search: HighlightColor


class ProjectColorSchemeData(TypedDict):
    color_scheme: ProjectColorScheme
    file_name: str
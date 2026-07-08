from __future__ import annotations

from services.highlighting.color_scheme_types import (
    HighlightColor,
    HighlightTheme,
    ProjectColorScheme,
    ProjectColorSchemeData,
)
from services.highlighting.interfaces import (
    IHighlightThemeRepository,
    IProjectColorSchemeRepository,
)


class ColorAssignmentService:
    """Creates stable project color schemes from curated highlight themes."""

    def __init__(
        self,
        theme_repository: IHighlightThemeRepository,
        project_color_scheme_repository: IProjectColorSchemeRepository,
    ) -> None:
        self._theme_repository = theme_repository
        self._project_color_scheme_repository = project_color_scheme_repository

    def create_project_color_scheme(
        self,
        tag_keys: list[str],
        theme_name: str,
        file_name: str | None = None,
        should_write_file: bool = True,
    ) -> ProjectColorSchemeData:
        """
        Create a project-specific color scheme from a predefined highlight theme.

        Args:
            tag_keys: Tag types that should receive colors.
            theme_name: Name of the highlight theme JSON file.
            file_name: Optional output file name for the generated project scheme.
            should_write_file: Whether the generated scheme should be written.

        Returns:
            The generated color scheme and the file name.
        """
        if not tag_keys:
            raise ValueError("At least one tag key is required.")

        theme = self._theme_repository.load_theme(theme_name)
        normalized_tag_keys = self._normalize_tag_keys(tag_keys)
        tag_colors = self._assign_tag_colors(normalized_tag_keys, theme)

        color_scheme: ProjectColorScheme = {
            "tags": tag_colors,
            "search": theme["search"],
            "current_search": theme["current_search"],
        }

        resolved_file_name = file_name or self._build_file_name(theme_name)

        if should_write_file:
            self._project_color_scheme_repository.save_color_scheme(
                color_scheme=color_scheme,
                file_name=resolved_file_name,
            )

        return {
            "color_scheme": color_scheme,
            "file_name": resolved_file_name,
        }

    def extend_project_color_scheme(
        self,
        existing_color_scheme: ProjectColorScheme,
        tag_keys: list[str],
        theme_name: str,
    ) -> ProjectColorScheme:
        """
        Add missing tag colors without changing existing assignments.

        Args:
            existing_color_scheme: Current project color scheme.
            tag_keys: Required tag types.
            theme_name: Highlight theme used for fallback colors.

        Returns:
            Updated project color scheme.
        """
        theme = self._theme_repository.load_theme(theme_name)
        normalized_tag_keys = self._normalize_tag_keys(tag_keys)

        updated_tags = dict(existing_color_scheme["tags"])
        used_color_names = self._find_used_color_names(
            existing_tags=updated_tags,
            theme=theme,
        )

        for tag_key in normalized_tag_keys:
            if tag_key in updated_tags:
                continue

            color_name = self._next_free_color_name(
                theme=theme,
                used_color_names=used_color_names,
            )
            updated_tags[tag_key] = theme["colors"][color_name]
            used_color_names.append(color_name)

        return {
            "tags": updated_tags,
            "search": existing_color_scheme["search"],
            "current_search": existing_color_scheme["current_search"],
        }

    def _assign_tag_colors(
        self,
        tag_keys: list[str],
        theme: HighlightTheme,
    ) -> dict[str, HighlightColor]:
        """
        Assign colors to tag keys using the best matching recommended set.

        Args:
            tag_keys: Normalized tag keys.
            theme: Highlight theme.

        Returns:
            Mapping from tag type to concrete colors.
        """
        color_names = self._select_color_names(
            count=len(tag_keys),
            theme=theme,
        )

        return {
            tag_key: theme["colors"][color_name]
            for tag_key, color_name in zip(tag_keys, color_names)
        }

    def _select_color_names(
        self,
        count: int,
        theme: HighlightTheme,
    ) -> list[str]:
        """
        Select a curated color order for the requested number of tags.

        Args:
            count: Number of required colors.
            theme: Highlight theme.

        Returns:
            Color names.
        """
        recommended_sets = theme["recommended_sets"]

        available_sizes = sorted(int(size) for size in recommended_sets)
        selected_size = next(
            (size for size in available_sizes if size >= count),
            available_sizes[-1],
        )

        selected_names = list(recommended_sets[str(selected_size)])

        if len(selected_names) >= count:
            return selected_names[:count]

        fallback_names = [
            color_name
            for color_name in theme["fallback_order"]
            if color_name not in selected_names
        ]

        combined_names = selected_names + fallback_names

        if len(combined_names) < count:
            raise ValueError(
                f"Theme does not define enough colors for {count} tag types."
            )

        return combined_names[:count]

    def _find_used_color_names(
        self,
        existing_tags: dict[str, HighlightColor],
        theme: HighlightTheme,
    ) -> list[str]:
        """
        Resolve which named theme colors are already used.

        Args:
            existing_tags: Existing tag color assignments.
            theme: Highlight theme.

        Returns:
            List of used color names.
        """
        used_color_names: list[str] = []

        for existing_color in existing_tags.values():
            for color_name, theme_color in theme["colors"].items():
                if existing_color == theme_color and color_name not in used_color_names:
                    used_color_names.append(color_name)

        return used_color_names

    def _next_free_color_name(
        self,
        theme: HighlightTheme,
        used_color_names: list[str],
    ) -> str:
        """
        Return the next unused color name.

        Args:
            theme: Highlight theme.
            used_color_names: Already used color names.

        Returns:
            Color name.

        Raises:
            ValueError: If no free color exists.
        """
        for color_name in theme["fallback_order"]:
            if color_name not in used_color_names:
                return color_name

        raise ValueError("No free highlight color remains in the selected theme.")

    def _normalize_tag_keys(self, tag_keys: list[str]) -> list[str]:
        """
        Remove duplicates while preserving order.

        Args:
            tag_keys: Raw tag keys.

        Returns:
            Normalized tag keys.
        """
        normalized: list[str] = []

        for tag_key in tag_keys:
            if tag_key not in normalized:
                normalized.append(tag_key)

        return normalized

    def _build_file_name(self, theme_name: str) -> str:
        """
        Build the project color scheme file name.

        Args:
            theme_name: Highlight theme file name.

        Returns:
            Project color scheme file name.
        """
        normalized_name = theme_name.removesuffix(".json")
        return f"{normalized_name}_project_color_scheme.json"
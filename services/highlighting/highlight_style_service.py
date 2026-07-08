from __future__ import annotations


from utils.interfaces import ISettingsManager


class HighlightStyleService:
    """Resolves semantic highlight types to concrete foreground/background colors."""

    def __init__(self, settings_manager: ISettingsManager) -> None:
        self._settings_manager = settings_manager

    def resolve_tag_style(self, tag_type: str) -> tuple[str, str]:
        """
        Resolve the colors for a tag type.

        Args:
            tag_type: The semantic tag type, e.g. "TIMEX3" or "GEO".

        Returns:
            A tuple containing background and foreground color.
        """
        color_scheme = self._settings_manager.get_color_scheme()
        try:
            tag_style = color_scheme["tags"][tag_type]
        except KeyError as exc:
            raise KeyError(
                f"No highlight style configured for tag type '{tag_type}'."
            ) from exc

        return self._extract_style(tag_style, label=f"tag '{tag_type}'")

    def resolve_search_style(self) -> tuple[str, str]:
        """
        Resolve the colors for non-current search result highlights.

        Returns:
            A tuple containing background and foreground color.
        """
        color_scheme = self._settings_manager.get_color_scheme()
        return self._extract_style(color_scheme["search"], label="search")

    def resolve_current_search_style(self) -> tuple[str, str]:
        """
        Resolve the colors for the current search result highlight.

        Returns:
            A tuple containing background and foreground color.
        """
        color_scheme = self._settings_manager.get_color_scheme()
        return self._extract_style(
            color_scheme["current_search"],
            label="current_search",
        )

    def _extract_style(self, style: dict[str, str], *, label: str) -> tuple[str, str]:
        """
        Extract background and foreground colors from one style entry.

        Args:
            style: The style dictionary.
            label: Human-readable label for error messages.

        Returns:
            A tuple containing background and foreground color.
        """
        try:
            return style["background_color"], style["font_color"]
        except KeyError as exc:
            raise KeyError(
                f"Invalid highlight style for {label}: expected keys "
                "'background_color' and 'font_color'."
            ) from exc
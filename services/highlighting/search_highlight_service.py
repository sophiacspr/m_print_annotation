from __future__ import annotations

from model.interfaces import ISearchModel
from services.highlighting.highlight_style_service import HighlightStyleService
from utils.interfaces import ISettingsManager

HighlightData = tuple[str, str, int, int]


class SearchHighlightService:
    """Computes styled search highlights for the active search model."""

    def __init__(
        self,
        settings_manager: ISettingsManager,
        style_service: HighlightStyleService,
    ) -> None:
        self._settings_manager = settings_manager
        self._style_service = style_service

    def compute(self, search_model: ISearchModel | None) -> list[HighlightData]:
        """
        Compute styled search highlights.

        Args:
            search_model: The currently active search model.

        Returns:
            A list of highlight tuples:
            (background_color, font_color, start, end).
        """
        if search_model is None:
            return []

        search_state = search_model.get_state()
        current_result = search_state.get("current_search_result")
        highlights: list[HighlightData] = []

        if self._settings_manager.are_all_search_results_highlighted():
            background_color, font_color = self._style_service.resolve_search_style()
            for result in search_state.get("results", []):
                if result == current_result:
                    continue

                span = self._extract_span(result)
                if span is None:
                    continue

                start, end = span
                highlights.append((background_color, font_color, start, end))

        if current_result is not None:
            span = self._extract_span(current_result)
            if span is not None:
                background_color, font_color = (
                    self._style_service.resolve_current_search_style()
                )
                start, end = span
                highlights.append((background_color, font_color, start, end))

        return highlights

    def _extract_span(self, result: dict) -> tuple[int, int] | None:
        """
        Extract start/end positions from a search result object or dictionary.

        Args:
            result: A search result with start/end attributes or keys.

        Returns:
            A start/end tuple, or None if the object has no valid span.
        """
        if isinstance(result, dict):
            start = result.get("start")
            end = result.get("end")
        else:
            start = getattr(result, "start", None)
            end = getattr(result, "end", None)

        if start is None or end is None:
            return None

        return int(start), int(end)
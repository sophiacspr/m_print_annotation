from __future__ import annotations

from typing import Any

from services.highlighting.highlight_style_service import HighlightStyleService
from utils.interfaces import ITagManager

HighlightData = tuple[str, str, int, int]


class TagHighlightService:
    """Computes styled tag highlights for one document model."""

    def __init__(
        self,
        tag_manager: ITagManager,
        style_service: HighlightStyleService,
    ) -> None:
        self._tag_manager = tag_manager
        self._style_service = style_service

    def compute(self, document_model: Any) -> list[HighlightData]:
        """
        Compute styled tag highlights for one document.

        Args:
            document_model: The document model whose tags should be highlighted.

        Returns:
            A list of highlight tuples:
            (background_color, font_color, start, end).
        """
        if document_model is None:
            return []

        raw_highlights = self._tag_manager.get_highlight_data(document_model)
        highlights: list[HighlightData] = []

        for tag_type, start, end in raw_highlights:
            background_color, font_color = self._style_service.resolve_tag_style(
                tag_type
            )
            highlights.append(
                (
                    background_color,
                    font_color,
                    int(start),
                    int(end),
                )
            )

        return highlights
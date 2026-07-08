from __future__ import annotations

from typing import Any

from model.highlight_model import HighlightModel
from model.interfaces import IComparisonModel, IDocumentModel
from services.highlighting.search_highlight_service import SearchHighlightService
from services.highlighting.tag_highlight_service import TagHighlightService

HighlightData = tuple[str, str, int, int]


class HighlightService:
    """Coordinates highlight refreshes for annotation and comparison mode."""

    ANNOTATION_VIEW_ID = "annotation"
    COMPARISON_VIEW_ID = "comparison"

    def __init__(
        self,
        annotation_document_model: IDocumentModel ,
        annotation_highlight_model: HighlightModel,
        comparison_model: IComparisonModel,
        tag_highlight_service: TagHighlightService,
        search_highlight_service: SearchHighlightService,
    ) -> None:
        self._annotation_document_model = annotation_document_model
        self._annotation_highlight_model = annotation_highlight_model
        self._comparison_model = comparison_model
        self._tag_highlight_service = tag_highlight_service
        self._search_highlight_service = search_highlight_service

    def refresh(
        self,
        *,
        active_view_id: str | None,
        current_search_model: Any | None,
    ) -> None:
        """
        Refresh highlight models for the active view.

        Args:
            active_view_id: The currently active top-level view id.
            current_search_model: The currently active search model, if any.
        """
        targets = self._get_targets(active_view_id)
        if not targets:
            return

        search_highlights = self._search_highlight_service.compute(
            current_search_model
        )

        for index, (document_model, highlight_model) in enumerate(targets):
            tag_highlights = self._tag_highlight_service.compute(document_model)

            # Search belongs only to the first active text display.
            # In annotation mode this is the annotation document.
            # In comparison mode this is the raw/base display.
            model_search_highlights = search_highlights if index == 0 else []

            self._set_highlights(
                highlight_model=highlight_model,
                tag_highlights=tag_highlights,
                search_highlights=model_search_highlights,
            )

    def _get_targets(self, active_view_id: str | None) -> list[tuple[Any, Any]]:
        """
        Resolve document/highlight model pairs for the active view.

        Args:
            active_view_id: The currently active top-level view id.

        Returns:
            A list of (document_model, highlight_model) pairs.
        """
        if active_view_id == self.ANNOTATION_VIEW_ID:
            return [
                (
                    self._annotation_document_model,
                    self._annotation_highlight_model,
                )
            ]

        if active_view_id == self.COMPARISON_VIEW_ID:
            return self._get_comparison_targets()

        return []

    def _get_comparison_targets(self) -> list[tuple[Any, Any]]:
        """
        Resolve comparison document/highlight model pairs.

        Returns:
            A list of (document_model, highlight_model) pairs.
        """
        if self._comparison_model is None:
            return []

        get_document_models = getattr(
            self._comparison_model,
            "get_document_models",
            None,
        )
        get_highlight_models = getattr(
            self._comparison_model,
            "get_highlight_models",
            None,
        )

        if not callable(get_document_models) or not callable(get_highlight_models):
            return []

        document_models = get_document_models()
        highlight_models = get_highlight_models()

        return list(zip(document_models, highlight_models))

    def _set_highlights(
        self,
        *,
        highlight_model: HighlightModel,
        tag_highlights: list[HighlightData],
        search_highlights: list[HighlightData],
    ) -> None:
        """
        Update one highlight model.

        Args:
            highlight_model: The target highlight model.
            tag_highlights: Styled tag highlights.
            search_highlights: Styled search highlights.
        """
        set_highlights = getattr(highlight_model, "set_highlights", None)
        if callable(set_highlights):
            set_highlights(tag_highlights, search_highlights)
            return

        # Fallback for the current legacy HighlightModel API.
        reset = getattr(highlight_model, "reset", None)
        if callable(reset):
            reset(notify=False)

        highlight_model.add_tag_highlights(tag_highlights)
        highlight_model.add_search_highlights(search_highlights)
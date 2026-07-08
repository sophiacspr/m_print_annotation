from __future__ import annotations

from PySide6.QtCore import QEvent, QObject, QTimer
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import QSplitter, QWidget

from controller.interfaces import IController


MAIN_HORIZONTAL_SPLITTER_LEFT_WEIGHT = 5
MAIN_HORIZONTAL_SPLITTER_RIGHT_WEIGHT = 1
MAIN_HORIZONTAL_SPLITTER_TOTAL_WEIGHT = (
    MAIN_HORIZONTAL_SPLITTER_LEFT_WEIGHT + MAIN_HORIZONTAL_SPLITTER_RIGHT_WEIGHT
)
MAIN_HORIZONTAL_SPLITTER_LEFT_RATIO = (
    MAIN_HORIZONTAL_SPLITTER_LEFT_WEIGHT / MAIN_HORIZONTAL_SPLITTER_TOTAL_WEIGHT
)
MAIN_HORIZONTAL_SPLITTER_RIGHT_RATIO = (
    MAIN_HORIZONTAL_SPLITTER_RIGHT_WEIGHT / MAIN_HORIZONTAL_SPLITTER_TOTAL_WEIGHT
)

# Keep this low enough so it does not override the intended ratio too aggressively.
MAIN_HORIZONTAL_SPLITTER_RIGHT_MIN_WIDTH = 260

# Apply the initial splitter ratio only once the splitter has a meaningful width.
MAIN_HORIZONTAL_SPLITTER_MIN_VALID_WIDTH = 800


class ViewBehavior(QObject):
    """Shared top-level view behavior without requiring inheritance between project views."""

    def __init__(self, widget: QWidget, controller: IController, view_id: str, observer_id: str) -> None:
        super().__init__(widget)
        self._widget = widget
        self._controller = controller
        self._view_id = view_id
        self._observer_id = observer_id
        self._undo_shortcut = QShortcut(QKeySequence("Ctrl+Z"), widget)
        self._redo_shortcut = QShortcut(QKeySequence("Ctrl+Y"), widget)
        self._undo_shortcut.activated.connect(
            lambda: self._controller.undo_command(self._controller.get_active_view())
        )
        self._redo_shortcut.activated.connect(
            lambda: self._controller.redo_command(self._controller.get_active_view())
        )
        widget.installEventFilter(self)
        widget.setFocusPolicy(widget.focusPolicy().StrongFocus)

    def eventFilter(self, watched: QWidget, event: QEvent) -> bool:  # noqa: N802 - Qt API
        if watched is self._widget and event.type() == QEvent.Type.FocusIn:
            self._controller.set_active_view(self._view_id)
        return False

    def get_view_id(self) -> str:
        return self._view_id

    def get_observer_id(self) -> str:
        return self._observer_id


class MainHorizontalSplitterBehavior(QObject):
    """Applies the shared initial ratio for top-level horizontal splitters.

    Hidden tab pages can have invalid or tiny widths when the view is constructed.
    Therefore the initial ratio is applied lazily on the first meaningful show/resize
    event instead of only once during construction.
    """

    def __init__(self, splitter: QSplitter) -> None:
        super().__init__(splitter)
        self._splitter = splitter
        self._has_applied_initial_sizes = False
        splitter.installEventFilter(self)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802 - Qt API
        if watched is self._splitter and event.type() in {
            QEvent.Type.Show,
            QEvent.Type.Resize,
        }:
            self.apply_initial_sizes_when_ready()
        return False

    def apply_initial_sizes_when_ready(self) -> None:
        """Applies the configured ratio once the splitter has a meaningful width."""
        if self._has_applied_initial_sizes:
            return

        total_width = self._splitter.width()
        if total_width < MAIN_HORIZONTAL_SPLITTER_MIN_VALID_WIDTH:
            return

        right_width = max(
            int(total_width * MAIN_HORIZONTAL_SPLITTER_RIGHT_RATIO),
            MAIN_HORIZONTAL_SPLITTER_RIGHT_MIN_WIDTH,
        )
        left_width = max(total_width - right_width, 1)

        self._splitter.setSizes([left_width, right_width])
        self._has_applied_initial_sizes = True


def configure_main_horizontal_splitter(splitter: QSplitter) -> None:
    """Configure the default main two-pane layout for top-level views.

    The layout policy is centralized here so annotation and comparison views use
    exactly the same initial left/right ratio and minimum size behavior.
    """
    splitter.setChildrenCollapsible(False)
    splitter.setStretchFactor(0, MAIN_HORIZONTAL_SPLITTER_LEFT_WEIGHT)
    splitter.setStretchFactor(1, MAIN_HORIZONTAL_SPLITTER_RIGHT_WEIGHT)

    right_widget = splitter.widget(1)
    if right_widget is not None:
        right_widget.setMinimumWidth(MAIN_HORIZONTAL_SPLITTER_RIGHT_MIN_WIDTH)

    behavior = MainHorizontalSplitterBehavior(splitter)
    splitter._main_horizontal_splitter_behavior = behavior  # keep QObject alive
    QTimer.singleShot(0, behavior.apply_initial_sizes_when_ready)

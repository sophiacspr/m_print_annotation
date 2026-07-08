from pathlib import Path
import sys

from PySide6.QtWidgets import QApplication

from frontend_pyside.main_window import MainWindow


def _apply_theme(app: QApplication) -> None:
    """Loads the application QSS theme."""
    theme_path = (
        Path(__file__).resolve().parent
        / "themes"
        / "tokyo_night_annotation_tool.qss"
    )

    if not theme_path.exists():
        raise FileNotFoundError(f"Theme file not found: {theme_path}")

    app.setStyleSheet(theme_path.read_text(encoding="utf-8"))


def run(controller) -> int:
    """Run the PySide6 frontend for an already constructed controller."""
    app = QApplication.instance() or QApplication(sys.argv)

    _apply_theme(app)

    window = MainWindow(controller)
    window.showMaximized()
    return app.exec()
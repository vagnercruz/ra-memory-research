"""Menu bar construction for the main window."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMessageBox

if TYPE_CHECKING:
    from ramr.ui.main_window import MainWindow


class MenuBarBuilder:
    """Builds the main window menu bar.

    Kept separate from :class:`MainWindow` so menu structure can grow
    without bloating the window class.
    """

    @staticmethod
    def build(window: MainWindow) -> None:
        menu_bar = window.menuBar()

        file_menu = menu_bar.addMenu("&File")
        exit_action = QAction("E&xit", window)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(window.close)
        file_menu.addAction(exit_action)

        view_menu = menu_bar.addMenu("&View")
        view_menu.addAction(window.project_dock.toggleViewAction())
        view_menu.addAction(window.inspector_dock.toggleViewAction())

        help_menu = menu_bar.addMenu("&Help")
        about_action = QAction("&About", window)
        about_action.triggered.connect(lambda: MenuBarBuilder._show_about_dialog(window))
        help_menu.addAction(about_action)

    @staticmethod
    def _show_about_dialog(window: MainWindow) -> None:
        QMessageBox.about(
            window,
            f"About {window.settings.application_name}",
            f"{window.settings.application_name} {window.settings.version}\n\n"
            "A memory research assistant for RetroAchievements developers.",
        )

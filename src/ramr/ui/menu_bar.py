"""Menu bar construction for the main window."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMenu, QMessageBox

if TYPE_CHECKING:
    from ramr.ui.main_window import MainWindow


@dataclass(slots=True)
class MainMenus:
    """Direct references to the menus of the main window.

    The window must keep this container alive: PySide6 invalidates menu
    wrappers reached through temporary ``actions()`` traversals, so menus
    are always accessed through these references instead.
    """

    file_menu: QMenu
    recent_projects_menu: QMenu
    view_menu: QMenu
    help_menu: QMenu


class MenuBarBuilder:
    """Builds the main window menu bar.

    Kept separate from :class:`MainWindow` so menu structure can grow
    without bloating the window class.
    """

    @staticmethod
    def build(window: MainWindow) -> MainMenus:
        menu_bar = window.menuBar()

        file_menu = menu_bar.addMenu("&File")

        new_project_action = QAction("&New Project…", window)
        new_project_action.setShortcut("Ctrl+N")
        new_project_action.triggered.connect(window.create_new_project)
        file_menu.addAction(new_project_action)

        open_project_action = QAction("&Open Project…", window)
        open_project_action.setShortcut("Ctrl+O")
        open_project_action.triggered.connect(window.open_project_with_picker)
        file_menu.addAction(open_project_action)

        recent_menu = file_menu.addMenu("Open &Recent")
        recent_menu.aboutToShow.connect(
            lambda: MenuBarBuilder._populate_recent_menu(window, recent_menu)
        )

        file_menu.addSeparator()

        close_project_action = QAction("&Close Project", window)
        close_project_action.triggered.connect(window.close_current_project)
        file_menu.addAction(close_project_action)

        file_menu.addSeparator()

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

        return MainMenus(
            file_menu=file_menu,
            recent_projects_menu=recent_menu,
            view_menu=view_menu,
            help_menu=help_menu,
        )

    @staticmethod
    def _populate_recent_menu(window: MainWindow, recent_menu: QMenu) -> None:
        recent_menu.clear()

        recent_directories = window.project_service.recent_projects()
        if not recent_directories:
            empty_action = QAction("No recent projects", window)
            empty_action.setEnabled(False)
            recent_menu.addAction(empty_action)
            return

        for directory in recent_directories:
            action = QAction(directory.name, window)
            action.setToolTip(str(directory))
            action.triggered.connect(
                lambda checked=False, path=directory: window.open_project_from_path(path)
            )
            recent_menu.addAction(action)

    @staticmethod
    def _show_about_dialog(window: MainWindow) -> None:
        QMessageBox.about(
            window,
            f"About {window.settings.application_name}",
            f"{window.settings.application_name} {window.settings.version}\n\n"
            "A memory research assistant for RetroAchievements developers.",
        )

from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMainWindow


class MenuBarBuilder:
    """
    Builds the application's menu bar.
    """

    @staticmethod
    def build(window: QMainWindow) -> None:
        menu_bar = window.menuBar()

        file_menu = menu_bar.addMenu("&File")
        project_menu = menu_bar.addMenu("&Project")
        tools_menu = menu_bar.addMenu("&Tools")
        help_menu = menu_bar.addMenu("&Help")

        exit_action = QAction("Exit", window)
        exit_action.triggered.connect(window.close)

        file_menu.addSeparator()
        file_menu.addAction(exit_action)
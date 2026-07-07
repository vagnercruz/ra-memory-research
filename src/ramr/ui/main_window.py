"""Main application window."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMainWindow

from ramr.core import constants
from ramr.core.settings import ApplicationSettings
from ramr.ui.docks.inspector_dock import InspectorDock
from ramr.ui.docks.project_dock import ProjectDock
from ramr.ui.menu_bar import MenuBarBuilder
from ramr.ui.status_bar import StatusBar
from ramr.ui.workspace import Workspace


class MainWindow(QMainWindow):
    """Top-level window hosting the central workspace and dockable panels."""

    def __init__(self, settings: ApplicationSettings) -> None:
        super().__init__()

        self.settings = settings

        self.setWindowTitle(settings.application_name)
        self.setMinimumSize(constants.WINDOW_MINIMUM_WIDTH, constants.WINDOW_MINIMUM_HEIGHT)

        self.workspace = Workspace()
        self.setCentralWidget(self.workspace)

        self.status_bar = StatusBar()
        self.setStatusBar(self.status_bar)

        self.project_dock = ProjectDock()
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.project_dock)

        self.inspector_dock = InspectorDock()
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.inspector_dock)

        MenuBarBuilder.build(self)

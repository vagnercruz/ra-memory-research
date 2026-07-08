"""Main application window."""

import logging
from pathlib import Path

from PySide6.QtCore import QStandardPaths, Qt, QTimer
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QFileDialog, QMainWindow, QMessageBox

from ramr.core import constants
from ramr.core.settings import ApplicationSettings
from ramr.domain.exceptions import EmulatorError, ProjectError
from ramr.domain.memory import ConnectionState
from ramr.services.emulator_service import EmulatorService
from ramr.services.project_service import ProjectService
from ramr.ui.dialogs.connect_emulator_dialog import ConnectEmulatorDialog
from ramr.ui.dialogs.new_project_dialog import NewProjectDialog
from ramr.ui.docks.inspector_dock import InspectorDock
from ramr.ui.docks.project_dock import ProjectDock
from ramr.ui.menu_bar import MenuBarBuilder
from ramr.ui.status_bar import StatusBar
from ramr.ui.workspace import Workspace

logger = logging.getLogger(__name__)

# How often to check that a connected emulator is still reachable.
CONNECTION_POLL_INTERVAL_MS = 1000

_CONNECTION_DESCRIPTIONS = {
    ConnectionState.DISCONNECTED: "No emulator connected",
    ConnectionState.LOST: "Connection lost",
}


class MainWindow(QMainWindow):
    """Top-level window hosting the central workspace and dockable panels.

    Presentation only: project and emulator actions delegate to their
    services and the window updates its views from the result.
    """

    def __init__(
        self,
        settings: ApplicationSettings,
        project_service: ProjectService,
        emulator_service: EmulatorService,
    ) -> None:
        super().__init__()

        self.settings = settings
        self.project_service = project_service
        self.emulator_service = emulator_service

        self.setMinimumSize(constants.WINDOW_MINIMUM_WIDTH, constants.WINDOW_MINIMUM_HEIGHT)

        self.workspace = Workspace()
        self.setCentralWidget(self.workspace)

        self.status_bar = StatusBar()
        self.setStatusBar(self.status_bar)

        self.project_dock = ProjectDock()
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.project_dock)

        self.inspector_dock = InspectorDock()
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.inspector_dock)

        self.menus = MenuBarBuilder.build(self)

        self._connection_timer = QTimer(self)
        self._connection_timer.setInterval(CONNECTION_POLL_INTERVAL_MS)
        self._connection_timer.timeout.connect(self.poll_connection)
        self._connection_timer.start()

        self._refresh_project_views()
        self._update_connection_views()

    # -- Project actions ---------------------------------------------------

    def create_new_project(self) -> None:
        """Ask for project data and create it through the service."""
        dialog = NewProjectDialog(self._default_projects_directory(), parent=self)
        if dialog.exec() != NewProjectDialog.DialogCode.Accepted:
            return

        try:
            project = self.project_service.create_project(
                name=dialog.project_name,
                system=dialog.system_name,
                parent_directory=dialog.parent_directory,
                notes=dialog.notes,
            )
        except ProjectError as error:
            self._show_error("Could not create the project.", error)
            return

        self._refresh_project_views()
        self.status_bar.showMessage(f"Project '{project.name}' created")

    def open_project_with_picker(self) -> None:
        """Ask for a project directory and open it."""
        directory = QFileDialog.getExistingDirectory(
            self, "Open Project", str(self._default_projects_directory())
        )
        if directory:
            self.open_project_from_path(Path(directory))

    def open_project_from_path(self, directory: Path) -> None:
        """Open the project stored at ``directory``."""
        try:
            project = self.project_service.open_project(directory)
        except ProjectError as error:
            self._show_error("Could not open the project.", error)
            return

        self._refresh_project_views()
        self.status_bar.showMessage(f"Project '{project.name}' opened")

    def close_current_project(self) -> None:
        """Save and close the open project."""
        self.project_service.close_project()
        self._refresh_project_views()
        self.status_bar.showMessage("Project closed")

    # -- Emulator actions --------------------------------------------------

    def connect_emulator(self) -> None:
        """Choose an emulator and connect to it through the service."""
        dialog = ConnectEmulatorDialog(self.emulator_service, parent=self)
        if dialog.exec() != ConnectEmulatorDialog.DialogCode.Accepted:
            return

        emulator_name = dialog.selected_emulator_name
        if emulator_name is None:
            return

        try:
            process = self.emulator_service.connect(emulator_name)
        except EmulatorError as error:
            self._show_error("Could not connect to the emulator.", error)
            self._update_connection_views()
            return

        self._update_connection_views()
        self.status_bar.showMessage(f"Connected to {emulator_name} (pid {process.pid})")

    def disconnect_emulator(self) -> None:
        """Disconnect the current emulator."""
        self.emulator_service.disconnect()
        self._update_connection_views()
        self.status_bar.showMessage("Emulator disconnected")

    def poll_connection(self) -> None:
        """Detect a dropped emulator connection and update the views."""
        previous_state = self.emulator_service.connection_state
        current_state = self.emulator_service.refresh_connection()
        if current_state != previous_state:
            self._update_connection_views()
            if current_state is ConnectionState.LOST:
                self.status_bar.showMessage("Emulator connection lost")

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802 (Qt naming)
        """Release resources before the window closes."""
        self._connection_timer.stop()
        self.emulator_service.disconnect()
        self.project_service.close_project()
        super().closeEvent(event)

    # -- View updates ------------------------------------------------------

    def _refresh_project_views(self) -> None:
        project = self.project_service.current_project
        if project is None:
            self.setWindowTitle(self.settings.application_name)
            self.project_dock.clear_project()
        else:
            self.setWindowTitle(f"{project.name} — {self.settings.application_name}")
            self.project_dock.show_project(project)

    def _update_connection_views(self) -> None:
        state = self.emulator_service.connection_state
        if state is ConnectionState.CONNECTED:
            description = f"Connected: {self.emulator_service.connected_emulator_name}"
        else:
            description = _CONNECTION_DESCRIPTIONS[state]

        self.status_bar.set_connection_state(description)
        self.menus.disconnect_emulator_action.setEnabled(state is ConnectionState.CONNECTED)

    def _show_error(self, summary: str, error: Exception) -> None:
        logger.warning("%s %s", summary, error)
        QMessageBox.warning(self, self.settings.application_name, f"{summary}\n\n{error}")

    @staticmethod
    def _default_projects_directory() -> Path:
        location = QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.DocumentsLocation
        )
        return Path(location)

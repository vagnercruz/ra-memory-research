"""Project explorer dock."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDockWidget, QListWidget


class ProjectDock(QDockWidget):
    """Lists the artifacts of the open project (snapshots, notes, exports)."""

    def __init__(self) -> None:
        super().__init__("Project Explorer")

        self.setObjectName("project_dock")
        self.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea
        )

        self.setWidget(QListWidget())

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QListWidget
from PySide6.QtWidgets import QDockWidget


class ProjectDock(QDockWidget):
    """
    Displays the current project structure.
    """

    def __init__(self) -> None:
        super().__init__("Project Explorer")

        self.setAllowedAreas(
            Qt.LeftDockWidgetArea
        )

        self.setWidget(
            QListWidget()
        )
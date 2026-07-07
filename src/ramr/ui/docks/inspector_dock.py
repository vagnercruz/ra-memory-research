"""Address inspector dock."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDockWidget, QLabel


class InspectorDock(QDockWidget):
    """Shows details about the selected address (value, history, notes)."""

    def __init__(self) -> None:
        super().__init__("Inspector")

        self.setObjectName("inspector_dock")
        self.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea
        )

        placeholder = QLabel("Nothing selected")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setWidget(placeholder)

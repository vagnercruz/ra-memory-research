from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QDockWidget


class InspectorDock(QDockWidget):
    """
    Displays information about the selected object.
    """

    def __init__(self) -> None:
        super().__init__("Inspector")

        self.setAllowedAreas(
            Qt.RightDockWidgetArea
        )

        self.setWidget(
            QLabel("Nothing selected")
        )
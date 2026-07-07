"""Central workspace widget."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

PLACEHOLDER_TEXT = "Open a project to start researching memory"


class Workspace(QWidget):
    """Central area that will host snapshot and comparison views."""

    def __init__(self) -> None:
        super().__init__()

        layout = QVBoxLayout(self)

        placeholder = QLabel(PLACEHOLDER_TEXT)
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(placeholder)

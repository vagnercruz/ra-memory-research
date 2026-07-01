from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QWidget
from PySide6.QtWidgets import QVBoxLayout


class Workspace(QWidget):
    """
    Central workspace.
    """

    def __init__(self) -> None:
        super().__init__()

        layout = QVBoxLayout(self)

        layout.addWidget(
            QLabel("Workspace")
        )
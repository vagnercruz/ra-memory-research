from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QStatusBar


class StatusBar(QStatusBar):
    """
    Main application status bar.
    """

    def __init__(self) -> None:
        super().__init__()

        self.status = QLabel("Ready")

        self.addWidget(self.status)

        self.showMessage("Application initialized")
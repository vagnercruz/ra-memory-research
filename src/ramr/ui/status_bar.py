"""Main window status bar."""

from PySide6.QtWidgets import QLabel, QStatusBar

READY_MESSAGE = "Ready"
DISCONNECTED_MESSAGE = "No emulator connected"


class StatusBar(QStatusBar):
    """Status bar showing transient messages and the emulator connection state."""

    def __init__(self) -> None:
        super().__init__()

        self.connection_label = QLabel(DISCONNECTED_MESSAGE)
        self.addPermanentWidget(self.connection_label)

        self.showMessage(READY_MESSAGE)

    def set_connection_state(self, description: str) -> None:
        """Update the permanent emulator connection indicator."""
        self.connection_label.setText(description)

from PySide6.QtWidgets import QApplication

from src.ui.main_window import MainWindow


class Application:
    """
    Application bootstrap class.
    Responsible for initializing the GUI and starting the event loop.
    """

    def __init__(self) -> None:
        self.qt_app = QApplication([])
        self.main_window = MainWindow()

    def run(self) -> None:
        """Start the application."""

        self.main_window.show()
        self.qt_app.exec()
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QMainWindow


class MainWindow(QMainWindow):
    """
    Main application window.
    """

    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("RA Memory Research")

        self.setMinimumSize(1000, 700)

        label = QLabel("RA Memory Research", self)
        label.move(20, 20)
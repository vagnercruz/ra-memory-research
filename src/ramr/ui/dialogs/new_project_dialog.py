"""Dialog collecting the data needed to create a new project."""

from pathlib import Path

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

# Prepopulated suggestions only; the combo box stays editable so any
# RetroAchievements-supported system can be typed in.
COMMON_SYSTEM_NAMES = (
    "PlayStation",
    "PlayStation 2",
    "Nintendo 64",
    "SNES",
    "NES",
    "Game Boy Advance",
    "Mega Drive",
    "Saturn",
    "Dreamcast",
    "GameCube",
)

NOTES_FIELD_HEIGHT = 80


class NewProjectDialog(QDialog):
    """Collects name, system, location, and optional notes for a new project.

    The dialog only gathers input; project creation itself stays in the
    service layer.
    """

    def __init__(self, default_parent_directory: Path, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.setWindowTitle("New Project")
        self.setModal(True)

        self._name_edit = QLineEdit()
        self._name_edit.setPlaceholderText("Game name, e.g. Castlevania")

        self._system_combo = QComboBox()
        self._system_combo.setEditable(True)
        self._system_combo.addItems(COMMON_SYSTEM_NAMES)

        self._location_edit = QLineEdit(str(default_parent_directory))
        browse_button = QPushButton("Browse…")
        browse_button.clicked.connect(self._browse_for_location)
        location_row = QHBoxLayout()
        location_row.addWidget(self._location_edit)
        location_row.addWidget(browse_button)

        self._notes_edit = QPlainTextEdit()
        self._notes_edit.setPlaceholderText("Optional research notes")
        self._notes_edit.setFixedHeight(NOTES_FIELD_HEIGHT)

        form = QFormLayout()
        form.addRow("&Name:", self._name_edit)
        form.addRow("&System:", self._system_combo)
        form.addRow("&Location:", location_row)
        form.addRow("N&otes:", self._notes_edit)

        self._buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self._buttons.accepted.connect(self.accept)
        self._buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(self._buttons)

        self._name_edit.textChanged.connect(self._update_ok_button)
        self._location_edit.textChanged.connect(self._update_ok_button)
        self._update_ok_button()

    @property
    def project_name(self) -> str:
        return self._name_edit.text().strip()

    @property
    def system_name(self) -> str:
        return self._system_combo.currentText().strip()

    @property
    def parent_directory(self) -> Path:
        return Path(self._location_edit.text().strip())

    @property
    def notes(self) -> str:
        return self._notes_edit.toPlainText()

    def _browse_for_location(self) -> None:
        directory = QFileDialog.getExistingDirectory(
            self, "Choose Project Location", self._location_edit.text()
        )
        if directory:
            self._location_edit.setText(directory)

    def _update_ok_button(self) -> None:
        ok_button = self._buttons.button(QDialogButtonBox.StandardButton.Ok)
        ok_button.setEnabled(bool(self.project_name) and bool(self._location_edit.text().strip()))

"""Dialog for choosing which emulator to connect to."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QDialogButtonBox,
    QHeaderView,
    QLabel,
    QPushButton,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ramr.services.emulator_service import EmulatorService

NOT_RUNNING_STATUS = "Not running"
RUNNING_STATUS = "Running (pid {pid})"

# Row payload: the emulator name is stored on the item so selection maps
# straight back to a provider without parsing the label.
_EMULATOR_NAME_ROLE = Qt.ItemDataRole.UserRole


class ConnectEmulatorDialog(QDialog):
    """Lists registered emulators with their detected status.

    The dialog only selects an emulator; the window performs the actual
    connection through the service so error handling stays in one place.
    """

    def __init__(self, service: EmulatorService, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self._service = service

        self.setWindowTitle("Connect Emulator")
        self.setModal(True)

        self._tree = QTreeWidget()
        self._tree.setColumnCount(2)
        self._tree.setHeaderLabels(["Emulator", "Status"])
        self._tree.setRootIsDecorated(False)
        self._tree.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self._tree.itemSelectionChanged.connect(self._update_ok_button)
        self._tree.itemDoubleClicked.connect(self._accept_if_running)

        refresh_button = QPushButton("&Refresh")
        refresh_button.clicked.connect(self.refresh)

        self._buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self._buttons.addButton(refresh_button, QDialogButtonBox.ButtonRole.ActionRole)
        self._buttons.accepted.connect(self.accept)
        self._buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Select an emulator to connect to:"))
        layout.addWidget(self._tree)
        layout.addWidget(self._buttons)

        self.refresh()

    @property
    def selected_emulator_name(self) -> str | None:
        items = self._tree.selectedItems()
        if not items:
            return None
        return items[0].data(0, _EMULATOR_NAME_ROLE)

    def refresh(self) -> None:
        """Rebuild the list from the service's current detection results."""
        self._tree.clear()

        running_pids = {
            detected.emulator_name: detected.process.pid
            for detected in self._service.detect_emulators()
        }

        for name in self._service.provider_names():
            pid = running_pids.get(name)
            status = RUNNING_STATUS.format(pid=pid) if pid is not None else NOT_RUNNING_STATUS
            item = QTreeWidgetItem([name, status])
            item.setData(0, _EMULATOR_NAME_ROLE, name)
            if pid is None:
                # Disable rows that cannot be connected right now.
                item.setFlags(Qt.ItemFlag.ItemIsSelectable & Qt.ItemFlag.NoItemFlags)
                item.setDisabled(True)
            self._tree.addTopLevelItem(item)

        self._update_ok_button()

    def _accept_if_running(self, item: QTreeWidgetItem) -> None:
        if not item.isDisabled():
            self.accept()

    def _update_ok_button(self) -> None:
        ok_button = self._buttons.button(QDialogButtonBox.StandardButton.Ok)
        ok_button.setEnabled(self.selected_emulator_name is not None)

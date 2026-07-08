"""Tests for the connect emulator dialog."""

from PySide6.QtWidgets import QDialogButtonBox
from pytestqt.qtbot import QtBot

from ramr.infrastructure.memory.fake_provider import FakeMemoryProvider
from ramr.infrastructure.memory.registry import MemoryProviderRegistry
from ramr.services.emulator_service import EmulatorService
from ramr.ui.dialogs.connect_emulator_dialog import (
    NOT_RUNNING_STATUS,
    ConnectEmulatorDialog,
)


def make_service(*providers: FakeMemoryProvider) -> EmulatorService:
    return EmulatorService(MemoryProviderRegistry(providers))


def make_dialog(qtbot: QtBot, service: EmulatorService) -> ConnectEmulatorDialog:
    dialog = ConnectEmulatorDialog(service)
    qtbot.addWidget(dialog)
    return dialog


def _ok_button(dialog: ConnectEmulatorDialog):
    return dialog._buttons.button(QDialogButtonBox.StandardButton.Ok)


def test_lists_all_providers_with_status(qtbot: QtBot) -> None:
    service = make_service(
        FakeMemoryProvider(emulator_name="Running", detectable=True),
        FakeMemoryProvider(emulator_name="Stopped", detectable=False),
    )

    dialog = make_dialog(qtbot, service)
    tree = dialog._tree

    rows = {
        tree.topLevelItem(index).text(0): tree.topLevelItem(index)
        for index in range(tree.topLevelItemCount())
    }
    assert set(rows) == {"Running", "Stopped"}
    assert rows["Stopped"].text(1) == NOT_RUNNING_STATUS
    assert rows["Stopped"].isDisabled()
    assert not rows["Running"].isDisabled()


def test_ok_disabled_until_running_emulator_selected(qtbot: QtBot) -> None:
    service = make_service(FakeMemoryProvider(emulator_name="Running", detectable=True))
    dialog = make_dialog(qtbot, service)

    assert not _ok_button(dialog).isEnabled()

    dialog._tree.topLevelItem(0).setSelected(True)

    assert _ok_button(dialog).isEnabled()
    assert dialog.selected_emulator_name == "Running"


def test_refresh_reflects_newly_started_emulator(qtbot: QtBot) -> None:
    provider = FakeMemoryProvider(emulator_name="Fake", detectable=False)
    dialog = make_dialog(qtbot, make_service(provider))
    assert dialog._tree.topLevelItem(0).isDisabled()

    provider.set_detectable(True)
    dialog.refresh()

    assert not dialog._tree.topLevelItem(0).isDisabled()


def test_no_selection_returns_none(qtbot: QtBot) -> None:
    service = make_service(FakeMemoryProvider(emulator_name="Running", detectable=True))
    dialog = make_dialog(qtbot, service)

    assert dialog.selected_emulator_name is None

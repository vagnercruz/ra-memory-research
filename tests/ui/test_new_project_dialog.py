"""Tests for the new project dialog."""

from pathlib import Path

import pytest
from PySide6.QtWidgets import QDialogButtonBox
from pytestqt.qtbot import QtBot

from ramr.ui.dialogs.new_project_dialog import NewProjectDialog


@pytest.fixture
def dialog(qtbot: QtBot, tmp_path: Path) -> NewProjectDialog:
    dialog = NewProjectDialog(default_parent_directory=tmp_path)
    qtbot.addWidget(dialog)
    return dialog


def _ok_button(dialog: NewProjectDialog):
    return dialog._buttons.button(QDialogButtonBox.StandardButton.Ok)


def test_ok_is_disabled_until_name_is_entered(dialog: NewProjectDialog) -> None:
    assert not _ok_button(dialog).isEnabled()

    dialog._name_edit.setText("Castlevania")

    assert _ok_button(dialog).isEnabled()


def test_ok_is_disabled_for_blank_name(dialog: NewProjectDialog) -> None:
    dialog._name_edit.setText("   ")

    assert not _ok_button(dialog).isEnabled()


def test_properties_expose_stripped_values(dialog: NewProjectDialog, tmp_path: Path) -> None:
    dialog._name_edit.setText("  Castlevania  ")
    dialog._system_combo.setCurrentText("PlayStation 2")
    dialog._notes_edit.setPlainText("HP research")

    assert dialog.project_name == "Castlevania"
    assert dialog.system_name == "PlayStation 2"
    assert dialog.parent_directory == tmp_path
    assert dialog.notes == "HP research"


def test_location_defaults_to_provided_directory(dialog: NewProjectDialog, tmp_path: Path) -> None:
    assert dialog.parent_directory == tmp_path

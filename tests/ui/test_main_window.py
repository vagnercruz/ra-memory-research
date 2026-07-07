"""Smoke tests for the main window shell."""

import pytest
from pytestqt.qtbot import QtBot

from ramr.core import constants
from ramr.core.settings import ApplicationSettings
from ramr.ui.main_window import MainWindow


@pytest.fixture
def main_window(qtbot: QtBot) -> MainWindow:
    window = MainWindow(ApplicationSettings())
    qtbot.addWidget(window)
    return window


def test_window_title_comes_from_settings(main_window: MainWindow) -> None:
    assert main_window.windowTitle() == constants.APPLICATION_NAME


def test_window_enforces_minimum_size(main_window: MainWindow) -> None:
    assert main_window.minimumWidth() == constants.WINDOW_MINIMUM_WIDTH
    assert main_window.minimumHeight() == constants.WINDOW_MINIMUM_HEIGHT


def test_shell_widgets_are_installed(main_window: MainWindow) -> None:
    assert main_window.centralWidget() is main_window.workspace
    assert main_window.statusBar() is main_window.status_bar
    assert main_window.project_dock.parent() is main_window
    assert main_window.inspector_dock.parent() is main_window


def test_menu_bar_contains_expected_menus(main_window: MainWindow) -> None:
    menu_titles = [action.text() for action in main_window.menuBar().actions()]

    assert menu_titles == ["&File", "&View", "&Help"]


def test_view_menu_toggles_dock_visibility(main_window: MainWindow, qtbot: QtBot) -> None:
    main_window.show()
    assert main_window.project_dock.isVisible()

    toggle_action = main_window.project_dock.toggleViewAction()
    toggle_action.trigger()

    assert not main_window.project_dock.isVisible()

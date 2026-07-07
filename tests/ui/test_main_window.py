"""Tests for the main window shell and its project flows."""

from collections.abc import Iterator
from pathlib import Path

import pytest
from pytestqt.qtbot import QtBot

from ramr.core import constants
from ramr.core.settings import ApplicationSettings
from ramr.infrastructure.filesystem.project_repository import ProjectRepository
from ramr.infrastructure.filesystem.recent_projects import RecentProjectsStore
from ramr.services.project_service import ProjectService
from ramr.ui.main_window import MainWindow
from ramr.ui.menu_bar import MenuBarBuilder


@pytest.fixture
def project_service(tmp_path: Path) -> Iterator[ProjectService]:
    service = ProjectService(
        repository=ProjectRepository(),
        recent_projects=RecentProjectsStore(tmp_path / "recent_projects.json"),
    )
    yield service
    service.close_project()


@pytest.fixture
def main_window(qtbot: QtBot, project_service: ProjectService) -> MainWindow:
    window = MainWindow(ApplicationSettings(), project_service)
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


def test_opening_project_updates_title(
    main_window: MainWindow, project_service: ProjectService, tmp_path: Path
) -> None:
    project = project_service.create_project("Castlevania", "PlayStation 2", tmp_path)
    project_service.close_project()

    main_window.open_project_from_path(project.root_directory)

    assert main_window.windowTitle() == f"Castlevania — {constants.APPLICATION_NAME}"


def test_closing_project_resets_title(
    main_window: MainWindow, project_service: ProjectService, tmp_path: Path
) -> None:
    project = project_service.create_project("Castlevania", "PlayStation 2", tmp_path)
    project_service.close_project()
    main_window.open_project_from_path(project.root_directory)

    main_window.close_current_project()

    assert main_window.windowTitle() == constants.APPLICATION_NAME
    assert not project_service.has_open_project


def test_opening_invalid_directory_reports_error(
    main_window: MainWindow, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    reported: list[str] = []
    monkeypatch.setattr(
        "ramr.ui.main_window.QMessageBox.warning",
        lambda parent, title, text: reported.append(text),
    )

    main_window.open_project_from_path(tmp_path / "not-a-project")

    assert len(reported) == 1
    assert "Could not open the project." in reported[0]
    assert main_window.windowTitle() == constants.APPLICATION_NAME


def test_recent_menu_lists_projects_most_recent_first(
    main_window: MainWindow, project_service: ProjectService, tmp_path: Path
) -> None:
    project_service.create_project("First", "SNES", tmp_path)
    project_service.create_project("Second", "SNES", tmp_path)

    recent_menu = main_window.menus.recent_projects_menu
    MenuBarBuilder._populate_recent_menu(main_window, recent_menu)

    labels = [action.text() for action in recent_menu.actions()]
    assert labels == ["Second", "First"]


def test_recent_menu_shows_placeholder_when_empty(main_window: MainWindow) -> None:
    recent_menu = main_window.menus.recent_projects_menu
    MenuBarBuilder._populate_recent_menu(main_window, recent_menu)

    actions = recent_menu.actions()
    assert [action.text() for action in actions] == ["No recent projects"]
    assert not actions[0].isEnabled()

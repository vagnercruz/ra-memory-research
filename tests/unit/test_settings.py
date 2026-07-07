"""Tests for application settings."""

from ramr import __version__
from ramr.core import constants
from ramr.core.settings import ApplicationSettings


def test_default_settings_match_application_constants() -> None:
    settings = ApplicationSettings()

    assert settings.application_name == constants.APPLICATION_NAME
    assert settings.organization_name == constants.ORGANIZATION_NAME
    assert settings.version == __version__


def test_settings_accept_overrides() -> None:
    settings = ApplicationSettings(application_name="Custom Name")

    assert settings.application_name == "Custom Name"

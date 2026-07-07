"""Global application settings."""

from dataclasses import dataclass

from ramr import __version__
from ramr.core import constants


@dataclass(slots=True)
class ApplicationSettings:
    """Runtime configuration for one application instance.

    Defaults come from :mod:`ramr.core.constants`; user-facing preferences
    (theme, recent projects, window state) will be persisted here in a
    later sprint through an infrastructure-backed store.
    """

    application_name: str = constants.APPLICATION_NAME
    organization_name: str = constants.ORGANIZATION_NAME
    version: str = __version__

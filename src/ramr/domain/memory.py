"""Value objects describing an emulator process and connection state."""

from dataclasses import dataclass
from enum import Enum


class ConnectionState(Enum):
    """State of the link between the application and an emulator."""

    DISCONNECTED = "disconnected"
    CONNECTED = "connected"
    LOST = "lost"


@dataclass(frozen=True, slots=True)
class EmulatorProcess:
    """A running emulator process the application can attach to.

    ``executable_path`` may be ``None`` when the operating system does not
    expose it (for example, insufficient permissions).
    """

    pid: int
    name: str
    executable_path: str | None = None

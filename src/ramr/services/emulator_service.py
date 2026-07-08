"""Use cases for connecting to emulators and reading their memory."""

import logging
from dataclasses import dataclass

from ramr.domain.exceptions import NotConnectedError
from ramr.domain.memory import ConnectionState, EmulatorProcess
from ramr.domain.memory_provider import MemoryProvider
from ramr.infrastructure.memory.registry import MemoryProviderRegistry

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class DetectedEmulator:
    """A registered emulator found running, ready to connect."""

    emulator_name: str
    process: EmulatorProcess


class EmulatorService:
    """Owns the connection to at most one emulator at a time.

    The UI talks to this service instead of touching providers directly, so
    connection state, provider selection, and reads stay coordinated in one
    place.
    """

    def __init__(self, registry: MemoryProviderRegistry) -> None:
        self._registry = registry
        self._connected_provider: MemoryProvider | None = None
        self._state = ConnectionState.DISCONNECTED

    @property
    def connection_state(self) -> ConnectionState:
        return self._state

    @property
    def connected_emulator_name(self) -> str | None:
        if self._connected_provider is None:
            return None
        return self._connected_provider.emulator_name

    @property
    def is_connected(self) -> bool:
        return self._state is ConnectionState.CONNECTED

    def provider_names(self) -> list[str]:
        """Names of every registered emulator, whether running or not."""
        return self._registry.names()

    def detect_emulators(self) -> list[DetectedEmulator]:
        """Registered emulators that are currently running."""
        detected: list[DetectedEmulator] = []
        for provider in self._registry.all():
            process = provider.detect()
            if process is not None:
                detected.append(DetectedEmulator(provider.emulator_name, process))
        return detected

    def connect(self, emulator_name: str) -> EmulatorProcess:
        """Connect to ``emulator_name``, replacing any existing connection.

        Raises:
            MemoryProviderError: if the name is not registered or attaching fails.
            EmulatorNotFoundError: if the emulator is not running.
        """
        provider = self._registry.get(emulator_name)
        self.disconnect()

        process = provider.connect()
        self._connected_provider = provider
        self._state = ConnectionState.CONNECTED
        logger.info("Emulator '%s' connected (pid %d)", emulator_name, process.pid)
        return process

    def disconnect(self) -> None:
        """Disconnect the current emulator; no-op when none is connected."""
        if self._connected_provider is not None:
            self._connected_provider.disconnect()
            logger.info("Emulator '%s' disconnected", self._connected_provider.emulator_name)
        self._connected_provider = None
        self._state = ConnectionState.DISCONNECTED

    def refresh_connection(self) -> ConnectionState:
        """Detect a dropped connection (e.g. the emulator was closed).

        Marks the state ``LOST`` and releases the provider if a previously
        connected emulator is no longer reachable. Returns the current state.
        """
        if (
            self._state is ConnectionState.CONNECTED
            and self._connected_provider is not None
            and not self._connected_provider.is_connected
        ):
            logger.warning("Lost connection to '%s'", self._connected_provider.emulator_name)
            self._connected_provider.disconnect()
            self._connected_provider = None
            self._state = ConnectionState.LOST
        return self._state

    def read_bytes(self, guest_address: int, size: int) -> bytes:
        """Read ``size`` bytes from the connected emulator at ``guest_address``.

        Raises:
            NotConnectedError: if no emulator is connected.
            MemoryReadError: if the read fails.
        """
        if self._connected_provider is None or self._state is not ConnectionState.CONNECTED:
            raise NotConnectedError("No emulator is connected.")
        return self._connected_provider.read_bytes(guest_address, size)

"""Base memory provider for emulators read through their host process."""

import logging
from abc import abstractmethod

from ramr.domain.exceptions import EmulatorNotFoundError, NotConnectedError
from ramr.domain.memory import EmulatorProcess
from ramr.domain.memory_provider import MemoryProvider
from ramr.infrastructure.memory.ports import MemoryReader, ProcessLocator
from ramr.infrastructure.memory.process_locator import EmulatorProcessLocator
from ramr.infrastructure.memory.process_reader import ProcessMemoryReader

logger = logging.getLogger(__name__)


class ProcessMemoryProvider(MemoryProvider):
    """Reads a guest console's RAM out of an emulator's host process.

    Subclasses declare which executables identify the emulator and how to
    resolve the *host* address of guest RAM base once connected. The reader
    and locator are injected so the connect/translate/read flow can be
    tested without a real emulator.
    """

    def __init__(
        self,
        reader: MemoryReader | None = None,
        locator: ProcessLocator | None = None,
    ) -> None:
        self._reader: MemoryReader = reader or ProcessMemoryReader()
        self._locator: ProcessLocator = locator or EmulatorProcessLocator()
        self._process: EmulatorProcess | None = None
        self._host_base: int | None = None

    @abstractmethod
    def _resolve_host_base(self, reader: MemoryReader, process: EmulatorProcess) -> int:
        """Return the host address where the console's guest RAM begins.

        Raises:
            MemoryProviderError: if the base cannot be determined.
        """

    def detect(self) -> EmulatorProcess | None:
        return self._locator.find(self.process_names)

    def connect(self) -> EmulatorProcess:
        process = self.detect()
        if process is None:
            raise EmulatorNotFoundError(f"{self.emulator_name} is not running.")

        self._reader.open(process.pid)
        try:
            self._host_base = self._resolve_host_base(self._reader, process)
        except Exception:
            self._reader.close()
            raise

        self._process = process
        logger.info("Connected to %s (pid %d)", self.emulator_name, process.pid)
        return process

    def disconnect(self) -> None:
        self._reader.close()
        self._process = None
        self._host_base = None

    @property
    def is_connected(self) -> bool:
        return self._process is not None and self._reader.is_open

    def read_bytes(self, guest_address: int, size: int) -> bytes:
        if not self.is_connected or self._host_base is None:
            raise NotConnectedError(f"{self.emulator_name} is not connected.")
        return self._reader.read(self._host_base + guest_address, size)

"""The memory provider port.

This abstraction is the boundary between the application and any emulator.
Services depend on :class:`MemoryProvider`; concrete adapters live in
``ramr.infrastructure.memory`` so new emulators never ripple upward.
"""

from abc import ABC, abstractmethod

from ramr.domain.memory import EmulatorProcess


class MemoryProvider(ABC):
    """Reads memory from one emulator, identified by its process.

    Guest addresses passed to :meth:`read_bytes` are console-relative (the
    same addresses RetroAchievements uses). Each provider is responsible for
    translating them to the emulator's host process memory.
    """

    @property
    @abstractmethod
    def emulator_name(self) -> str:
        """Human-readable name of the emulator this provider targets."""

    @property
    @abstractmethod
    def process_names(self) -> tuple[str, ...]:
        """Executable names that identify this emulator's process."""

    @abstractmethod
    def detect(self) -> EmulatorProcess | None:
        """Return the running emulator process, or ``None`` if not running."""

    @abstractmethod
    def connect(self) -> EmulatorProcess:
        """Attach to the running emulator.

        Raises:
            EmulatorNotFoundError: if no matching process is running.
            MemoryProviderError: if attaching or locating guest memory fails.
        """

    @abstractmethod
    def disconnect(self) -> None:
        """Detach from the emulator; safe to call when not connected."""

    @property
    @abstractmethod
    def is_connected(self) -> bool:
        """Whether the provider currently holds a live connection."""

    @abstractmethod
    def read_bytes(self, guest_address: int, size: int) -> bytes:
        """Read ``size`` bytes starting at ``guest_address``.

        Raises:
            NotConnectedError: if the provider is not connected.
            MemoryReadError: if the read fails or returns fewer bytes.
        """

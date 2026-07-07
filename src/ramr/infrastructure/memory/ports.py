"""Infrastructure ports shared by memory providers.

These protocols let process-backed providers depend on small, swappable
collaborators (a memory reader and a process locator) so they can be
tested with in-memory fakes instead of a live emulator.
"""

from collections.abc import Sequence
from typing import Protocol

from ramr.domain.memory import EmulatorProcess


class MemoryReader(Protocol):
    """Reads raw bytes from an already-located address space."""

    @property
    def is_open(self) -> bool: ...

    def open(self, pid: int) -> None: ...

    def close(self) -> None: ...

    def read(self, address: int, size: int) -> bytes: ...


class ProcessLocator(Protocol):
    """Finds a running process by one of several executable names."""

    def find(self, process_names: Sequence[str]) -> EmulatorProcess | None: ...

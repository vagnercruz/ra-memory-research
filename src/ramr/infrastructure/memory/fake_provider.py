"""In-memory memory provider for offline development and tests."""

from ramr.domain.exceptions import (
    EmulatorNotFoundError,
    MemoryReadError,
    NotConnectedError,
)
from ramr.domain.memory import EmulatorProcess
from ramr.domain.memory_provider import MemoryProvider

FAKE_PROCESS_PID = 4242


class FakeMemoryProvider(MemoryProvider):
    """A provider backed by a bytearray instead of a real emulator.

    It supports the whole provider contract so the UI and services can be
    exercised without an emulator running. Tests can seed the memory buffer
    and toggle whether the emulator appears to be running.
    """

    def __init__(
        self,
        emulator_name: str = "Fake Emulator",
        process_names: tuple[str, ...] = ("fake-emulator.exe",),
        memory: bytes | bytearray = b"",
        detectable: bool = True,
    ) -> None:
        self._emulator_name = emulator_name
        self._process_names = process_names
        self._memory = bytearray(memory)
        self._detectable = detectable
        self._connected = False

    @property
    def emulator_name(self) -> str:
        return self._emulator_name

    @property
    def process_names(self) -> tuple[str, ...]:
        return self._process_names

    def set_detectable(self, detectable: bool) -> None:
        """Control whether the fake emulator appears to be running."""
        self._detectable = detectable

    def write_bytes(self, address: int, data: bytes) -> None:
        """Seed the backing buffer, growing it if needed."""
        end = address + len(data)
        if end > len(self._memory):
            self._memory.extend(b"\x00" * (end - len(self._memory)))
        self._memory[address:end] = data

    def detect(self) -> EmulatorProcess | None:
        if not self._detectable:
            return None
        return EmulatorProcess(pid=FAKE_PROCESS_PID, name=self._process_names[0])

    def connect(self) -> EmulatorProcess:
        process = self.detect()
        if process is None:
            raise EmulatorNotFoundError(f"{self._emulator_name} is not running.")
        self._connected = True
        return process

    def disconnect(self) -> None:
        self._connected = False

    @property
    def is_connected(self) -> bool:
        return self._connected

    def read_bytes(self, guest_address: int, size: int) -> bytes:
        if not self._connected:
            raise NotConnectedError(f"{self._emulator_name} is not connected.")
        if size <= 0:
            raise MemoryReadError(f"Read size must be positive, got {size}.")
        if guest_address < 0 or guest_address + size > len(self._memory):
            raise MemoryReadError(
                f"Read of {size} bytes at {guest_address:#x} is out of bounds "
                f"(memory size {len(self._memory)})."
            )
        return bytes(self._memory[guest_address : guest_address + size])

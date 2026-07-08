"""Tests for the process-backed provider base and the PCSX2 provider."""

import pytest

from ramr.domain.exceptions import (
    EmulatorNotFoundError,
    MemoryProviderError,
    NotConnectedError,
)
from ramr.domain.memory import EmulatorProcess
from ramr.infrastructure.memory.buffer_reader import BufferMemoryReader
from ramr.infrastructure.memory.pcsx2_provider import Pcsx2Provider
from ramr.infrastructure.memory.ports import MemoryReader
from ramr.infrastructure.memory.process_provider import ProcessMemoryProvider

_HOST_BASE = 0x100


class _StubLocator:
    def __init__(self, process: EmulatorProcess | None) -> None:
        self._process = process
        self.requested_names: list[str] = []

    def find(self, process_names):
        self.requested_names = list(process_names)
        return self._process


class _FixedBaseProvider(ProcessMemoryProvider):
    """Concrete provider that resolves a known host base for testing."""

    emulator_name = "Stub Emulator"
    process_names = ("stub.exe",)

    def _resolve_host_base(self, reader: MemoryReader, process: EmulatorProcess) -> int:
        return _HOST_BASE


def make_provider(
    *, detectable: bool = True, buffer: bytes = bytes(512)
) -> tuple[_FixedBaseProvider, BufferMemoryReader]:
    process = EmulatorProcess(pid=99, name="stub.exe") if detectable else None
    reader = BufferMemoryReader(buffer)
    provider = _FixedBaseProvider(reader=reader, locator=_StubLocator(process))
    return provider, reader


def test_connect_opens_reader_and_translates_addresses() -> None:
    buffer = bytearray(512)
    buffer[_HOST_BASE + 8 : _HOST_BASE + 11] = b"\x01\x02\x03"
    provider, reader = make_provider(buffer=bytes(buffer))

    provider.connect()

    assert provider.is_connected
    assert reader.is_open
    # Guest offset 8 maps to host address _HOST_BASE + 8.
    assert provider.read_bytes(8, 3) == b"\x01\x02\x03"


def test_connect_without_process_raises_and_leaves_reader_closed() -> None:
    provider, reader = make_provider(detectable=False)

    with pytest.raises(EmulatorNotFoundError):
        provider.connect()

    assert not reader.is_open
    assert not provider.is_connected


def test_read_before_connect_raises() -> None:
    provider, _ = make_provider()

    with pytest.raises(NotConnectedError):
        provider.read_bytes(0, 1)


def test_disconnect_closes_reader() -> None:
    provider, reader = make_provider()
    provider.connect()

    provider.disconnect()

    assert not reader.is_open
    assert not provider.is_connected


def test_base_resolution_failure_closes_reader() -> None:
    class _FailingProvider(ProcessMemoryProvider):
        emulator_name = "Failing"
        process_names = ("stub.exe",)

        def _resolve_host_base(self, reader, process):
            raise MemoryProviderError("cannot resolve base")

    reader = BufferMemoryReader(bytes(16))
    provider = _FailingProvider(
        reader=reader, locator=_StubLocator(EmulatorProcess(pid=1, name="stub.exe"))
    )

    with pytest.raises(MemoryProviderError):
        provider.connect()

    assert not reader.is_open


def test_pcsx2_uses_known_process_names() -> None:
    assert "pcsx2-qt.exe" in Pcsx2Provider.process_names
    assert Pcsx2Provider.emulator_name == "PCSX2"


def test_pcsx2_without_calibration_raises_on_connect() -> None:
    reader = BufferMemoryReader(bytes(16))
    provider = Pcsx2Provider(
        reader=reader, locator=_StubLocator(EmulatorProcess(pid=1, name="pcsx2-qt.exe"))
    )

    with pytest.raises(MemoryProviderError, match="not calibrated"):
        provider.connect()

    assert not reader.is_open


def test_pcsx2_with_override_reads_translated_bytes() -> None:
    buffer = bytearray(256)
    buffer[0x40:0x44] = b"\xaa\xbb\xcc\xdd"
    reader = BufferMemoryReader(bytes(buffer))
    provider = Pcsx2Provider(
        guest_base_override=0x40,
        reader=reader,
        locator=_StubLocator(EmulatorProcess(pid=1, name="pcsx2-qt.exe")),
    )

    provider.connect()

    assert provider.read_bytes(0, 4) == b"\xaa\xbb\xcc\xdd"

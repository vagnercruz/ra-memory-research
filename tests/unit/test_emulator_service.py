"""Tests for the emulator service."""

import pytest

from ramr.domain.exceptions import EmulatorNotFoundError, NotConnectedError
from ramr.domain.memory import ConnectionState
from ramr.infrastructure.memory.fake_provider import FakeMemoryProvider
from ramr.infrastructure.memory.registry import MemoryProviderRegistry
from ramr.services.emulator_service import EmulatorService


def make_service(*providers: FakeMemoryProvider) -> EmulatorService:
    return EmulatorService(MemoryProviderRegistry(providers))


def test_starts_disconnected() -> None:
    service = make_service(FakeMemoryProvider(emulator_name="Fake"))

    assert service.connection_state is ConnectionState.DISCONNECTED
    assert not service.is_connected
    assert service.connected_emulator_name is None


def test_connect_updates_state_and_allows_reads() -> None:
    provider = FakeMemoryProvider(emulator_name="Fake", memory=bytes(range(8)))
    service = make_service(provider)

    process = service.connect("Fake")

    assert service.is_connected
    assert service.connection_state is ConnectionState.CONNECTED
    assert service.connected_emulator_name == "Fake"
    assert process.pid > 0
    assert service.read_bytes(2, 2) == bytes([2, 3])


def test_detect_lists_only_running_emulators() -> None:
    running = FakeMemoryProvider(emulator_name="Running", detectable=True)
    stopped = FakeMemoryProvider(emulator_name="Stopped", detectable=False)
    service = make_service(running, stopped)

    detected = service.detect_emulators()

    assert [item.emulator_name for item in detected] == ["Running"]


def test_connect_replaces_previous_connection() -> None:
    first = FakeMemoryProvider(emulator_name="First", memory=b"aaaa")
    second = FakeMemoryProvider(emulator_name="Second", memory=b"bbbb")
    service = make_service(first, second)

    service.connect("First")
    service.connect("Second")

    assert service.connected_emulator_name == "Second"
    assert not first.is_connected
    assert second.is_connected


def test_connect_to_stopped_emulator_raises() -> None:
    service = make_service(FakeMemoryProvider(emulator_name="Fake", detectable=False))

    with pytest.raises(EmulatorNotFoundError):
        service.connect("Fake")

    assert service.connection_state is ConnectionState.DISCONNECTED


def test_read_without_connection_raises() -> None:
    service = make_service(FakeMemoryProvider(emulator_name="Fake"))

    with pytest.raises(NotConnectedError):
        service.read_bytes(0, 1)


def test_disconnect_returns_to_disconnected() -> None:
    provider = FakeMemoryProvider(emulator_name="Fake", memory=b"data")
    service = make_service(provider)
    service.connect("Fake")

    service.disconnect()

    assert service.connection_state is ConnectionState.DISCONNECTED
    assert not provider.is_connected


def test_refresh_marks_lost_when_emulator_disappears() -> None:
    provider = FakeMemoryProvider(emulator_name="Fake", memory=b"data")
    service = make_service(provider)
    service.connect("Fake")

    # Simulate the emulator process going away underneath us.
    provider.disconnect()

    assert service.refresh_connection() is ConnectionState.LOST
    assert service.connection_state is ConnectionState.LOST
    assert service.connected_emulator_name is None
    with pytest.raises(NotConnectedError):
        service.read_bytes(0, 1)


def test_refresh_keeps_state_when_connection_healthy() -> None:
    service = make_service(FakeMemoryProvider(emulator_name="Fake", memory=b"data"))
    service.connect("Fake")

    assert service.refresh_connection() is ConnectionState.CONNECTED

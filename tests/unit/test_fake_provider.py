"""Tests for the fake memory provider."""

import pytest

from ramr.domain.exceptions import (
    EmulatorNotFoundError,
    MemoryReadError,
    NotConnectedError,
)
from ramr.infrastructure.memory.fake_provider import FakeMemoryProvider


def test_connect_then_read_returns_seeded_bytes() -> None:
    provider = FakeMemoryProvider(memory=bytes(range(8)))

    provider.connect()

    assert provider.is_connected
    assert provider.read_bytes(2, 3) == bytes([2, 3, 4])


def test_write_bytes_grows_buffer() -> None:
    provider = FakeMemoryProvider()
    provider.connect()

    provider.write_bytes(4, b"\xde\xad")

    assert provider.read_bytes(4, 2) == b"\xde\xad"


def test_read_without_connect_raises() -> None:
    with pytest.raises(NotConnectedError):
        FakeMemoryProvider(memory=b"data").read_bytes(0, 1)


def test_connect_when_not_detectable_raises() -> None:
    provider = FakeMemoryProvider(detectable=False)

    assert provider.detect() is None
    with pytest.raises(EmulatorNotFoundError):
        provider.connect()


def test_read_out_of_bounds_raises() -> None:
    provider = FakeMemoryProvider(memory=b"1234")
    provider.connect()

    with pytest.raises(MemoryReadError, match="out of bounds"):
        provider.read_bytes(0, 100)


def test_disconnect_stops_reads() -> None:
    provider = FakeMemoryProvider(memory=b"1234")
    provider.connect()

    provider.disconnect()

    assert not provider.is_connected
    with pytest.raises(NotConnectedError):
        provider.read_bytes(0, 1)

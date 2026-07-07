"""Tests for the memory domain value objects and provider port."""

import inspect

import pytest

from ramr.domain.memory import ConnectionState, EmulatorProcess
from ramr.domain.memory_provider import MemoryProvider


def test_emulator_process_is_immutable() -> None:
    process = EmulatorProcess(pid=1234, name="pcsx2-qt.exe")

    with pytest.raises(AttributeError):
        process.pid = 5678  # type: ignore[misc]


def test_emulator_process_executable_path_defaults_to_none() -> None:
    assert EmulatorProcess(pid=1, name="x").executable_path is None


def test_connection_states_are_distinct() -> None:
    assert len({state.value for state in ConnectionState}) == len(ConnectionState)


def test_memory_provider_cannot_be_instantiated_directly() -> None:
    with pytest.raises(TypeError):
        MemoryProvider()  # type: ignore[abstract]


def test_memory_provider_declares_expected_interface() -> None:
    members = dict(inspect.getmembers(MemoryProvider))
    for name in (
        "emulator_name",
        "process_names",
        "detect",
        "connect",
        "disconnect",
        "is_connected",
        "read_bytes",
    ):
        assert name in members

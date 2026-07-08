"""Tests for the memory provider registry."""

import pytest

from ramr.domain.exceptions import MemoryProviderError
from ramr.infrastructure.memory.fake_provider import FakeMemoryProvider
from ramr.infrastructure.memory.registry import (
    MemoryProviderRegistry,
    build_default_registry,
)


def test_names_are_sorted() -> None:
    registry = MemoryProviderRegistry(
        [
            FakeMemoryProvider(emulator_name="DuckStation"),
            FakeMemoryProvider(emulator_name="BizHawk"),
        ]
    )

    assert registry.names() == ["BizHawk", "DuckStation"]


def test_get_returns_registered_provider() -> None:
    provider = FakeMemoryProvider(emulator_name="BizHawk")
    registry = MemoryProviderRegistry([provider])

    assert registry.get("BizHawk") is provider


def test_get_unknown_name_raises() -> None:
    with pytest.raises(MemoryProviderError, match="No memory provider"):
        MemoryProviderRegistry().get("Unknown")


def test_register_replaces_same_named_provider() -> None:
    first = FakeMemoryProvider(emulator_name="BizHawk")
    second = FakeMemoryProvider(emulator_name="BizHawk")
    registry = MemoryProviderRegistry([first])

    registry.register(second)

    assert registry.get("BizHawk") is second
    assert registry.names() == ["BizHawk"]


def test_default_registry_includes_pcsx2() -> None:
    assert "PCSX2" in build_default_registry().names()

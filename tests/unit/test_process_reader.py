"""Tests for the Windows process memory reader.

The reader is exercised against this test process: a ctypes buffer with a
known payload is read back through OpenProcess/ReadProcessMemory. This
verifies the real Win32 path without needing a separate process.
"""

import ctypes
import os
import sys

import pytest

from ramr.domain.exceptions import MemoryReadError
from ramr.infrastructure.memory.process_reader import ProcessMemoryReader

pytestmark = pytest.mark.skipif(
    sys.platform != "win32", reason="ProcessMemoryReader is Windows-only"
)


def test_reads_known_payload_from_own_process() -> None:
    payload = b"RAMR-process-memory-marker"
    buffer = ctypes.create_string_buffer(payload)
    address = ctypes.addressof(buffer)

    reader = ProcessMemoryReader()
    reader.open(os.getpid())
    try:
        assert reader.read(address, len(payload)) == payload
    finally:
        reader.close()


def test_is_open_reflects_lifecycle() -> None:
    reader = ProcessMemoryReader()
    assert not reader.is_open

    reader.open(os.getpid())
    assert reader.is_open

    reader.close()
    assert not reader.is_open


def test_read_before_open_raises() -> None:
    with pytest.raises(MemoryReadError, match="not open"):
        ProcessMemoryReader().read(0x1000, 4)


def test_non_positive_size_raises() -> None:
    reader = ProcessMemoryReader()
    reader.open(os.getpid())
    try:
        with pytest.raises(MemoryReadError, match="positive"):
            reader.read(ctypes.addressof(ctypes.create_string_buffer(4)), 0)
    finally:
        reader.close()


def test_reading_unmapped_address_raises() -> None:
    reader = ProcessMemoryReader()
    reader.open(os.getpid())
    try:
        with pytest.raises(MemoryReadError):
            reader.read(0x1, 8)
    finally:
        reader.close()


def test_close_is_idempotent() -> None:
    reader = ProcessMemoryReader()
    reader.open(os.getpid())

    reader.close()
    reader.close()

    assert not reader.is_open

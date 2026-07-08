"""Tests for the in-memory buffer reader."""

import pytest

from ramr.domain.exceptions import MemoryReadError
from ramr.infrastructure.memory.buffer_reader import BufferMemoryReader


def test_read_returns_requested_slice() -> None:
    reader = BufferMemoryReader(bytes(range(16)))
    reader.open(pid=1)

    assert reader.read(4, 3) == bytes([4, 5, 6])


def test_read_before_open_raises() -> None:
    with pytest.raises(MemoryReadError, match="not open"):
        BufferMemoryReader(b"data").read(0, 1)


def test_read_out_of_bounds_raises() -> None:
    reader = BufferMemoryReader(b"1234")
    reader.open(pid=1)

    with pytest.raises(MemoryReadError, match="out of bounds"):
        reader.read(2, 10)


def test_non_positive_size_raises() -> None:
    reader = BufferMemoryReader(b"1234")
    reader.open(pid=1)

    with pytest.raises(MemoryReadError, match="positive"):
        reader.read(0, 0)


def test_close_marks_reader_closed() -> None:
    reader = BufferMemoryReader(b"1234")
    reader.open(pid=1)

    reader.close()

    assert not reader.is_open

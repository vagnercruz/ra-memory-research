"""In-memory :class:`MemoryReader` backed by a byte buffer.

Useful for offline development and deterministic tests: it satisfies the
same reader port as :class:`ProcessMemoryReader` but serves bytes from a
buffer, treating addresses as offsets into it.
"""

from ramr.domain.exceptions import MemoryReadError


class BufferMemoryReader:
    """Serves reads from an in-memory buffer, addressing it from offset zero."""

    def __init__(self, buffer: bytes | bytearray) -> None:
        self._buffer = bytearray(buffer)
        self._open = False

    @property
    def is_open(self) -> bool:
        return self._open

    def open(self, pid: int) -> None:
        self._open = True

    def close(self) -> None:
        self._open = False

    def read(self, address: int, size: int) -> bytes:
        if not self._open:
            raise MemoryReadError("Reader is not open.")
        if size <= 0:
            raise MemoryReadError(f"Read size must be positive, got {size}.")
        if address < 0 or address + size > len(self._buffer):
            raise MemoryReadError(
                f"Read of {size} bytes at {address:#x} is out of bounds "
                f"(buffer size {len(self._buffer)})."
            )
        return bytes(self._buffer[address : address + size])

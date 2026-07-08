"""Windows implementation of :class:`MemoryReader` using the Win32 API."""

import ctypes
import logging
import sys
from ctypes import wintypes

from ramr.domain.exceptions import MemoryProviderError, MemoryReadError

logger = logging.getLogger(__name__)

# Minimal access rights needed to read another process's memory.
_PROCESS_VM_READ = 0x0010
_PROCESS_QUERY_INFORMATION = 0x0400


class ProcessMemoryReader:
    """Reads process memory through ``OpenProcess`` and ``ReadProcessMemory``.

    Windows-only, matching the application's target platform. The kernel32
    bindings are loaded lazily so the module stays importable (for tooling
    and tests) on other platforms.
    """

    def __init__(self) -> None:
        self._handle: int | None = None
        self._kernel32: ctypes.WinDLL | None = None

    @property
    def is_open(self) -> bool:
        return self._handle is not None

    def open(self, pid: int) -> None:
        """Open a read handle to the process ``pid``.

        Raises:
            MemoryProviderError: if not running on Windows.
            MemoryReadError: if the process cannot be opened.
        """
        if self._handle is not None:
            self.close()

        kernel32 = self._load_kernel32()
        handle = kernel32.OpenProcess(_PROCESS_VM_READ | _PROCESS_QUERY_INFORMATION, False, pid)
        if not handle:
            raise MemoryReadError(
                f"Could not open process {pid} (error {ctypes.get_last_error()})."
            )

        self._handle = handle
        self._kernel32 = kernel32
        logger.debug("Opened read handle to process %d", pid)

    def read(self, address: int, size: int) -> bytes:
        """Read ``size`` bytes from ``address`` in the opened process.

        Raises:
            MemoryReadError: if not open, ``size`` is not positive, or the
                read fails or returns fewer bytes than requested.
        """
        if self._handle is None or self._kernel32 is None:
            raise MemoryReadError("Reader is not open.")
        if size <= 0:
            raise MemoryReadError(f"Read size must be positive, got {size}.")

        buffer = (ctypes.c_char * size)()
        bytes_read = ctypes.c_size_t(0)
        succeeded = self._kernel32.ReadProcessMemory(
            self._handle,
            ctypes.c_void_p(address),
            buffer,
            size,
            ctypes.byref(bytes_read),
        )
        if not succeeded or bytes_read.value != size:
            raise MemoryReadError(
                f"Failed to read {size} bytes at {address:#x} "
                f"(read {bytes_read.value}, error {ctypes.get_last_error()})."
            )
        return bytes(buffer.raw[: bytes_read.value])

    def close(self) -> None:
        """Close the process handle; safe to call when already closed."""
        if self._handle is not None and self._kernel32 is not None:
            self._kernel32.CloseHandle(self._handle)
            logger.debug("Closed process read handle")
        self._handle = None
        self._kernel32 = None

    @staticmethod
    def _load_kernel32() -> ctypes.WinDLL:
        if sys.platform != "win32":
            raise MemoryProviderError(
                "Reading emulator process memory is only supported on Windows."
            )

        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel32.OpenProcess.restype = wintypes.HANDLE
        kernel32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        kernel32.ReadProcessMemory.restype = wintypes.BOOL
        kernel32.ReadProcessMemory.argtypes = [
            wintypes.HANDLE,
            wintypes.LPCVOID,
            wintypes.LPVOID,
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_size_t),
        ]
        kernel32.CloseHandle.restype = wintypes.BOOL
        kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
        return kernel32

"""PCSX2 (PlayStation 2) memory provider."""

from ramr.domain.exceptions import MemoryProviderError
from ramr.domain.memory import EmulatorProcess
from ramr.infrastructure.memory.ports import MemoryReader, ProcessLocator
from ramr.infrastructure.memory.process_provider import ProcessMemoryProvider

# Executable names across PCSX2 builds (Qt and legacy wx, plain and AVX2).
PCSX2_PROCESS_NAMES = (
    "pcsx2-qt.exe",
    "pcsx2x64-avx2.exe",
    "pcsx2x64.exe",
    "pcsx2.exe",
)


class Pcsx2Provider(ProcessMemoryProvider):
    """Reads PS2 main memory from a running PCSX2 process.

    PCSX2 allocates the 32 MiB EE main RAM on the host heap, so its base
    address is not a fixed constant and varies per launch and build. A
    robust resolver (signature scan or the emulator's memory-exposure API)
    is planned; until then the base can be supplied through
    ``guest_base_override`` for calibrated setups, keeping this provider
    honest rather than reading from a guessed address.
    """

    emulator_name = "PCSX2"
    process_names = PCSX2_PROCESS_NAMES

    def __init__(
        self,
        guest_base_override: int | None = None,
        reader: MemoryReader | None = None,
        locator: ProcessLocator | None = None,
    ) -> None:
        super().__init__(reader=reader, locator=locator)
        self._guest_base_override = guest_base_override

    def _resolve_host_base(self, reader: MemoryReader, process: EmulatorProcess) -> int:
        if self._guest_base_override is not None:
            return self._guest_base_override
        raise MemoryProviderError(
            "PCSX2 guest RAM base is not calibrated. Provide guest_base_override; "
            "automatic base resolution will be added in a future sprint."
        )

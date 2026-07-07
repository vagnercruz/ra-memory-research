"""psutil-backed process locator."""

import logging
from collections.abc import Callable, Iterable, Sequence

from ramr.domain.memory import EmulatorProcess

logger = logging.getLogger(__name__)

# One process as a plain mapping (psutil's ``Process.info``); kept abstract so
# the locator can be driven by a fake iterator in tests.
ProcessInfo = dict[str, object]
ProcessIterator = Callable[[], Iterable[ProcessInfo]]


class EmulatorProcessLocator:
    """Finds a running emulator process by executable name.

    The process iterator is injected so tests can supply a fixed process
    list; the default iterator reads live processes with psutil.
    """

    def __init__(self, process_iterator: ProcessIterator | None = None) -> None:
        self._process_iterator = process_iterator or self._iter_live_processes

    def find(self, process_names: Sequence[str]) -> EmulatorProcess | None:
        wanted = {name.lower() for name in process_names}
        for info in self._process_iterator():
            name = str(info.get("name") or "")
            if name.lower() in wanted:
                pid = int(info.get("pid") or 0)
                executable = info.get("exe")
                logger.info("Located emulator process '%s' (pid %d)", name, pid)
                return EmulatorProcess(
                    pid=pid,
                    name=name,
                    executable_path=str(executable) if executable else None,
                )
        return None

    @staticmethod
    def _iter_live_processes() -> Iterable[ProcessInfo]:
        import psutil

        for process in psutil.process_iter(["pid", "name", "exe"]):
            yield process.info

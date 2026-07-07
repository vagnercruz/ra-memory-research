"""Persistent list of recently opened project directories."""

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

DEFAULT_RECENT_PROJECTS_LIMIT = 10


class RecentProjectsStore:
    """Keeps the most recently opened project paths in a JSON file.

    The file path is injected so the store stays free of Qt and easy to
    test; the application passes a file inside its per-user data directory.
    """

    def __init__(self, file_path: Path, limit: int = DEFAULT_RECENT_PROJECTS_LIMIT) -> None:
        self._file_path = file_path
        self._limit = limit

    def add(self, project_directory: Path) -> None:
        """Record ``project_directory`` as the most recently opened project."""
        entries = self.list()
        resolved = project_directory.resolve()
        entries = [entry for entry in entries if entry != resolved]
        entries.insert(0, resolved)
        self._write(entries[: self._limit])

    def remove(self, project_directory: Path) -> None:
        """Forget ``project_directory`` (e.g. after it failed to open)."""
        resolved = project_directory.resolve()
        self._write([entry for entry in self.list() if entry != resolved])

    def list(self) -> list[Path]:
        """Return recorded paths, most recently opened first."""
        if not self._file_path.exists():
            return []

        try:
            data = json.loads(self._file_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            logger.warning("Ignoring unreadable recent projects file: %s", error)
            return []

        if not isinstance(data, list):
            logger.warning("Ignoring malformed recent projects file: not a list")
            return []

        return [Path(entry) for entry in data if isinstance(entry, str)]

    def _write(self, entries: list[Path]) -> None:
        self._file_path.parent.mkdir(parents=True, exist_ok=True)
        content = json.dumps([str(entry) for entry in entries], indent=2)
        self._file_path.write_text(content, encoding="utf-8")

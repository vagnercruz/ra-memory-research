"""Project model: one game under research."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ramr.domain.exceptions import InvalidProjectFileError

PROJECT_SCHEMA_VERSION = 1

_REQUIRED_FIELDS = ("schema_version", "name", "system", "created_at", "modified_at")


def _utc_now() -> datetime:
    return datetime.now(UTC)


@dataclass(slots=True)
class Project:
    """A portable, per-game research project.

    ``root_directory`` is derived from where the project was opened and is
    intentionally excluded from serialization so project directories can be
    moved or shared without breaking.
    """

    name: str
    system: str
    root_directory: Path
    notes: str = ""
    created_at: datetime = field(default_factory=_utc_now)
    modified_at: datetime = field(default_factory=_utc_now)
    schema_version: int = PROJECT_SCHEMA_VERSION

    def touch(self) -> None:
        """Record that the project was modified now."""
        self.modified_at = _utc_now()

    def to_dict(self) -> dict[str, Any]:
        """Serializable representation for ``project.json``."""
        return {
            "schema_version": self.schema_version,
            "name": self.name,
            "system": self.system,
            "notes": self.notes,
            "created_at": self.created_at.isoformat(),
            "modified_at": self.modified_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any], root_directory: Path) -> "Project":
        """Build a project from parsed ``project.json`` content.

        Raises:
            InvalidProjectFileError: if required fields are missing or malformed.
        """
        missing = [name for name in _REQUIRED_FIELDS if name not in data]
        if missing:
            raise InvalidProjectFileError(f"Project file misses required fields: {missing}")

        try:
            return cls(
                name=str(data["name"]),
                system=str(data["system"]),
                root_directory=root_directory,
                notes=str(data.get("notes", "")),
                created_at=datetime.fromisoformat(data["created_at"]),
                modified_at=datetime.fromisoformat(data["modified_at"]),
                schema_version=int(data["schema_version"]),
            )
        except (TypeError, ValueError) as error:
            raise InvalidProjectFileError(f"Project file has malformed values: {error}") from error

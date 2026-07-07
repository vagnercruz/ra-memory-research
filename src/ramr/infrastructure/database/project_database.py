"""Per-project SQLite database for large research datasets."""

import logging
import sqlite3
from collections.abc import Callable
from pathlib import Path

logger = logging.getLogger(__name__)

DATABASE_FILE_NAME = "research.db"

Migration = Callable[[sqlite3.Connection], None]


def _migration_1_metadata_table(connection: sqlite3.Connection) -> None:
    connection.execute("""
        CREATE TABLE metadata (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
        """)


# Ordered schema migrations; index 0 upgrades the schema to version 1.
# Never modify an entry after release — append a new migration instead.
_MIGRATIONS: tuple[Migration, ...] = (_migration_1_metadata_table,)


class ProjectDatabase:
    """Owns the SQLite connection for one project.

    Large datasets (snapshots, value histories) belong here; ``project.json``
    stays reserved for small, human-readable metadata. Schema versioning uses
    SQLite's ``user_version`` pragma with append-only migrations.
    """

    def __init__(self, database_path: Path) -> None:
        self._database_path = database_path
        self._connection: sqlite3.Connection | None = None

    @classmethod
    def for_project_directory(cls, root_directory: Path) -> "ProjectDatabase":
        """Database located at the standard path inside a project directory."""
        return cls(root_directory / DATABASE_FILE_NAME)

    @property
    def connection(self) -> sqlite3.Connection:
        """The open connection.

        Raises:
            RuntimeError: if the database has not been opened.
        """
        if self._connection is None:
            raise RuntimeError("Database is not open; call open() first.")
        return self._connection

    @property
    def is_open(self) -> bool:
        return self._connection is not None

    def open(self) -> None:
        """Open the database file and apply any pending migrations."""
        if self._connection is not None:
            return

        self._connection = sqlite3.connect(self._database_path)
        self._connection.execute("PRAGMA foreign_keys = ON")
        self._apply_migrations()
        logger.info("Opened project database: %s", self._database_path)

    def close(self) -> None:
        """Close the connection; safe to call when already closed."""
        if self._connection is not None:
            self._connection.close()
            self._connection = None
            logger.info("Closed project database: %s", self._database_path)

    def schema_version(self) -> int:
        """Current schema version recorded in the database."""
        row = self.connection.execute("PRAGMA user_version").fetchone()
        return int(row[0])

    def set_metadata(self, key: str, value: str) -> None:
        """Store a key-value pair in the project metadata table."""
        with self.connection:
            self.connection.execute(
                "INSERT INTO metadata (key, value) VALUES (?, ?) "
                "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
                (key, value),
            )

    def get_metadata(self, key: str) -> str | None:
        """Read a value from the project metadata table."""
        row = self.connection.execute("SELECT value FROM metadata WHERE key = ?", (key,)).fetchone()
        return None if row is None else str(row[0])

    def _apply_migrations(self) -> None:
        current_version = self.schema_version()
        for version, migration in enumerate(_MIGRATIONS, start=1):
            if version <= current_version:
                continue
            with self.connection:
                migration(self.connection)
                self.connection.execute(f"PRAGMA user_version = {version}")
            logger.info("Migrated project database to schema version %d", version)

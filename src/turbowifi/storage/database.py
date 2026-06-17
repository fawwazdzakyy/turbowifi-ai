"""
SQLite database connection and lifecycle.
"""

import sqlite3
from pathlib import Path
from contextlib import contextmanager
from typing import Generator

from turbowifi.storage.schema import MIGRATIONS


class Storage:
    def __init__(self, db_path: Path | str):
        self.db_path = Path(db_path)
        self._init_db()

    @contextmanager
    def get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Get a configured database connection."""
        conn = sqlite3.connect(
            str(self.db_path),
            timeout=5.0,  # Wait up to 5s for lock
            isolation_level=None,  # Autocommit mode, we handle transactions manually if needed
        )
        conn.row_factory = sqlite3.Row

        # Configure WAL mode and other pragmas for performance
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA temp_store=MEMORY")
        conn.execute("PRAGMA foreign_keys=ON")

        try:
            yield conn
        finally:
            conn.close()

    def _init_db(self) -> None:
        """Initialize schema and apply migrations."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        with self.get_connection() as conn:
            # Check current version
            conn.execute("CREATE TABLE IF NOT EXISTS schema_version (version INTEGER)")
            cur = conn.execute("SELECT version FROM schema_version")
            row = cur.fetchone()

            if not row:
                current_version = 0
                conn.execute("INSERT INTO schema_version (version) VALUES (0)")
            else:
                current_version = row["version"]

            # Apply migrations
            for i in range(current_version, len(MIGRATIONS)):
                try:
                    conn.executescript(MIGRATIONS[i])
                    conn.execute("UPDATE schema_version SET version = ?", (i + 1,))
                except Exception as e:
                    raise RuntimeError(f"Database migration to version {i + 1} failed: {e}")

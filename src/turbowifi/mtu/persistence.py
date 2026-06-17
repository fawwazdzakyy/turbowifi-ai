"""
Persistence for MTU scans and history.
"""

from turbowifi.storage.database import Storage
from turbowifi.config.settings import get_db_path


class MTUPersistence:
    def __init__(self):
        self.storage = Storage(get_db_path())
        self._ensure_table()

    def _ensure_table(self):
        with self.storage.get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS mtu_scans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    interface TEXT NOT NULL,
                    optimal_mtu INTEGER NOT NULL,
                    confidence REAL NOT NULL
                )
            """)

    def record_scan(self, interface: str, optimal_mtu: int, confidence: float):
        import time

        with self.storage.get_connection() as conn:
            conn.execute(
                "INSERT INTO mtu_scans (timestamp, interface, optimal_mtu, confidence) VALUES (?, ?, ?, ?)",
                (time.time(), interface, optimal_mtu, confidence),
            )

    def get_last_scan_time(self) -> float | None:
        with self.storage.get_connection() as conn:
            cursor = conn.execute("SELECT timestamp FROM mtu_scans ORDER BY timestamp DESC LIMIT 1")
            row = cursor.fetchone()
            if row:
                return row["timestamp"]
        return None

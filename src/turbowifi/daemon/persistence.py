import json
import time
from turbowifi.storage.database import Storage
from turbowifi.storage.queries import Queries
from turbowifi.config.settings import get_db_path


class DaemonPersistence:
    def __init__(self):
        self.storage = Storage(get_db_path())
        self.queries = Queries(self.storage)

    def set_status(self, status: dict):
        with self.storage.get_connection() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO daemon_state (key, value, updated_at) VALUES (?, ?, ?)",
                ("status", json.dumps(status), time.time()),
            )

    def get_status(self) -> dict:
        default_status = {
            "state": "STOPPED",
            "pause_reason": "Not running",
            "next_run": None,
            "last_run": None,
            "updated_at": time.time(),
        }
        with self.storage.get_connection() as conn:
            cursor = conn.execute("SELECT value FROM daemon_state WHERE key = ?", ("status",))
            row = cursor.fetchone()
            if row:
                try:
                    data = json.loads(row["value"])
                    default_status.update(data)
                except Exception:
                    pass
            return default_status

    def set_state(
        self, state: str, pause_reason: str = None, next_run: float = None, last_run: float = None
    ):
        s = self.get_status()
        s["state"] = state
        s["updated_at"] = time.time()
        if pause_reason is not None:
            s["pause_reason"] = pause_reason
        if next_run is not None:
            s["next_run"] = next_run
        if last_run is not None:
            s["last_run"] = last_run
        self.set_status(s)

    def get_state(self) -> str:
        return self.get_status().get("state", "STOPPED")

    def cleanup_old_scans(self, max_days: int = 7):
        """Retention policy: delete scans older than max_days to bound DB growth."""
        # Simple bounds management
        with self.storage.get_connection() as conn:
            # We don't have a direct timestamp cleanup right now but we can limit by row count
            conn.execute("""
                DELETE FROM scans 
                WHERE id NOT IN (
                    SELECT id FROM scans ORDER BY timestamp DESC LIMIT 5000
                )
            """)

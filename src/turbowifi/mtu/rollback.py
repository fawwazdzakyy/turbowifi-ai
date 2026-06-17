"""
Safe Rollback Engine for MTU.
"""

import json
import logging
from turbowifi.mtu.platform import MTUPlatform
from turbowifi.storage.database import Storage
from turbowifi.config.settings import get_db_path

logger = logging.getLogger("mtu.rollback")


class MTURollbackEngine:
    def __init__(self):
        self.storage = Storage(get_db_path())
        self.platform = MTUPlatform()

    def create_backup(self, interface: str) -> bool:
        """Stores the current MTU state into backups table."""
        current_mtu = self.platform.get_current_mtu(interface)
        if not current_mtu:
            return False

        state_json = json.dumps({"interface": interface, "mtu": current_mtu})

        with self.storage.get_connection() as conn:
            import time

            conn.execute(
                "INSERT INTO backups (module, state_json, created_at, is_active) VALUES (?, ?, ?, ?)",
                ("mtu", state_json, time.time(), 1),
            )
        return True

    def rollback_latest(self) -> bool:
        """Reverts to the most recent active MTU backup."""
        with self.storage.get_connection() as conn:
            cursor = conn.execute(
                "SELECT id, state_json FROM backups WHERE module = 'mtu' AND is_active = 1 ORDER BY created_at DESC LIMIT 1"
            )
            row = cursor.fetchone()

            if not row:
                logger.warning("No active MTU backups found.")
                return False

            backup_id = row["id"]
            state = json.loads(row["state_json"])

        interface = state.get("interface")
        original_mtu = state.get("mtu")

        if interface and original_mtu:
            success = self.platform.set_mtu(interface, original_mtu)
            if success:
                # Mark as inactive
                with self.storage.get_connection() as conn:
                    conn.execute("UPDATE backups SET is_active = 0 WHERE id = ?", (backup_id,))
                logger.info(f"Successfully rolled back {interface} to MTU {original_mtu}")
                return True

        return False

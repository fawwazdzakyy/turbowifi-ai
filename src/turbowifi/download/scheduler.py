"""
Dynamic concurrency scheduler.
"""

from turbowifi.storage.database import Storage
from turbowifi.storage.queries import Queries
from turbowifi.config.settings import get_db_path


class DownloadScheduler:
    """Adjusts concurrent connections based on recent daemon metrics."""

    def __init__(self, override_connections: int | None = None):
        self.override = override_connections
        self.storage = Storage(get_db_path())
        self.queries = Queries(self.storage)

    def determine_concurrency(self) -> int:
        if self.override is not None and self.override > 0:
            return min(self.override, 32)  # Cap at 32

        recent = self.queries.get_recent_scans(limit=1)
        if not recent:
            return 4  # Safe default

        latest = recent[0]

        # High loss? Reduce concurrency to avoid exacerbating congestion
        if latest.packet_loss_pct > 2.0:
            return 2
        elif latest.packet_loss_pct > 0.5:
            return 4

        # High jitter? Keep it moderate
        if latest.jitter_ms > 30.0:
            return 4

        # Good network! Push it up
        return 8

"""
Typed queries for the database.
"""

from typing import List, Optional

from turbowifi.storage.database import Storage
from turbowifi.storage.models import OperationStateRecord, ScanRecord, BaselineRecord


class Queries:
    def __init__(self, storage: Storage):
        self.storage = storage

    # --- Operation State ---

    def get_operation_state(self, operation_id: str) -> Optional[OperationStateRecord]:
        with self.storage.get_connection() as conn:
            cur = conn.execute(
                "SELECT * FROM operation_state WHERE operation_id = ?", (operation_id,)
            )
            row = cur.fetchone()
            if not row:
                return None
            return OperationStateRecord(**dict(row))

    def get_pending_operations(self) -> List[OperationStateRecord]:
        with self.storage.get_connection() as conn:
            cur = conn.execute(
                "SELECT * FROM operation_state WHERE current_state NOT IN ('IDLE', 'COMPLETE')"
            )
            return [OperationStateRecord(**dict(row)) for row in cur.fetchall()]

    def upsert_operation_state(self, state: OperationStateRecord) -> None:
        with self.storage.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO operation_state (
                    operation_id, operation_type, current_state, started_at, 
                    updated_at, backup_ids_json, plan_json, error_message, metadata_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(operation_id) DO UPDATE SET
                    current_state = excluded.current_state,
                    updated_at = excluded.updated_at,
                    backup_ids_json = excluded.backup_ids_json,
                    plan_json = excluded.plan_json,
                    error_message = excluded.error_message,
                    metadata_json = excluded.metadata_json
            """,
                (
                    state.operation_id,
                    state.operation_type,
                    state.current_state,
                    state.started_at,
                    state.updated_at,
                    state.backup_ids_json,
                    state.plan_json,
                    state.error_message,
                    state.metadata_json,
                ),
            )

    # --- Scans ---

    def insert_scan(self, scan: ScanRecord) -> int:
        with self.storage.get_connection() as conn:
            cur = conn.execute(
                """
                INSERT INTO scans (
                    timestamp, latency_ms, jitter_ms, packet_loss_pct, 
                    dns_latency_ms, stability_score
                ) VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    scan.timestamp,
                    scan.latency_ms,
                    scan.jitter_ms,
                    scan.packet_loss_pct,
                    scan.dns_latency_ms,
                    scan.stability_score,
                ),
            )
            return cur.lastrowid

    def get_recent_scans(self, limit: int = 50) -> List[ScanRecord]:
        with self.storage.get_connection() as conn:
            cur = conn.execute("SELECT * FROM scans ORDER BY timestamp DESC LIMIT ?", (limit,))
            # Reverse to get chronological order if needed, but usually we just process them
            return [ScanRecord(**dict(row)) for row in cur.fetchall()]

    # --- Baselines ---

    def insert_baseline(self, baseline: BaselineRecord) -> int:
        with self.storage.get_connection() as conn:
            cur = conn.execute(
                """
                INSERT INTO baselines (
                    computed_at, sample_count, confidence, latency_ms,
                    jitter_ms, packet_loss_pct, dns_latency_ms, stability_score,
                    latency_p90, jitter_p90, dns_latency_p90
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    baseline.computed_at,
                    baseline.sample_count,
                    baseline.confidence,
                    baseline.latency_ms,
                    baseline.jitter_ms,
                    baseline.packet_loss_pct,
                    baseline.dns_latency_ms,
                    baseline.stability_score,
                    baseline.latency_p90,
                    baseline.jitter_p90,
                    baseline.dns_latency_p90,
                ),
            )
            return cur.lastrowid

    def get_latest_baseline(self) -> Optional[BaselineRecord]:
        with self.storage.get_connection() as conn:
            cur = conn.execute("SELECT * FROM baselines ORDER BY computed_at DESC LIMIT 1")
            row = cur.fetchone()
            if not row:
                return None
            return BaselineRecord(**dict(row))

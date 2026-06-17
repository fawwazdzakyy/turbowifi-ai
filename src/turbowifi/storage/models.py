"""
Storage models (dataclasses matching DB rows).
"""

from dataclasses import dataclass


@dataclass
class OperationStateRecord:
    operation_id: str
    operation_type: str
    current_state: str
    started_at: float
    updated_at: float
    backup_ids_json: str | None
    plan_json: str | None
    error_message: str | None
    metadata_json: str | None


@dataclass
class ScanRecord:
    id: int
    timestamp: float
    latency_ms: float
    jitter_ms: float
    packet_loss_pct: float
    dns_latency_ms: float | None
    stability_score: float


@dataclass
class BaselineRecord:
    id: int
    computed_at: float
    sample_count: int
    confidence: float
    latency_ms: float
    jitter_ms: float
    packet_loss_pct: float
    dns_latency_ms: float
    stability_score: float
    latency_p90: float
    jitter_p90: float
    dns_latency_p90: float


@dataclass
class BackupRecord:
    id: int
    module: str
    state_json: str
    created_at: float
    is_active: bool

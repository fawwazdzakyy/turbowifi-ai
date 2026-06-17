"""
Database schema definition.
"""

SCHEMA_V1 = """
CREATE TABLE IF NOT EXISTS scans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp REAL NOT NULL,
    latency_ms REAL NOT NULL,
    jitter_ms REAL NOT NULL,
    packet_loss_pct REAL NOT NULL,
    dns_latency_ms REAL,
    stability_score REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_scans_time ON scans(timestamp);

CREATE TABLE IF NOT EXISTS baselines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    computed_at REAL NOT NULL,
    sample_count INTEGER NOT NULL,
    confidence REAL NOT NULL,
    latency_ms REAL NOT NULL,
    jitter_ms REAL NOT NULL,
    packet_loss_pct REAL NOT NULL,
    dns_latency_ms REAL NOT NULL,
    stability_score REAL NOT NULL,
    latency_p90 REAL NOT NULL,
    jitter_p90 REAL NOT NULL,
    dns_latency_p90 REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_baselines_time ON baselines(computed_at);

CREATE TABLE IF NOT EXISTS operation_state (
    operation_id TEXT PRIMARY KEY,
    operation_type TEXT NOT NULL,
    current_state TEXT NOT NULL,
    started_at REAL NOT NULL,
    updated_at REAL NOT NULL,
    backup_ids_json TEXT,
    plan_json TEXT,
    error_message TEXT,
    metadata_json TEXT
);

CREATE TABLE IF NOT EXISTS daemon_state (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS backups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    module TEXT NOT NULL,
    state_json TEXT NOT NULL,
    created_at REAL NOT NULL,
    is_active INTEGER NOT NULL DEFAULT 1
);
"""

MIGRATIONS = [
    SCHEMA_V1,
    # Future migrations will be added here
]

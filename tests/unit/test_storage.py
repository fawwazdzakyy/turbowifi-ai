"""
Unit tests for storage layer.
"""

from turbowifi.storage.models import ScanRecord


def test_db_initialization(temp_db):
    """Test schema and migrations apply correctly."""
    with temp_db.get_connection() as conn:
        cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row["name"] for row in cur.fetchall()]
        assert "scans" in tables
        assert "operation_state" in tables


def test_insert_scan(queries):
    """Test inserting a scan record."""
    scan = ScanRecord(
        id=0,
        timestamp=1000.0,
        latency_ms=25.0,
        jitter_ms=5.0,
        packet_loss_pct=0.0,
        dns_latency_ms=10.0,
        stability_score=0.9,
    )
    scan_id = queries.insert_scan(scan)
    assert scan_id > 0

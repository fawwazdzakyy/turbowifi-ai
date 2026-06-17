"""
Unit tests for the TUI Dashboard.
"""

from turbowifi.tui.state import DashboardState
from turbowifi.tui.renderer import render_metric


def test_dashboard_state_defaults():
    state = DashboardState()
    assert state.network_metrics == {}
    assert state.optimization_score == 0.0
    assert state.daemon_status == "STOPPED"


def test_render_metric():
    text_none = render_metric("Lat", None)
    assert "N/A" in str(text_none)

    text_val = render_metric("Lat", 20.0, "ms")
    assert "20.0ms" in str(text_val)

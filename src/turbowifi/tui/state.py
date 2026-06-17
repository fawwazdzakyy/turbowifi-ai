"""
TUI state management.
"""

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class DashboardState:
    network_metrics: Dict[str, float] = field(default_factory=dict)
    optimization_score: float = 0.0
    network_grade: str = "N/A"
    prediction: str = "UNKNOWN"
    capability_mode: str = "UNKNOWN"
    daemon_status: str = "STOPPED"
    last_actions: List[str] = field(default_factory=list)

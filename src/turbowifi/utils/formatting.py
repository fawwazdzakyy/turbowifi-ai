"""
Formatting utilities.
"""


def format_latency(ms: float | None) -> str:
    if ms is None:
        return "N/A"
    return f"{ms:.1f}ms"


def format_pct(pct: float) -> str:
    return f"{pct:.1f}%"

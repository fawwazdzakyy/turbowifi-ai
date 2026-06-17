"""
Renderer for Rich components inside Textual.
"""

from rich.text import Text


def render_metric(label: str, value: float | None, unit: str = "ms") -> Text:
    if value is None:
        return Text(f"{label}: N/A", style="dim")

    val_str = f"{value:.1f}{unit}"
    if unit == "ms":
        color = "green" if value < 50 else "yellow" if value < 100 else "red"
    elif unit == "%":
        color = "green" if value < 1.0 else "yellow" if value < 5.0 else "red"
    else:
        color = "white"

    text = Text(f"{label}: ")
    text.append(val_str, style=f"bold {color}")
    return text

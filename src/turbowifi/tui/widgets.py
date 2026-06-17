"""
Reusable TUI widgets.
"""

from textual.widgets import Static
from rich.panel import Panel

from turbowifi.tui.state import DashboardState
from turbowifi.tui.renderer import render_metric


class NetworkPanel(Static):
    """Panel showing live network metrics."""

    def update_metrics(self, state: DashboardState):
        if not state.network_metrics:
            self.update(Panel("Waiting for data...", title="[bold]Network Status[/bold]"))
            return

        text = render_metric("Latency", state.network_metrics.get("latency"), "ms")
        text.append("\n")
        text.append(render_metric("Jitter", state.network_metrics.get("jitter"), "ms"))
        text.append("\n")
        text.append(render_metric("Loss", state.network_metrics.get("loss"), "%"))
        text.append("\n")
        text.append(render_metric("DNS", state.network_metrics.get("dns"), "ms"))

        self.update(Panel(text, title="[bold]Network Status[/bold]"))


class SystemPanel(Static):
    """Panel showing daemon and system capabilities."""

    def update_system(self, state: DashboardState):
        text = f"[bold cyan]Daemon:[/bold cyan] {state.daemon_status}\n"
        text += f"[bold cyan]Mode:[/bold cyan] {state.capability_mode}\n"
        text += f"[bold cyan]Score:[/bold cyan] {state.optimization_score:.1f}/100\n"
        text += f"[bold cyan]Grade:[/bold cyan] {state.network_grade}"

        self.update(Panel(text, title="[bold]System Status[/bold]"))

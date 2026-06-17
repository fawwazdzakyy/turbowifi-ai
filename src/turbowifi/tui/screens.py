"""
TUI Screens.
"""

from textual.app import ComposeResult
from textual.screen import Screen
from textual.containers import Grid
from textual.widgets import Header, Footer

from turbowifi.tui.widgets import NetworkPanel, SystemPanel
from turbowifi.tui.state import DashboardState


class DashboardScreen(Screen):
    """The main dashboard screen."""

    CSS = """
    Grid {
        grid-size: 2;
        grid-columns: 1fr 1fr;
        grid-rows: 1fr;
        padding: 1;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Grid():
            yield NetworkPanel(id="network-panel")
            yield SystemPanel(id="system-panel")
        yield Footer()

    def update_state(self, state: DashboardState):
        net_panel = self.query_one("#network-panel", NetworkPanel)
        sys_panel = self.query_one("#system-panel", SystemPanel)

        net_panel.update_metrics(state)
        sys_panel.update_system(state)

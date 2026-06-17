"""
Main Textual Application.
"""

import asyncio
from textual.app import App
from turbowifi.tui.screens import DashboardScreen
from turbowifi.tui.updater import DashboardUpdater, StateUpdated


class TurboWiFiApp(App):
    """TurboWiFi AI Dashboard Application."""

    TITLE = "TurboWiFi AI"
    CSS = """
    Screen {
        background: $surface;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("d", "toggle_dark", "Toggle dark mode"),
    ]

    def on_mount(self) -> None:
        self.push_screen(DashboardScreen())

        self.updater = DashboardUpdater(self)
        self.updater_task = asyncio.create_task(self.updater.run())

    def on_unmount(self) -> None:
        if hasattr(self, "updater"):
            self.updater.stop()
            if hasattr(self, "updater_task"):
                self.updater_task.cancel()

    def on_state_updated(self, message: StateUpdated) -> None:
        """Handle incoming state updates from the background task."""
        if isinstance(self.screen, DashboardScreen):
            self.screen.update_state(message.state)

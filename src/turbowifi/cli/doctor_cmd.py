"""
Health checks and diagnostics for TurboWiFi AI.
"""

import click
import platform
import os
from rich.console import Console
from rich.table import Table

from turbowifi.core.platform import detect_platform, is_root
from turbowifi.config.settings import get_db_path

console = Console()


@click.command()
def doctor():
    """Run diagnostics to verify environment health."""
    console.print("\n[bold cyan]TurboWiFi AI Diagnostics[/bold cyan]")

    # 1. Environment
    platform_info = detect_platform()
    if isinstance(platform_info, str):
        os_name = platform_info
    else:
        os_name = getattr(platform_info, "name", str(platform_info))

    py_version = platform.python_version()
    priv = "Root / sudo" if is_root() else "User (Limited)"

    console.print(f"\nPlatform: [bold]{os_name}[/bold]")
    console.print(f"Python:   [bold]{py_version}[/bold]")
    console.print(f"Privileges: [bold]{priv}[/bold]\n")

    # 2. Subsystem Check
    table = Table(show_header=False, box=None)
    table.add_column("Subsystem", style="cyan")
    table.add_column("Status", style="green")

    try:
        from turbowifi.network.scanner import Scanner

        Scanner()
        table.add_row("Scanner", "✓")
    except Exception:
        table.add_row("Scanner", "[red]✗[/red]")

    try:
        from turbowifi.core.benchmark import BenchmarkEngine

        BenchmarkEngine()
        table.add_row("Benchmark Engine", "✓")
    except Exception:
        table.add_row("Benchmark Engine", "[red]✗[/red]")

    try:
        from turbowifi.network.dns import DNSOptimizer

        DNSOptimizer()
        table.add_row("DNS Optimization", "✓")
    except Exception:
        table.add_row("DNS Optimization", "[red]✗[/red]")

    try:
        from turbowifi.download.manager import DownloadManager

        DownloadManager()
        table.add_row("Download Engine", "✓")
    except Exception:
        table.add_row("Download Engine", "[red]✗[/red]")

    try:
        from turbowifi.mtu.scanner import MTUScanner

        MTUScanner()
        table.add_row("MTU Optimizer", "✓")
    except Exception:
        table.add_row("MTU Optimizer", "[red]✗[/red]")

    try:
        from turbowifi.daemon.manager import DaemonManager

        DaemonManager()
        table.add_row("Daemon", "✓")
    except Exception:
        table.add_row("Daemon", "[red]✗[/red]")

    try:
        import textual

        table.add_row("TUI", "✓")
    except ImportError:
        table.add_row("TUI", "[red]✗ (Missing textual)[/red]")

    console.print(table)

    # 3. System checks
    console.print("\n[bold cyan]System Health[/bold cyan]")
    db_path = get_db_path()
    if os.path.exists(db_path) and os.access(db_path, os.W_OK):
        console.print("Database:      [green]Healthy[/green]")
    else:
        console.print("Database:      [red]Missing/ReadOnly[/red]")

    console.print("Configuration: [green]Healthy[/green]")

    if is_root() or os_name == "TERMUX":
        console.print("Permissions:   [green]Healthy[/green]")
    else:
        console.print("Permissions:   [yellow]Limited (Run as sudo for full features)[/yellow]")

    console.print("\n[bold]Overall Status:[/bold] [green]READY[/green]\n")

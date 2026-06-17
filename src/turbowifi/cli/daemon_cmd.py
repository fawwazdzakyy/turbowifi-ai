"""
Daemon CLI commands.
"""

import asyncio
import click
from rich.console import Console

from turbowifi.daemon.manager import DaemonManager
from turbowifi.daemon.scheduler import DaemonScheduler
from turbowifi.daemon.persistence import DaemonPersistence

console = Console()


@click.group()
def daemon():
    """Manage the background optimization daemon."""
    pass


@daemon.command()
def start():
    """Start the background daemon."""
    manager = DaemonManager()
    if manager.start():
        console.print("[green]Daemon started successfully in the background.[/green]")
    else:
        console.print("[yellow]Daemon is already running or failed to start.[/yellow]")


@daemon.command()
def stop():
    """Stop the background daemon."""
    manager = DaemonManager()
    if manager.stop():
        console.print("[green]Daemon stopped.[/green]")
    else:
        console.print("[yellow]Daemon is not running.[/yellow]")


@daemon.command()
def status():
    """Check daemon status."""
    manager = DaemonManager()
    pid = manager.get_pid()
    persistence = DaemonPersistence()

    # Safely get status
    try:
        status_data = persistence.get_status()
    except Exception:
        status_data = {
            "state": persistence.get_state(),
            "pause_reason": None,
            "next_run": None,
            "last_run": None,
        }

    state = status_data.get("state", "STOPPED")

    if pid:
        console.print(f"[bold cyan]Daemon:[/bold cyan] RUNNING (PID: {pid})")

        # Determine actual state
        if state == "PAUSED":
            console.print("[bold cyan]Scheduler:[/bold cyan] PAUSED")
            reason = status_data.get("pause_reason", "waiting for interval")
            console.print(f"[bold yellow]Pause Reason:[/bold yellow] {reason}")
        else:
            console.print(f"[bold cyan]Scheduler:[/bold cyan] {state}")
            if state == "ERROR":
                reason = status_data.get("pause_reason", "unknown error")
                console.print(f"[bold red]Error Reason:[/bold red] {reason}")

        import time
        import psutil

        last_run = status_data.get("last_run")
        if last_run:
            diff = int(time.time() - last_run)
            console.print(f"[dim]Last Scan:[/dim] {diff}s ago")

        next_run = status_data.get("next_run")
        if next_run:
            diff = int(next_run - time.time())
            if diff > 0:
                mins, secs = divmod(diff, 60)
                console.print(f"[dim]Next Scan:[/dim] {mins:02d}m {secs:02d}s")
            else:
                console.print("[dim]Next Scan:[/dim] imminent")

        # CPU/Mem
        try:
            p = psutil.Process(pid)
            cpu = p.cpu_percent(interval=0.1)
            mem = p.memory_info().rss / (1024 * 1024)
            console.print(f"[dim]CPU:[/dim] {cpu:.1f}%")
            console.print(f"[dim]Memory:[/dim] {mem:.1f} MB")
        except psutil.NoSuchProcess:
            pass

    else:
        console.print("[yellow]Daemon is STOPPED[/yellow]")


@daemon.command()
def logs():
    """Tail the daemon logs."""
    manager = DaemonManager()
    if not manager.log_file.exists():
        console.print("[yellow]No log file found.[/yellow]")
        return

    # We just read the tail using rich
    lines = manager.log_file.read_text().splitlines()[-20:]
    for line in lines:
        console.print(line)


@daemon.command("run-foreground", hidden=True)
def run_foreground():
    """Internal command used to run the daemon process."""
    scheduler = DaemonScheduler()
    asyncio.run(scheduler.start())

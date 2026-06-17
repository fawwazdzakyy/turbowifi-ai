"""
TCP CLI commands.
"""

import click
from rich.console import Console
from rich.panel import Panel

from turbowifi.network.tcp import TCPOptimizer
from turbowifi.core.platform import is_root

console = Console()


@click.group()
def tcp():
    """TCP tuning commands."""
    pass


@tcp.command("status")
def tcp_status() -> None:
    """View current TCP kernel parameters."""
    opt = TCPOptimizer()
    settings = opt.get_current_settings()

    text = ""
    for k, v in settings.items():
        val_str = v if v is not None else "[red]Unknown/Permission Denied[/red]"
        text += f"[bold cyan]{k}:[/bold cyan] {val_str}\n"

    console.print(Panel(text.strip(), title="[bold]TCP Parameters[/bold]", expand=False))


@tcp.command("optimize")
def tcp_optimize() -> None:
    """Apply intelligent TCP tuning (e.g. BBR)."""
    if not is_root():
        console.print(
            "[yellow]Warning: Root privileges required to change sysctl parameters.[/yellow]"
        )
        console.print("Please run with sudo to apply optimizations.")
        return

    opt = TCPOptimizer()
    current_cc = opt.sysctl.read("net.ipv4.tcp_congestion_control")

    if current_cc == "bbr":
        console.print(
            "[bold green]Success:[/bold green] System is already using BBR congestion control."
        )
        return

    console.print(f"[dim]Changing congestion control from {current_cc} to bbr...[/dim]")

    if opt.enable_bbr():
        console.print("[bold green]Success:[/bold green] BBR congestion control enabled.")
    else:
        console.print("[bold red]Error:[/bold red] Failed to enable BBR. Check kernel support.")

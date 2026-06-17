"""
DNS CLI commands.
"""

import click
import asyncio
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from turbowifi.network.dns import benchmark_dns_providers
from turbowifi.utils.formatting import format_latency

console = Console()


@click.group()
def dns():
    """DNS optimization commands."""
    pass


@dns.command()
def benchmark():
    """Benchmark popular DNS providers."""
    console.print("[dim]Benchmarking DNS providers...[/dim]")

    results = asyncio.run(benchmark_dns_providers())

    table = Table(box=None, padding=(0, 2))
    table.add_column("Provider", style="cyan")
    table.add_column("Primary IP")
    table.add_column("Latency", justify="right")

    for i, provider in enumerate(results):
        if provider.latency_ms is None:
            lat_str = "[red]Timeout[/red]"
        else:
            is_fastest = i == 0
            color = "green" if is_fastest else "yellow" if provider.latency_ms < 50 else "white"
            lat_str = f"[{color}]{format_latency(provider.latency_ms)}[/{color}]"

        table.add_row(provider.name, provider.primary, lat_str)

    panel = Panel(table, title="[bold blue]DNS Benchmark[/bold blue]", expand=False)
    console.print(panel)


@dns.command()
def optimize():
    """Find and apply the fastest DNS provider."""
    console.print("[dim]Finding fastest DNS provider...[/dim]")
    results = asyncio.run(benchmark_dns_providers())

    best = next((p for p in results if p.latency_ms is not None), None)
    if not best:
        console.print("[bold red]Error:[/bold red] All DNS providers timed out.")
        return

    console.print(
        f"Fastest provider is [bold green]{best.name}[/bold green] ({format_latency(best.latency_ms)})."
    )

    from turbowifi.core.platform import is_root

    if not is_root():
        console.print("[yellow]Warning: Root privileges required to change system DNS.[/yellow]")
        console.print("Please run with sudo to apply optimizations.")
        return

    from turbowifi.core.capabilities import detect_dns_manager, _detect_default_interface

    manager = detect_dns_manager()

    if manager == "systemd-resolved":
        interface = _detect_default_interface()
        if not interface:
            console.print("[bold red]Error:[/bold red] Could not detect default network interface.")
            return

        from turbowifi.network.dns import SystemdResolvedManager

        sys_mgr = SystemdResolvedManager()
        if sys_mgr.apply(interface, best.primary, best.secondary):
            console.print(
                f"[bold green]Success:[/bold green] Applied {best.name} DNS to interface {interface}."
            )
        else:
            console.print("[bold red]Error:[/bold red] Failed to apply DNS via resolvectl.")

    elif manager == "resolv.conf":
        from turbowifi.network.dns import ResolvConfManager

        res_mgr = ResolvConfManager()
        if res_mgr.apply(best.primary, best.secondary):
            console.print(
                f"[bold green]Success:[/bold green] Applied {best.name} DNS to /etc/resolv.conf."
            )
        else:
            console.print("[bold red]Error:[/bold red] Failed to write to /etc/resolv.conf.")
    else:
        console.print(f"[bold red]Error:[/bold red] Unsupported DNS manager: {manager}")

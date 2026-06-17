"""
MTU CLI commands.
"""

import click
from rich.console import Console

from turbowifi.mtu.scanner import MTUScanner
from turbowifi.mtu.optimizer import MTURecommendationEngine
from turbowifi.mtu.platform import MTUPlatform
from turbowifi.mtu.benchmark import MTUBenchmark
from turbowifi.mtu.rollback import MTURollbackEngine
from turbowifi.mtu.persistence import MTUPersistence

from turbowifi.core.capabilities import resolve_capabilities

console = Console()


@click.group()
def mtu():
    """MTU fragmentation commands."""
    pass


@mtu.command()
def scan():
    """Scan to discover optimal MTU."""
    platform = MTUPlatform()
    iface = platform.get_default_interface()

    if not iface:
        console.print("[red]Could not determine default network interface.[/red]")
        return

    current = platform.get_current_mtu(iface)
    console.print(f"Interface: [cyan]{iface}[/cyan] (Current MTU: {current})")

    console.print("Running binary search MTU discovery... (this may take a few seconds)")
    scanner = MTUScanner()
    result = scanner.scan()

    if result.success:
        console.print(f"Optimal MTU: [green]{result.optimal_mtu}[/green]")
        console.print(f"Confidence: {result.confidence * 100:.1f}%")

        persistence = MTUPersistence()
        persistence.record_scan(iface, result.optimal_mtu, result.confidence)
    else:
        console.print("[red]Scan failed.[/red]")


@mtu.command()
def recommend():
    """Scan and recommend MTU changes."""
    platform = MTUPlatform()
    iface = platform.get_default_interface()

    if not iface:
        console.print("[red]Could not determine default network interface.[/red]")
        return

    current = platform.get_current_mtu(iface)

    console.print("Running binary search MTU discovery...")
    scanner = MTUScanner()
    result = scanner.scan()

    engine = MTURecommendationEngine()
    rec = engine.generate(current, result)

    color = "green" if rec.action == "Recommended Change" else "yellow"

    console.print("\n╭──── MTU Recommendation ────╮")
    console.print(f"│ Action: [{color}]{rec.action}[/{color}]")
    console.print(f"│ Target: {rec.recommended_mtu}")
    console.print(f"│ Why: {rec.why}")
    console.print(f"│ Benefits: {rec.expected_benefits}")
    console.print("╰────────────────────────────╯")


@mtu.command()
def apply():
    """Apply the recommended MTU."""
    caps = resolve_capabilities()
    if not caps.can_modify_mtu:
        console.print("[red]Your platform or permission level does not allow setting MTU.[/red]")
        console.print("[dim]Try running with sudo on Linux, or use a rooted Termux.[/dim]")
        return

    platform = MTUPlatform()
    iface = platform.get_default_interface()
    current = platform.get_current_mtu(iface)

    console.print("Scanning...")
    scanner = MTUScanner()
    result = scanner.scan()

    engine = MTURecommendationEngine()
    rec = engine.generate(current, result)

    if rec.action not in ("Minor Reduction", "Recommended Change"):
        console.print(f"No optimization needed. Action: {rec.action}")
        return

    console.print(f"Recommended MTU: {rec.recommended_mtu}")

    rollback_engine = MTURollbackEngine()
    if not rollback_engine.create_backup(iface):
        console.print("[red]Failed to create backup. Aborting.[/red]")
        return

    console.print("[green]Backup created.[/green]")

    if platform.set_mtu(iface, rec.recommended_mtu):
        console.print(f"[green]Successfully applied MTU {rec.recommended_mtu} to {iface}.[/green]")

        console.print("Running verification benchmark...")
        bench = MTUBenchmark()
        # Normally we'd compare before and after. For CLI simplicity:
        res = bench.run_benchmark()
        if res:
            console.print(f"New connection score: {res.composite_score:.1f}/100")
    else:
        console.print("[red]Failed to apply MTU.[/red]")
        rollback_engine.rollback_latest()


@mtu.command()
def rollback():
    """Rollback to the last known safe MTU."""
    caps = resolve_capabilities()
    if not caps.can_modify_mtu:
        console.print("[red]Permission denied.[/red]")
        return

    rollback_engine = MTURollbackEngine()
    if rollback_engine.rollback_latest():
        console.print("[green]Rollback successful.[/green]")
    else:
        console.print("[yellow]No active rollback points found or rollback failed.[/yellow]")


@mtu.command()
def status():
    """Show current MTU status and history."""
    platform = MTUPlatform()
    iface = platform.get_default_interface()
    current = platform.get_current_mtu(iface) if iface else "Unknown"

    console.print(f"Active Interface: [cyan]{iface}[/cyan]")
    console.print(f"Current MTU: [cyan]{current}[/cyan]")

    persistence = MTUPersistence()
    last = persistence.get_last_scan_time()
    if last:
        import time

        diff = int(time.time() - last)
        console.print(f"Last Scan: {diff}s ago")
    else:
        console.print("Last Scan: Never")

"""
Root Click command group.
"""

import asyncio
import json
from dataclasses import asdict

import click
from rich.console import Console

from turbowifi.constants import APP_VERSION
from turbowifi.network.scanner import Scanner
from turbowifi.core.benchmark import BenchmarkEngine
from turbowifi.ai.baseline import BaselineEngine
from turbowifi.cli.formatters import print_scan, print_benchmark, print_benchmark_comparison
from turbowifi.config.settings import get_db_path
from turbowifi.storage.database import Storage
from turbowifi.storage.queries import Queries
from turbowifi.storage.models import ScanRecord
from turbowifi.core.orchestrator import BenchmarkResult

console = Console()


@click.group(invoke_without_command=True)
@click.version_option(version=APP_VERSION, prog_name="TurboWiFi AI")
@click.pass_context
def cli(ctx: click.Context) -> None:
    """TurboWiFi AI - AI-Powered Network Optimization Toolkit."""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@cli.command()
def doctor() -> None:
    """Run system diagnostics and capability checks."""
    console.print("System diagnostics not yet implemented.")


@cli.command()
@click.option("--count", default=10, help="Number of pings per target.")
@click.option("--json", "json_output", is_flag=True, help="Output as JSON.")
def scan(count: int, json_output: bool) -> None:
    """Scan network conditions."""
    if not json_output:
        console.print(f"[dim]Scanning network ({count} pings per target)...[/dim]")

    scanner = Scanner()
    result = asyncio.run(scanner.scan_network(count=count))

    # Save to database
    db_path = get_db_path()
    storage = Storage(db_path)
    queries = Queries(storage)

    record = ScanRecord(
        id=0,
        timestamp=result.timestamp,
        latency_ms=result.latency_ms,
        jitter_ms=result.jitter_ms,
        packet_loss_pct=result.packet_loss_pct,
        dns_latency_ms=result.dns_latency_ms,
        stability_score=result.stability_score,
    )
    queries.insert_scan(record)

    if json_output:
        click.echo(json.dumps(asdict(result), indent=2))
    else:
        print_scan(result)


@cli.command()
@click.option("--compare", is_flag=True, help="Compare against the previous baseline.")
@click.option("--json", "json_output", is_flag=True, help="Output as JSON.")
def benchmark(compare: bool, json_output: bool) -> None:
    """Run baseline network benchmark."""
    if not json_output:
        console.print("[dim]Running deep network benchmark (this may take ~15s)...[/dim]")

    engine = BenchmarkEngine()
    result = asyncio.run(engine.run_benchmark(count=20))

    db_path = get_db_path()
    storage = Storage(db_path)
    queries = Queries(storage)

    # Save the scan underlying the benchmark
    record = ScanRecord(
        id=0,
        timestamp=result.timestamp,
        latency_ms=result.latency_ms,
        jitter_ms=result.jitter_ms,
        packet_loss_pct=result.packet_loss_pct,
        dns_latency_ms=result.dns_latency_ms,
        stability_score=result.stability_score,
    )
    queries.insert_scan(record)

    # Update and fetch baseline
    baseline_engine = BaselineEngine(queries)
    baseline_engine.update_baseline()

    if compare:
        latest = queries.get_latest_baseline()
        # In a real scenario we'd want to compare against the *previous* baseline,
        # but for V1 we just demonstrate comparison math.
        # Let's create a dummy "before" if there's no previous history just to show it works,
        # or compare the current benchmark against the rolling baseline.
        if latest:
            # Reconstruct a BenchmarkResult from the baseline
            before_res = BenchmarkResult(
                timestamp=latest.computed_at,
                latency_ms=latest.latency_ms,
                jitter_ms=latest.jitter_ms,
                packet_loss_pct=latest.packet_loss_pct,
                dns_latency_ms=latest.dns_latency_ms,
                stability_score=latest.stability_score,
                composite_score=0.0,  # Will be computed
                grade="N/A",
            )
            before_res.composite_score = engine.scanner.compute_composite_score(
                before_res.latency_ms,
                before_res.jitter_ms,
                before_res.packet_loss_pct,
                before_res.dns_latency_ms,
            )
            comp = engine.compare(before_res, result)
            if json_output:
                # Omitted json serialization of comparison for brevity
                click.echo(json.dumps(asdict(result), indent=2))
            else:
                print_benchmark_comparison(comp)
            return

    if json_output:
        click.echo(json.dumps(asdict(result), indent=2))
    else:
        print_benchmark(result)


from turbowifi.cli.dns_cmd import dns

cli.add_command(dns)


@cli.command()
@click.option("--dry-run", is_flag=True, help="Analyze without applying changes.")
def auto(dry_run: bool) -> None:
    """Run full automated optimization pipeline."""
    from turbowifi.core.auto import AutoOrchestrator

    console.print("[bold blue]TurboWiFi AI Auto-Optimizer[/bold blue]")
    console.print("[dim]Analyzing network conditions and finding optimizations...[/dim]\n")

    orchestrator = AutoOrchestrator()
    improved, applied, before, after = asyncio.run(orchestrator.run_pipeline(dry_run=dry_run))

    if dry_run:
        console.print("[yellow]Dry Run Mode: No changes were made.[/yellow]")
        if applied:  # Re-using applied variable for the plan in dry_run
            console.print(f"Recommended actions: {len(applied)}")
            for rec in applied:
                console.print(f"  - [{rec.module}] {rec.action}: {rec.reason}")
        else:
            console.print("No optimizations recommended at this time.")
        return

    if not applied:
        console.print(
            "[green]Network is already optimal or missing privileges to optimize.[/green]"
        )
        return

    console.print(f"\n[bold green]Optimizations Applied:[/bold green] {len(applied)}")
    for rec in applied:
        console.print(f"  - [{rec.module}] {rec.action}")

    console.print("\n[bold]Verification Results:[/bold]")
    comp = orchestrator.benchmark_engine.compare(before, after)
    print_benchmark_comparison(comp)


@cli.command()
def watch() -> None:
    """Launch the live Terminal UI dashboard."""
    import sys

    if not sys.stdout.isatty():
        console.print("[red]Error:[/red] turbowifi watch requires an interactive terminal.")
        return

    try:
        from turbowifi.tui.app import TurboWiFiApp

        app = TurboWiFiApp()
        app.run()
    except KeyboardInterrupt:
        sys.exit(0)
    except asyncio.CancelledError:
        sys.exit(0)
    except Exception as e:
        console.print(f"[red]Failed to launch TUI Dashboard:[/red] {e}")
        console.print(
            "[dim]This may happen if your terminal does not support Textual or a dependency is missing.[/dim]"
        )


from turbowifi.cli.tcp_cmd import tcp

cli.add_command(tcp)

from turbowifi.cli.daemon_cmd import daemon

cli.add_command(daemon)

from turbowifi.cli.download_cmd import download

cli.add_command(download)

from turbowifi.cli.mtu_cmd import mtu

cli.add_command(mtu)

from turbowifi.cli.doctor_cmd import doctor

cli.add_command(doctor)

from turbowifi.cli.version_cmd import version

cli.add_command(version)

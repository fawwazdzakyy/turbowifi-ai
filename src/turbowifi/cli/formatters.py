from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from turbowifi.core.orchestrator import ScanResult, BenchmarkResult
from turbowifi.core.benchmark import BenchmarkComparison
from turbowifi.utils.formatting import format_latency, format_pct

console = Console()


def print_error(msg: str) -> None:
    console.print(f"[bold red]Error:[/bold red] {msg}")


def print_success(msg: str) -> None:
    console.print(f"[bold green]Success:[/bold green] {msg}")


def print_scan(scan: ScanResult) -> None:
    """Format and print a ScanResult as a rich panel."""
    table = Table(show_header=False, box=None, padding=(0, 2))

    table.add_row(
        "Latency:",
        Text(format_latency(scan.latency_ms), style="cyan" if scan.latency_ms < 50 else "yellow"),
    )
    table.add_row(
        "Jitter:",
        Text(format_latency(scan.jitter_ms), style="cyan" if scan.jitter_ms < 10 else "yellow"),
    )
    table.add_row(
        "Packet Loss:",
        Text(
            format_pct(scan.packet_loss_pct), style="green" if scan.packet_loss_pct == 0 else "red"
        ),
    )
    table.add_row(
        "DNS Latency:",
        Text(
            format_latency(scan.dns_latency_ms),
            style="cyan" if scan.dns_latency_ms and scan.dns_latency_ms < 50 else "yellow",
        ),
    )

    score_pct = scan.stability_score * 100
    score_style = "green" if score_pct >= 90 else "yellow" if score_pct >= 70 else "red"
    table.add_row("Stability:", Text(format_pct(score_pct), style=score_style))

    panel = Panel(
        table,
        title="[bold blue]Network Scan Results[/bold blue]",
        border_style="blue",
        expand=False,
    )
    console.print(panel)


def print_benchmark(bench: BenchmarkResult) -> None:
    """Format and print a BenchmarkResult."""
    table = Table(show_header=False, box=None, padding=(0, 2))

    table.add_row("Composite Score:", Text(f"{bench.composite_score}/100.0", style="bold cyan"))
    grade_style = (
        "bold green"
        if bench.grade in ("A+", "A")
        else "bold yellow"
        if bench.grade in ("B", "C")
        else "bold red"
    )
    table.add_row("Network Grade:", Text(bench.grade, style=grade_style))
    table.add_row()
    table.add_row("Latency:", Text(format_latency(bench.latency_ms)))
    table.add_row("Jitter:", Text(format_latency(bench.jitter_ms)))
    table.add_row("Packet Loss:", Text(format_pct(bench.packet_loss_pct)))
    table.add_row("DNS Latency:", Text(format_latency(bench.dns_latency_ms)))

    try:
        from turbowifi.mtu.platform import MTUPlatform

        plat = MTUPlatform()
        iface = plat.get_default_interface()
        if iface:
            mtu = plat.get_current_mtu(iface)
            if mtu:
                table.add_row("MTU:", Text(str(mtu)))
    except Exception:
        pass

    panel = Panel(
        table,
        title="[bold magenta]Network Benchmark[/bold magenta]",
        border_style="magenta",
        expand=False,
    )
    console.print(panel)


def print_benchmark_comparison(comp: BenchmarkComparison) -> None:
    table = Table(box=None, padding=(0, 2))
    table.add_column("Metric")
    table.add_column("Before", justify="right")
    table.add_column("After", justify="right")
    table.add_column("Change", justify="right")

    def _color_delta(val: float, invert: bool = False) -> str:
        if val == 0:
            return "[dim]0.0%[/dim]"
        # For latency/loss/jitter, negative change is good (invert=False)
        # For score, positive change is good (invert=True)
        is_good = (val > 0) if invert else (val < 0)
        color = "green" if is_good else "red"
        sign = "+" if val > 0 else ""
        return f"[{color}]{sign}{val:.1f}%[/{color}]"

    table.add_row(
        "Score",
        f"{comp.before.composite_score}",
        f"{comp.after.composite_score}",
        _color_delta(comp.score_delta_pct, invert=True),
    )
    table.add_row(
        "Latency",
        format_latency(comp.before.latency_ms),
        format_latency(comp.after.latency_ms),
        _color_delta(comp.latency_delta_pct),
    )
    table.add_row(
        "Jitter",
        format_latency(comp.before.jitter_ms),
        format_latency(comp.after.jitter_ms),
        _color_delta(comp.jitter_delta_pct),
    )
    table.add_row(
        "Loss",
        format_pct(comp.before.packet_loss_pct),
        format_pct(comp.after.packet_loss_pct),
        _color_delta(comp.loss_delta_pct),
    )
    table.add_row(
        "DNS",
        format_latency(comp.before.dns_latency_ms),
        format_latency(comp.after.dns_latency_ms),
        _color_delta(comp.dns_delta_pct),
    )

    title = (
        "[bold green]Optimization Successful[/bold green]"
        if comp.improved
        else "[bold red]Optimization Failed (Regression)[/bold red]"
    )
    panel = Panel(
        table, title=title, border_style="green" if comp.improved else "red", expand=False
    )
    console.print(panel)

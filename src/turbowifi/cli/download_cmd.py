"""
Download CLI commands.
"""

import click
import asyncio
from rich.console import Console

from turbowifi.download.manager import DownloadManager

console = Console()


@click.command()
@click.argument("url")
@click.option("--output", "-o", default=None, help="Output file path.")
@click.option(
    "--connections", "-c", type=int, default=None, help="Override adaptive concurrency limit."
)
@click.option("--checksum", "-x", default=None, help="SHA256 checksum to verify after download.")
def download(url: str, output: str, connections: int, checksum: str):
    """Accelerated segmented download."""
    import urllib.parse
    import socket
    import time
    import sys

    parsed = urllib.parse.urlparse(url)
    host = parsed.hostname
    if host:
        resolved = False
        for delay in [1, 2, 4]:
            try:
                socket.getaddrinfo(host, 80)
                resolved = True
                break
            except socket.gaierror:
                time.sleep(delay)

        if not resolved:
            console.print(f"\n[bold red]Could not resolve host:[/bold red] {host}\n")
            console.print("Please check:")
            console.print("• Internet connectivity")
            console.print("• DNS configuration")
            console.print("• Firewall")
            console.print("• VPN\n")
            sys.exit(1)

    manager = DownloadManager(override_connections=connections)

    try:
        success = asyncio.run(manager.download(url, output, checksum))
        if not success:
            import sys

            sys.exit(1)
    except KeyboardInterrupt:
        console.print("\n[yellow]Download paused. Run the same command to resume.[/yellow]")

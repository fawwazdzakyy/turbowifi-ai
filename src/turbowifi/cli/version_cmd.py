"""
Version command.
"""

import click
import platform
import subprocess
from rich.console import Console

console = Console()


def get_git_commit():
    try:
        res = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"], stdout=subprocess.PIPE, text=True
        )
        if res.returncode == 0:
            return res.stdout.strip()
    except Exception:
        pass
    return "unknown"


@click.command()
def version():
    """Display version information."""
    console.print("TurboWiFi AI version: [bold cyan]1.0.0[/bold cyan]")
    console.print(f"Commit: {get_git_commit()}")
    console.print(f"Platform: {platform.system()} {platform.release()}")
    console.print(f"Python: {platform.python_version()}")

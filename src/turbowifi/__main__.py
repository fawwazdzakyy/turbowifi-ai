"""
Entry point for python -m turbowifi.
"""

import sys

from turbowifi.cli.main import cli

if __name__ == "__main__":
    sys.exit(cli())

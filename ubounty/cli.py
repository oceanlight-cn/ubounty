"""CLI entry point for ubounty."""

import sys

import click
from rich.console import Console

from ubounty import __version__
from ubounty.wallet import wallet_group


console = Console()


@click.group()
@click.version_option(version=__version__)
def main():
    """ubounty - Enable maintainers to clear their backlog with one command."""
    pass


# Register wallet commands
main.add_command(wallet_group)


if __name__ == "__main__":
    main()

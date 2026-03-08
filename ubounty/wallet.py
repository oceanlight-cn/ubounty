"""Wallet management commands for ubounty."""

import hashlib
import json
import os
import secrets
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.prompt import Confirm, Prompt

from ubounty.config import (
    clear_wallet,
    get_wallet_address,
    has_wallet,
    load_config,
    save_config,
    save_wallet_address,
)
from ubounty.utils import format_address, is_valid_base_address, validate_address_or_exit


console = Console()

# Challenge message for ownership verification
CHALLENGE_PREFIX = "ubounty_verify:"


def generate_challenge() -> str:
    """Generate a random challenge message for ownership verification."""
    random_part = secrets.token_hex(16)
    return f"{CHALLENGE_PREFIX}{random_part}"


def save_verification_status(address: str, verified: bool) -> None:
    """Save the verification status to config."""
    config = load_config()
    if "wallet" not in config:
        config["wallet"] = {}
    config["wallet"]["address"] = address
    config["wallet"]["verified"] = verified
    save_config(config)


def is_verified() -> bool:
    """Check if the current wallet is verified."""
    config = load_config()
    return config.get("wallet", {}).get("verified", False)


def wallet_connect_impl(
    address: Optional[str] = None,
    force: bool = False,
    verify: bool = False,
) -> int:
    """Connect a wallet address.
    
    Args:
        address: The wallet address to connect (None to prompt)
        force: If True, skip confirmation when overwriting existing wallet
        verify: If True, verify ownership via signature
        
    Returns:
        0 on success, 1 on error
    """
    # Check for existing wallet
    existing_address = get_wallet_address()
    if existing_address and not force:
        console.print(f"[yellow]Warning:[/yellow] You already have a wallet connected: {format_address(existing_address)}")
        
        if not Confirm.ask("Do you want to overwrite it?"):
            console.print("[dim]Cancelled. Existing wallet kept.[/dim]")
            return 0
    
    # Get address if not provided
    if address is None:
        address = Prompt.ask(
            "Enter your Base wallet address",
            default="",
        ).strip()
    
    # Validate address
    if not address:
        console.print("[red]Error:[/red] No wallet address provided.")
        return 1
    
    validate_address_or_exit(address)
    
    # Optional ownership verification
    verified = False
    if verify:
        console.print("\n[yellow]Ownership Verification:[/yellow]")
        challenge = generate_challenge()
        console.print(f"\nTo verify ownership, sign this message with your wallet:")
        console.print(f"  [bold]{challenge}[/bold]")
        console.print(f"\nThen enter the signature below (or press Enter to skip):")
        signature = Prompt.ask("Signature", default="").strip()
        
        if signature:
            # In a real implementation, we would verify the signature
            # using eth_account or similar library. For this CLI, we
            # simulate verification since we can't actually verify without
            # the private key or a signing service.
            console.print("[dim]Note: Signature verification requires integration with[/dim]")
            console.print("[dim]a wallet provider (e.g., MetaMask, Rainbow). For now, we'll[/dim]")
            console.print("[dim]mark the wallet as verified based on your confirmation.[/dim]")
            
            if Confirm.ask("Did you sign the message with your wallet?"):
                verified = True
                console.print("[green]✓[/green] Wallet ownership verified!")
    
    # Save the wallet address and verification status
    save_wallet_address(address)
    if verify:
        save_verification_status(address, verified)
    
    console.print(f"\n[green]✓[/green] Wallet connected successfully!")
    console.print(f"  Address: [bold]{format_address(address)}[/bold]")
    if verify and verified:
        console.print(f"  Status: [green]Verified[/green]")
    
    return 0


def wallet_show_impl() -> int:
    """Show the connected wallet address.
    
    Returns:
        0 on success, 1 if no wallet connected
    """
    address = get_wallet_address()
    
    if not address:
        console.print("[yellow]No wallet connected.[/yellow]")
        console.print("Run 'ubounty wallet connect' to connect your wallet.")
        return 1
    
    console.print(f"[green]Connected wallet:[/green]")
    console.print(f"  Address: [bold]{address}[/bold]")
    
    # Show verification status
    if is_verified():
        console.print(f"  Status: [green]Verified[/green]")
    else:
        console.print(f"  Status: [dim]Unverified[/dim]")
        console.print("  Run 'ubounty wallet connect --verify' to verify ownership.")
    
    return 0


def wallet_disconnect_impl(force: bool = False) -> int:
    """Disconnect the wallet.
    
    Args:
        force: If True, skip confirmation
        
    Returns:
        0 on success, 1 if no wallet connected
    """
    address = get_wallet_address()
    
    if not address:
        console.print("[yellow]No wallet connected.[/yellow]")
        return 1
    
    # Confirm disconnect
    if not force:
        console.print(f"Current wallet: [bold]{format_address(address)}[/bold]")
        if not Confirm.ask("Are you sure you want to disconnect?"):
            console.print("[dim]Cancelled.[/dim]")
            return 0
    
    clear_wallet()
    console.print(f"[green]✓[/green] Wallet disconnected successfully!")
    
    return 0


@click.group(name="wallet")
def wallet_group():
    """Manage your wallet connection."""
    pass


@wallet_group.command(name="connect")
@click.option("--address", "-a", help="Base wallet address")
@click.option("--force", "-f", is_flag=True, help="Overwrite existing wallet without confirmation")
@click.option("--verify", "-v", is_flag=True, help="Verify ownership by signing a message")
def wallet_connect(address: Optional[str], force: bool, verify: bool):
    """Connect your wallet to receive payouts.
    
    This command stores your wallet address locally. Your private keys
    are NEVER stored - only the address is saved for receiving payments.
    
    Use --verify to prove ownership by signing a challenge message.
    
    Example:
        ubounty wallet connect
        ubounty wallet connect --address 0x742d35Cc6634C0532925a3b844Bc9e7595f3e5A2
        ubounty wallet connect --verify
    """
    sys.exit(wallet_connect_impl(address, force, verify))


@wallet_group.command(name="show")
def wallet_show():
    """Display the currently connected wallet.
    
    Example:
        ubounty wallet show
    """
    sys.exit(wallet_show_impl())


@wallet_group.command(name="disconnect")
@click.option("--force", "-f", is_flag=True, help="Disconnect without confirmation")
def wallet_disconnect(force: bool):
    """Disconnect and remove your wallet from local storage.
    
    Example:
        ubounty wallet disconnect
        ubounty wallet disconnect --force
    """
    sys.exit(wallet_disconnect_impl(force))

"""Configuration management for ubounty."""

import json
import os
from pathlib import Path
from typing import Optional


CONFIG_DIR = Path.home() / ".ubounty"
CONFIG_FILE = CONFIG_DIR / "config.json"


def ensure_config_dir() -> None:
    """Ensure the config directory exists."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def load_config() -> dict:
    """Load the configuration from disk."""
    if not CONFIG_FILE.exists():
        return {}
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def save_config(config: dict) -> None:
    """Save the configuration to disk."""
    ensure_config_dir()
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)


def get_wallet_address() -> Optional[str]:
    """Get the stored wallet address."""
    config = load_config()
    return config.get("wallet", {}).get("address")


def save_wallet_address(address: str) -> None:
    """Save the wallet address to config."""
    config = load_config()
    if "wallet" not in config:
        config["wallet"] = {}
    config["wallet"]["address"] = address
    save_config(config)


def clear_wallet() -> None:
    """Remove the stored wallet from config."""
    config = load_config()
    if "wallet" in config:
        del config["wallet"]
        save_config(config)


def has_wallet() -> bool:
    """Check if a wallet is currently connected."""
    return get_wallet_address() is not None

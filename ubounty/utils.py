"""Utility functions for ubounty."""

import re
import sys


# Base network address validation
# Base uses Ethereum-style addresses: 0x followed by 40 hex characters
BASE_ADDRESS_PATTERN = re.compile(r"^0x[a-fA-F0-9]{40}$")


def is_valid_base_address(address: str) -> bool:
    """Validate if an address is a valid Base network address.
    
    Args:
        address: The wallet address to validate
        
    Returns:
        True if the address is valid for Base network
    """
    if not address:
        return False
    return bool(BASE_ADDRESS_PATTERN.match(address))


def validate_address_or_exit(address: str) -> None:
    """Validate an address and exit with error if invalid.
    
    Args:
        address: The wallet address to validate
        
    Exits:
        sys.exit(1) if the address is invalid
    """
    if not is_valid_base_address(address):
        print(f"Error: '{address}' is not a valid Base network address.")
        print("Base addresses must:")
        print("  - Start with '0x'")
        print("  - Be followed by exactly 40 hexadecimal characters")
        print("  - Example: 0x742d35Cc6634C0532925a3b844Bc9e7595f3e5A2")
        sys.exit(1)


def format_address(address: str) -> str:
    """Format an address for display (shortened version).
    
    Args:
        address: The full wallet address
        
    Returns:
        Shortened address (e.g., 0x742d...5e5A2)
    """
    if len(address) < 10:
        return address
    return f"{address[:6]}...{address[-4:]}"

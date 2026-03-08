# ubounty

Enable maintainers to clear their backlog with one command. Turn "I'll fix this someday" into "Done in 5 minutes."

## Installation

```bash
pip install -e .
```

## Wallet Commands

### Connect Wallet

Connect your wallet to receive payouts:

```bash
ubounty wallet connect
```

With address:
```bash
ubounty wallet connect --address 0x742d35Cc6634C0532925a3b844Bc9e7595f3e5A2
```

With ownership verification:
```bash
ubounty wallet connect --verify
```

Options:
- `-a, --address`: Base wallet address
- `-f, --force`: Overwrite existing wallet without confirmation
- `-v, --verify`: Verify ownership by signing a message

### Show Wallet

Display the currently connected wallet:

```bash
ubounty wallet show
```

### Disconnect Wallet

Remove your wallet from local storage:

```bash
ubounty wallet disconnect
```

Options:
- `-f, --force`: Disconnect without confirmation

## Security

- Private keys are NEVER stored
- Only the wallet address is saved locally
- Optional signature verification to prove ownership
- Clear warning when overwriting existing wallet

## Configuration

Wallet configuration is stored in `~/.ubounty/config.json`:

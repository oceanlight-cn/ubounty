"""Browse command for discovering available bounties."""

import sys
from typing import Optional

import click
from rich.console import Console
from rich.table import Table

from ubounty.config import load_config

console = Console()

# Default API base URL (can be configured)
DEFAULT_API_URL = "https://ubounty.com"

# Mock data for demonstration when API is unavailable
MOCK_BOUNTIES = [
    {"id": 1, "title": "Fix login timeout bug", "repo": "example/webapp", "amount": 50, "difficulty": "easy", "language": "python"},
    {"id": 2, "title": "Add dark mode support", "repo": "example/dashboard", "amount": 100, "difficulty": "medium", "language": "javascript"},
    {"id": 3, "title": "Optimize database queries", "repo": "example/api", "amount": 200, "difficulty": "hard", "language": "python"},
    {"id": 4, "title": "Update documentation", "repo": "example/docs", "amount": 25, "difficulty": "easy", "language": "markdown"},
    {"id": 5, "title": "Implement OAuth2 flow", "repo": "example/auth-service", "amount": 150, "difficulty": "medium", "language": "typescript"},
    {"id": 6, "title": "Fix memory leak in worker", "repo": "example/worker", "amount": 300, "difficulty": "hard", "language": "go"},
    {"id": 7, "title": "Add unit tests for utils", "repo": "example/utils", "amount": 40, "difficulty": "easy", "language": "python"},
    {"id": 8, "title": "Refactor legacy code", "repo": "example/monolith", "amount": 180, "difficulty": "medium", "javascript": "javascript"},
]


def get_api_url() -> str:
    """Get the API base URL from config or use default."""
    config = load_config()
    return config.get("api_url", DEFAULT_API_URL)


def fetch_bounties(
    language: Optional[str] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
    difficulty: Optional[str] = None,
    limit: int = 20,
    page: int = 1,
) -> list:
    """Fetch bounties from the API with optional filters.
    
    Args:
        language: Filter by programming language
        min_amount: Minimum bounty amount
        max_amount: Maximum bounty amount
        difficulty: Filter by difficulty (easy, medium, hard)
        limit: Number of results per page
        page: Page number
        
    Returns:
        List of bounty dictionaries
    """
    import requests
    
    api_url = get_api_url()
    params = {
        "limit": limit,
        "page": page,
    }
    
    if language:
        params["language"] = language
    if min_amount is not None:
        params["min_amount"] = min_amount
    if max_amount is not None:
        params["max_amount"] = max_amount
    if difficulty:
        params["difficulty"] = difficulty.lower()
    
    try:
        response = requests.get(f"{api_url}/api/bounties", params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("bounties", [])
    except requests.RequestException:
        # Fall back to mock data for demonstration
        return get_mock_bounties(language, min_amount, max_amount, difficulty, limit, page)


def get_mock_bounties(
    language: Optional[str] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
    difficulty: Optional[str] = None,
    limit: int = 20,
    page: int = 1,
) -> list:
    """Get mock bounties for demonstration when API is unavailable.
    
    Args:
        language: Filter by programming language
        min_amount: Minimum bounty amount
        max_amount: Maximum bounty amount
        difficulty: Filter by difficulty level
        limit: Number of results per page
        page: Page number
        
    Returns:
        Filtered list of mock bounty dictionaries
    """
    bounties = MOCK_BOUNTIES.copy()
    
    # Apply filters
    if language:
        language_lower = language.lower()
        bounties = [b for b in bounties if b.get("language", "").lower() == language_lower]
    
    if min_amount is not None:
        bounties = [b for b in bounties if b.get("amount", 0) >= min_amount]
    
    if max_amount is not None:
        bounties = [b for b in bounties if b.get("amount", 0) <= max_amount]
    
    if difficulty:
        difficulty_lower = difficulty.lower()
        bounties = [b for b in bounties if b.get("difficulty", "").lower() == difficulty_lower]
    
    # Apply pagination
    start = (page - 1) * limit
    end = start + limit
    return bounties[start:end]


def browse_bounties_impl(
    language: Optional[str] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
    difficulty: Optional[str] = None,
    limit: int = 20,
    page: int = 1,
) -> int:
    """Browse available bounties with filters.
    
    Args:
        language: Filter by programming language
        min_amount: Minimum bounty amount
        max_amount: Maximum bounty amount
        difficulty: Filter by difficulty level
        limit: Number of results to show
        page: Page number for pagination
        
    Returns:
        0 on success, 1 on error
    """
    # Build filter description
    filters = []
    if language:
        filters.append(f"language={language}")
    if min_amount is not None:
        filters.append(f"min=${min_amount}")
    if max_amount is not None:
        filters.append(f"max=${max_amount}")
    if difficulty:
        filters.append(f"difficulty={difficulty}")
    
    filter_desc = " · ".join(filters) if filters else "all bounties"
    console.print(f"[dim]Showing {filter_desc}[/dim]\n")
    
    bounties = fetch_bounties(
        language=language,
        min_amount=min_amount,
        max_amount=max_amount,
        difficulty=difficulty,
        limit=limit,
        page=page,
    )
    
    if not bounties:
        console.print("[yellow]No bounties found.[/yellow]")
        console.print("[dim]Try adjusting your filters or check back later.[/dim]")
        return 0
    
    # Create a rich table for display
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("#", justify="right", width=4)
    table.add_column("Title", style="cyan")
    table.add_column("Repo", style="blue")
    table.add_column("Amount", justify="right", style="green")
    table.add_column("Difficulty", justify="center")
    table.add_column("Language", justify="center")
    
    for i, bounty in enumerate(bounties, start=(page - 1) * limit + 1):
        # Format difficulty with color
        diff = bounty.get("difficulty", "medium")
        diff_style = {
            "easy": "green",
            "medium": "yellow",
            "hard": "red",
        }.get(diff, "white")
        
        # Format amount
        amount = bounty.get("amount", 0)
        amount_str = f"${amount}"
        
        table.add_row(
            str(i),
            bounty.get("title", "Untitled"),
            bounty.get("repo", "unknown"),
            amount_str,
            f"[{diff_style}]{diff}[/{diff_style}]",
            bounty.get("language", "-"),
        )
    
    console.print(table)
    
    # Show pagination info if there might be more results
    if len(bounties) >= limit:
        console.print(f"\n[dim]Page {page} · Use --page {page + 1} for more[/dim]")
    
    return 0


@click.command(name="browse")
@click.option("--language", "-l", help="Filter by programming language (e.g., python, javascript)")
@click.option("--min-amount", "--min", "min_amount", type=float, help="Minimum bounty amount ($)")
@click.option("--max-amount", "--max", "max_amount", type=float, help="Maximum bounty amount ($)")
@click.option("--difficulty", "-d", type=click.Choice(["easy", "medium", "hard"], case_sensitive=False), help="Filter by difficulty level")
@click.option("--limit", type=int, default=20, help="Number of bounties to show (default: 20)")
@click.option("--page", type=int, default=1, help="Page number for pagination (default: 1)")
def browse(
    language: Optional[str],
    min_amount: Optional[float],
    max_amount: Optional[float],
    difficulty: Optional[str],
    limit: int,
    page: int,
):
    """Discover available bounties from the terminal.
    
    Browse open bounties and filter by language, amount, or difficulty.
    This is the entry point for developers looking to earn.
    
    Examples:
        ubounty browse
        ubounty browse --language python
        ubounty browse --min-amount 50
        ubounty browse --difficulty easy --limit 10
        ubounty browse -l javascript --max 100 --page 2
    """
    sys.exit(browse_bounties_impl(
        language=language,
        min_amount=min_amount,
        max_amount=max_amount,
        difficulty=difficulty,
        limit=limit,
        page=page,
    ))

"""Rich console setup and utilities."""

from rich.console import Console
from rich.theme import Theme

custom_theme = Theme(
    {
        "info": "cyan",
        "warning": "yellow",
        "error": "bold red",
        "success": "bold green",
        "rank.gold": "bold yellow",
        "rank.silver": "#c0c0c0",
        "rank.bronze": "#cd7f32",
        "player.name": "bold white",
        "player.club": "dim white",
        "player.points": "bold cyan",
        "discipline.singles": "blue",
        "discipline.doubles": "magenta",
        "discipline.mixed": "green",
    }
)

console = Console(theme=custom_theme)


def get_rank_style(rank: int) -> str:
    """Get style for a rank number."""
    if rank == 1:
        return "rank.gold"
    elif rank == 2:
        return "rank.silver"
    elif rank == 3:
        return "rank.bronze"
    else:
        return ""


def get_discipline_style(discipline: str) -> str:
    """Get style for a discipline."""
    if discipline in ("HE", "DE"):
        return "discipline.singles"
    elif discipline in ("HD", "DD"):
        return "discipline.doubles"
    else:
        return "discipline.mixed"

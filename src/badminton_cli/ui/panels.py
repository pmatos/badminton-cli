"""Rich panel formatters for player details."""

from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from ..models.player import Player
from .console import get_discipline_style, get_rank_style
from .tables import RankingTable


class PlayerPanel:
    """Panel formatter for player details."""

    @staticmethod
    def create(players: list[Player]) -> Panel:
        """Create a detailed panel for a player.

        Args:
            players: List of Player entries (one per discipline).

        Returns:
            A Rich Panel with player information.
        """
        if not players:
            return Panel("No player data", title="Unknown Player")

        first = players[0]

        info_lines = [
            f"[bold]Player ID:[/] {first.player_id}",
            f"[bold]Birth Year:[/] {first.birth_year}",
            f"[bold]Club:[/] {first.club}",
            f"[bold]District:[/] {first.district}",
            f"[bold]Age Class:[/] {first.age_class_2}",
        ]

        if first.ranking_week:
            info_lines.append(f"[bold]Ranking Week:[/] {first.ranking_week}")

        info_text = "\n".join(info_lines)

        rankings_table = RankingTable.create_player_rankings(players, title="")

        from rich.console import Group

        content = Group(
            Text.from_markup(info_text),
            Text(""),
            rankings_table,
        )

        return Panel(
            content,
            title=f"[bold white]{first.full_name}[/]",
            border_style="cyan",
            padding=(1, 2),
        )


class ComparisonPanel:
    """Panel formatter for player comparison."""

    @staticmethod
    def create(
        player1_entries: list[Player],
        player2_entries: list[Player],
    ) -> Panel:
        """Create a comparison panel for two players.

        Args:
            player1_entries: First player's entries across disciplines.
            player2_entries: Second player's entries across disciplines.

        Returns:
            A Rich Panel with comparison information.
        """
        if not player1_entries or not player2_entries:
            return Panel("Insufficient data for comparison", title="Comparison")

        p1 = player1_entries[0]
        p2 = player2_entries[0]

        comparison_table = RankingTable.create_comparison(
            player1_entries, player2_entries
        )

        return Panel(
            comparison_table,
            title=f"[bold]Player Comparison[/]",
            border_style="magenta",
            padding=(1, 2),
        )


class TeamPanel:
    """Panel formatter for team points calculation."""

    @staticmethod
    def create(
        player1_entries: list[Player],
        player2_entries: list[Player],
        discipline: str | None = None,
    ) -> Panel:
        """Create a team points panel.

        Args:
            player1_entries: First player's entries.
            player2_entries: Second player's entries.
            discipline: Specific discipline to show, or None for all doubles.

        Returns:
            A Rich Panel with team points information.
        """
        if not player1_entries or not player2_entries:
            return Panel("Insufficient data", title="Team Points")

        p1 = player1_entries[0]
        p2 = player2_entries[0]

        table = Table(show_header=True, header_style="bold")
        table.add_column("Discipline", min_width=15)
        table.add_column(p1.full_name, justify="right")
        table.add_column(p2.full_name, justify="right")
        table.add_column("Team Total", justify="right", style="bold green")

        doubles_disciplines = ["HD", "DD", "HM", "DM"]
        if discipline:
            doubles_disciplines = [discipline]

        for disc_code in doubles_disciplines:
            p1_entry = next(
                (p for p in player1_entries if p.discipline.value == disc_code), None
            )
            p2_entry = next(
                (p for p in player2_entries if p.discipline.value == disc_code), None
            )

            if p1_entry and p2_entry:
                total = p1_entry.points + p2_entry.points
                disc_style = get_discipline_style(disc_code)
                disc_name = p1_entry.discipline.full_name

                table.add_row(
                    f"[{disc_style}]{disc_name}[/]",
                    f"{p1_entry.points:.3f}",
                    f"{p2_entry.points:.3f}",
                    f"{total:.3f}",
                )

        return Panel(
            table,
            title=f"[bold]Team: {p1.full_name} & {p2.full_name}[/]",
            border_style="green",
            padding=(1, 2),
        )

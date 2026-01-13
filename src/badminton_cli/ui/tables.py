"""Rich table formatters for player data."""

from rich.table import Table

from ..models.player import Discipline, Player
from ..search.fuzzy import SearchResult
from .console import get_discipline_style, get_rank_style


class RankingTable:
    """Table formatter for ranking data."""

    @staticmethod
    def create_top_rankings(
        players: list[Player],
        title: str = "Top Rankings",
        show_age_rank: bool = False,
    ) -> Table:
        """Create a table of top ranked players."""
        table = Table(title=title, show_header=True, header_style="bold")

        table.add_column("#", style="dim", width=4, justify="right")
        if show_age_rank:
            table.add_column("Age#", style="dim", width=4, justify="right")
        table.add_column("Name", style="player.name", min_width=20)
        table.add_column("Club", style="player.club", min_width=15)
        table.add_column("Points", style="player.points", justify="right")
        table.add_column("Age", justify="center")
        table.add_column("Tournaments", justify="right")

        for player in players:
            rank_style = get_rank_style(player.rank)
            rank_str = f"[{rank_style}]{player.rank}[/]" if rank_style else str(player.rank)
            row = [rank_str]
            if show_age_rank:
                age_rank_str = str(player.age_group_rank) if player.age_group_rank else "-"
                row.append(age_rank_str)
            row.extend([
                player.full_name,
                player.club[:25] + "..." if len(player.club) > 25 else player.club,
                f"{player.points:.3f}",
                player.age_class_2,
                str(player.tournaments),
            ])
            table.add_row(*row)

        return table

    @staticmethod
    def create_search_results(
        results: list[tuple[SearchResult, list[Player]]],
        title: str = "Search Results",
    ) -> Table:
        """Create a table of search results."""
        table = Table(title=title, show_header=True, header_style="bold")

        table.add_column("#", style="dim", width=3, justify="right")
        table.add_column("Name", style="player.name", min_width=20)
        table.add_column("Club", style="player.club", min_width=15)
        table.add_column("ID", style="dim")
        table.add_column("Best Rank", justify="right")

        for i, (result, players) in enumerate(results, 1):
            best_player = min(players, key=lambda p: p.rank)
            table.add_row(
                str(i),
                result.full_name,
                best_player.club[:20] + "..." if len(best_player.club) > 20 else best_player.club,
                result.player_id,
                f"#{best_player.rank} ({best_player.discipline.value})",
            )

        return table

    @staticmethod
    def create_player_rankings(
        players: list[Player],
        title: str = "Player Rankings",
    ) -> Table:
        """Create a table of a single player's rankings across disciplines."""
        table = Table(title=title, show_header=True, header_style="bold")

        has_age_rank = any(p.age_group_rank is not None for p in players)

        table.add_column("Discipline", min_width=15)
        table.add_column("Rank", justify="right")
        if has_age_rank:
            table.add_column("Age Rank", justify="right")
        table.add_column("Points", justify="right", style="player.points")
        table.add_column("Tournaments", justify="right")

        for player in sorted(players, key=lambda p: p.rank):
            disc_style = get_discipline_style(player.discipline.value)
            row = [
                f"[{disc_style}]{player.discipline.full_name}[/]",
                f"#{player.rank}",
            ]
            if has_age_rank:
                age_rank_str = f"#{player.age_group_rank}" if player.age_group_rank else "-"
                row.append(age_rank_str)
            row.extend([
                f"{player.points:.3f}",
                str(player.tournaments),
            ])
            table.add_row(*row)

        return table

    @staticmethod
    def create_comparison(
        player1_entries: list[Player],
        player2_entries: list[Player],
    ) -> Table:
        """Create a comparison table for two players."""
        if not player1_entries or not player2_entries:
            return Table(title="Comparison (No Data)")

        p1 = player1_entries[0]
        p2 = player2_entries[0]

        table = Table(
            title=f"[bold]{p1.full_name}[/] vs [bold]{p2.full_name}[/]",
            show_header=True,
            header_style="bold",
        )

        table.add_column("", style="dim")
        table.add_column(p1.full_name, justify="center")
        table.add_column(p2.full_name, justify="center")
        table.add_column("Team Sum", justify="center", style="bold")

        table.add_row("Club", p1.club[:20], p2.club[:20], "-")
        table.add_row("Birth Year", str(p1.birth_year), str(p2.birth_year), "-")
        table.add_row("Age Class", p1.age_class_2, p2.age_class_2, "-")

        table.add_section()

        all_disciplines = set(p.discipline for p in player1_entries + player2_entries)

        for disc in sorted(all_disciplines, key=lambda d: d.value):
            p1_entry = next((p for p in player1_entries if p.discipline == disc), None)
            p2_entry = next((p for p in player2_entries if p.discipline == disc), None)

            p1_points = f"{p1_entry.points:.3f}" if p1_entry else "-"
            p2_points = f"{p2_entry.points:.3f}" if p2_entry else "-"

            team_sum: str
            if disc.is_doubles() and p1_entry and p2_entry:
                total = p1_entry.points + p2_entry.points
                team_sum = f"[bold green]{total:.3f}[/]"
            else:
                team_sum = "-"

            disc_style = get_discipline_style(disc.value)
            table.add_row(
                f"[{disc_style}]{disc.value}[/]",
                p1_points,
                p2_points,
                team_sum,
            )

        return table

    @staticmethod
    def create_history_list(
        weeks: list[tuple[int, int]],
        title: str = "Available Ranking Weeks",
    ) -> Table:
        """Create a table of available ranking weeks."""
        table = Table(title=title, show_header=True, header_style="bold")

        table.add_column("Year", justify="center")
        table.add_column("Week", justify="center")
        table.add_column("Label", style="dim")

        for year, week in weeks:
            table.add_row(str(year), f"KW {week}", f"KW {week} {year}")

        return table

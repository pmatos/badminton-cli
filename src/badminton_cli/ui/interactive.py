"""Interactive TUI mode for player search."""

from rich.live import Live
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from ..data.database import Database
from ..models.player import RankingWeek
from ..search.fuzzy import FuzzySearch
from .console import console
from .panels import ComparisonPanel, PlayerPanel, TeamPanel
from .tables import RankingTable


class InteractiveMode:
    """Interactive TUI for player search and exploration."""

    def __init__(self, db: Database):
        self.db = db
        self.search = FuzzySearch(db)
        self.search.build_index()

    def run(self) -> None:
        """Run the interactive mode."""
        console.print(
            Panel(
                "[bold]Badminton CLI - Interactive Mode[/]\n\n"
                "Commands:\n"
                "  [cyan]<name>[/]     - Search for a player\n"
                "  [cyan]compare[/]   - Compare two players\n"
                "  [cyan]team[/]      - Calculate team points\n"
                "  [cyan]top[/]       - Show top rankings\n"
                "  [cyan]quit[/]      - Exit\n",
                title="Welcome",
                border_style="cyan",
            )
        )

        while True:
            try:
                command = Prompt.ask("\n[bold cyan]badminton[/]")
                command = command.strip().lower()

                if command in ("quit", "exit", "q"):
                    console.print("[dim]Goodbye![/]")
                    break
                elif command == "compare":
                    self._compare_mode()
                elif command == "team":
                    self._team_mode()
                elif command == "top":
                    self._top_mode()
                elif command:
                    self._search_mode(command)
            except KeyboardInterrupt:
                console.print("\n[dim]Goodbye![/]")
                break
            except EOFError:
                break

    def _search_mode(self, query: str) -> None:
        """Search for players."""
        results = self.search.search_with_details(query, limit=10)

        if not results:
            console.print("[warning]No players found.[/]")
            return

        table = RankingTable.create_search_results(results)
        console.print(table)

        if len(results) == 1:
            _, players = results[0]
            console.print()
            console.print(PlayerPanel.create(players))
        else:
            choice = Prompt.ask(
                "Enter number to view details (or press Enter to skip)",
                default="",
            )
            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(results):
                    _, players = results[idx]
                    console.print()
                    console.print(PlayerPanel.create(players))

    def _compare_mode(self) -> None:
        """Compare two players."""
        console.print("[info]Enter two player names to compare.[/]")

        name1 = Prompt.ask("First player")
        results1 = self.search.search_with_details(name1, limit=5)
        if not results1:
            console.print("[warning]First player not found.[/]")
            return

        player1_entries = self._select_player(results1, "first")
        if not player1_entries:
            return

        name2 = Prompt.ask("Second player")
        results2 = self.search.search_with_details(name2, limit=5)
        if not results2:
            console.print("[warning]Second player not found.[/]")
            return

        player2_entries = self._select_player(results2, "second")
        if not player2_entries:
            return

        console.print()
        console.print(ComparisonPanel.create(player1_entries, player2_entries))

    def _team_mode(self) -> None:
        """Calculate team points for two players."""
        console.print("[info]Enter two player names for team calculation.[/]")

        name1 = Prompt.ask("First player")
        results1 = self.search.search_with_details(name1, limit=5)
        if not results1:
            console.print("[warning]First player not found.[/]")
            return

        player1_entries = self._select_player(results1, "first")
        if not player1_entries:
            return

        name2 = Prompt.ask("Second player")
        results2 = self.search.search_with_details(name2, limit=5)
        if not results2:
            console.print("[warning]Second player not found.[/]")
            return

        player2_entries = self._select_player(results2, "second")
        if not player2_entries:
            return

        console.print()
        console.print(TeamPanel.create(player1_entries, player2_entries))

    def _top_mode(self) -> None:
        """Show top rankings."""
        from ..models.player import Discipline

        disc_choice = Prompt.ask(
            "Discipline",
            choices=["HE", "HD", "DE", "DD", "HM", "DM", "all"],
            default="HE",
        )

        discipline = None if disc_choice == "all" else Discipline(disc_choice)
        players = self.db.get_players(discipline=discipline, limit=20)

        if not players:
            console.print("[warning]No rankings available.[/]")
            return

        title = f"Top 20 - {discipline.full_name}" if discipline else "Top 20 - All"
        table = RankingTable.create_top_rankings(players, title=title)
        console.print(table)

    def _select_player(
        self,
        results: list,
        ordinal: str,
    ) -> list | None:
        """Helper to select a player from search results."""
        if len(results) == 1:
            return results[0][1]

        table = RankingTable.create_search_results(results, title=f"Select {ordinal} player")
        console.print(table)

        choice = Prompt.ask(f"Select {ordinal} player number", default="1")
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(results):
                return results[idx][1]

        console.print("[warning]Invalid selection.[/]")
        return None

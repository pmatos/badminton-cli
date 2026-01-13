"""Command-line interface for badminton-cli."""

import click
from rich.progress import Progress, SpinnerColumn, TextColumn

from .data.database import Database
from .data.downloader import Downloader
from .data.parser import parse_excel
from .models.player import Discipline, RankingWeek
from .search.fuzzy import FuzzySearch
from .ui.console import console
from .ui.interactive import InteractiveMode
from .ui.panels import ComparisonPanel, PlayerPanel, TeamPanel
from .ui.tables import RankingTable


def ensure_data(db: Database, downloader: Downloader) -> bool:
    """Ensure we have data to work with.

    Returns True if data is available, False otherwise.
    """
    if db.get_current_week() is not None:
        return True

    console.print("[info]No local data found. Downloading current rankings...[/]")

    try:
        week = downloader.get_current_week()
        if week is None:
            console.print("[error]Could not fetch ranking data.[/]")
            return False

        path = downloader.download_week(week)
        players = parse_excel(path, week)
        db.index_week(week, players)
        console.print(f"[success]Downloaded and indexed {week.label}[/]")
        return True
    except Exception as e:
        console.print(f"[error]Failed to download data: {e}[/]")
        return False


@click.group(invoke_without_command=True)
@click.pass_context
def main(ctx: click.Context) -> None:
    """Badminton CLI - German U19 Rankings Explorer.

    Run without arguments to start interactive mode.
    """
    ctx.ensure_object(dict)
    ctx.obj["db"] = Database()
    ctx.obj["downloader"] = Downloader()

    if ctx.invoked_subcommand is None:
        if not ensure_data(ctx.obj["db"], ctx.obj["downloader"]):
            return
        interactive = InteractiveMode(ctx.obj["db"])
        interactive.run()


@main.command()
@click.option("--all", "download_all", is_flag=True, help="Download all historical data")
@click.option("--force", is_flag=True, help="Force re-download of all files")
@click.pass_context
def update(ctx: click.Context, download_all: bool, force: bool) -> None:
    """Download and update ranking data."""
    downloader: Downloader = ctx.obj["downloader"]
    db: Database = ctx.obj["db"]

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        if download_all:
            task = progress.add_task("Fetching available weeks...", total=None)
            weeks = downloader.get_available_weeks()
            progress.update(task, description=f"Found {len(weeks)} ranking weeks")

            for i, week in enumerate(weeks):
                progress.update(
                    task,
                    description=f"Downloading {week.label} ({i + 1}/{len(weeks)})",
                )

                should_download = force or not downloader.is_downloaded(week)
                if week.is_current:
                    should_download = True

                if should_download:
                    try:
                        path = downloader.download_week(week, force=force or week.is_current)
                        players = parse_excel(path, week)
                        db.index_week(week, players)
                    except Exception as e:
                        console.print(f"[warning]Failed to download {week.label}: {e}[/]")

            progress.update(task, description="[success]Update complete![/]")
        else:
            task = progress.add_task("Updating current week...", total=None)
            week = downloader.get_current_week()
            if week:
                path = downloader.download_week(week, force=True)
                players = parse_excel(path, week)
                db.index_week(week, players)
                progress.update(task, description=f"[success]Updated {week.label}[/]")
            else:
                progress.update(task, description="[error]Could not fetch current week[/]")


@main.command()
@click.argument("name")
@click.option("--limit", "-n", default=10, help="Maximum results to show")
@click.pass_context
def search(ctx: click.Context, name: str, limit: int) -> None:
    """Search for players by name."""
    db: Database = ctx.obj["db"]

    if not ensure_data(db, ctx.obj["downloader"]):
        return

    fuzzy = FuzzySearch(db)
    fuzzy.build_index()

    results = fuzzy.search_with_details(name, limit=limit)

    if not results:
        console.print("[warning]No players found.[/]")
        return

    table = RankingTable.create_search_results(results)
    console.print(table)


@main.command()
@click.argument("player_id")
@click.option("--week", "-w", help="Ranking week (e.g., 'KW2' or '2026-KW02')")
@click.pass_context
def player(ctx: click.Context, player_id: str, week: str | None) -> None:
    """Show detailed information for a player by ID."""
    db: Database = ctx.obj["db"]

    if not ensure_data(db, ctx.obj["downloader"]):
        return

    ranking_week = parse_week_arg(week) if week else None
    players = db.get_player_by_id(player_id, ranking_week)

    if not players:
        console.print(f"[warning]Player '{player_id}' not found.[/]")
        return

    console.print(PlayerPanel.create(players))


@main.command()
@click.argument("id1")
@click.argument("id2")
@click.option("--week", "-w", help="Ranking week")
@click.pass_context
def compare(ctx: click.Context, id1: str, id2: str, week: str | None) -> None:
    """Compare two players side by side."""
    db: Database = ctx.obj["db"]

    if not ensure_data(db, ctx.obj["downloader"]):
        return

    ranking_week = parse_week_arg(week) if week else None

    player1 = db.get_player_by_id(id1, ranking_week)
    player2 = db.get_player_by_id(id2, ranking_week)

    if not player1:
        console.print(f"[warning]Player '{id1}' not found.[/]")
        return
    if not player2:
        console.print(f"[warning]Player '{id2}' not found.[/]")
        return

    console.print(ComparisonPanel.create(player1, player2))


@main.command()
@click.argument("id1")
@click.argument("id2")
@click.option("--discipline", "-d", type=click.Choice(["HD", "DD", "HM", "DM"]),
              help="Specific discipline")
@click.option("--week", "-w", help="Ranking week")
@click.pass_context
def team(ctx: click.Context, id1: str, id2: str, discipline: str | None, week: str | None) -> None:
    """Calculate combined team points for doubles."""
    db: Database = ctx.obj["db"]

    if not ensure_data(db, ctx.obj["downloader"]):
        return

    ranking_week = parse_week_arg(week) if week else None

    player1 = db.get_player_by_id(id1, ranking_week)
    player2 = db.get_player_by_id(id2, ranking_week)

    if not player1:
        console.print(f"[warning]Player '{id1}' not found.[/]")
        return
    if not player2:
        console.print(f"[warning]Player '{id2}' not found.[/]")
        return

    console.print(TeamPanel.create(player1, player2, discipline))


@main.command()
@click.option("--discipline", "-d", type=click.Choice(["HE", "HD", "DE", "DD", "HM", "DM"]),
              help="Filter by discipline")
@click.option("--limit", "-n", default=20, help="Number of results")
@click.option("--week", "-w", help="Ranking week")
@click.pass_context
def top(ctx: click.Context, discipline: str | None, limit: int, week: str | None) -> None:
    """Show top ranked players."""
    db: Database = ctx.obj["db"]

    if not ensure_data(db, ctx.obj["downloader"]):
        return

    ranking_week = parse_week_arg(week) if week else None
    disc = Discipline(discipline) if discipline else None

    players = db.get_players(week=ranking_week, discipline=disc, limit=limit)

    if not players:
        console.print("[warning]No rankings available.[/]")
        return

    title = f"Top {limit}"
    if disc:
        title += f" - {disc.full_name}"

    table = RankingTable.create_top_rankings(players, title=title)
    console.print(table)


@main.command()
@click.argument("player_ids", nargs=-1, required=True)
@click.option("--discipline", "-d", type=click.Choice(["HE", "HD", "DE", "DD", "HM", "DM"]),
              help="Discipline to show (defaults to player's best)")
@click.option("--points", "-p", is_flag=True, help="Show points instead of rank")
@click.pass_context
def graph(ctx: click.Context, player_ids: tuple[str, ...], discipline: str | None, points: bool) -> None:
    """Show rank history graph for one or more players.

    Examples:

        badminton-cli graph 01-150083

        badminton-cli graph 01-150083 06-153539 --discipline HE
    """
    from .ui.graphs import plot_multi_player_history, plot_rank_history

    db: Database = ctx.obj["db"]

    if not ensure_data(db, ctx.obj["downloader"]):
        return

    weeks = db.get_weeks()
    if len(weeks) < 2:
        console.print("[warning]Need at least 2 ranking weeks for history graph.[/]")
        console.print("[info]Run 'update --all' to download historical data.[/]")
        return

    disc = Discipline(discipline) if discipline else None

    if len(player_ids) == 1:
        player_id = player_ids[0]
        players = db.get_player_by_id(player_id)
        if not players:
            console.print(f"[warning]Player '{player_id}' not found.[/]")
            return

        history = db.get_player_history(player_id, disc)
        if not history:
            console.print(f"[warning]No history data for '{player_id}'.[/]")
            return

        actual_disc = disc
        if actual_disc is None:
            first_week = history[0][0]
            entries = db.get_player_by_id(player_id, first_week)
            if entries:
                actual_disc = entries[0].discipline

        plot_rank_history(history, players[0].full_name, actual_disc or Discipline.HE, show_points=points)
    else:
        histories: list[tuple[str, list[tuple[RankingWeek, int, float]]]] = []
        actual_disc = disc

        for player_id in player_ids:
            players = db.get_player_by_id(player_id)
            if not players:
                console.print(f"[warning]Player '{player_id}' not found, skipping.[/]")
                continue

            history = db.get_player_history(player_id, disc)
            if not history:
                console.print(f"[warning]No history for '{player_id}', skipping.[/]")
                continue

            histories.append((players[0].full_name, history))

            if actual_disc is None:
                first_week = history[0][0]
                entries = db.get_player_by_id(player_id, first_week)
                if entries:
                    actual_disc = entries[0].discipline

        if not histories:
            console.print("[warning]No valid player histories found.[/]")
            return

        plot_multi_player_history(histories, actual_disc or Discipline.HE, show_points=points)


@main.command()
@click.pass_context
def history(ctx: click.Context) -> None:
    """List available ranking weeks."""
    db: Database = ctx.obj["db"]

    weeks = db.get_weeks()

    if not weeks:
        console.print("[warning]No ranking data available. Run 'update --all' first.[/]")
        return

    table = RankingTable.create_history_list(
        [(w.year, w.week) for w in weeks]
    )
    console.print(table)


def parse_week_arg(week_str: str) -> RankingWeek | None:
    """Parse a week argument string into a RankingWeek.

    Accepts formats:
    - 'KW2' or 'kw2' (current year assumed)
    - '2026-KW02' or '2026_KW02'
    - '2' (just the week number)
    """
    import re
    from datetime import datetime

    week_str = week_str.strip().upper()

    match = re.match(r"(\d{4})[-_]?KW(\d{1,2})", week_str)
    if match:
        return RankingWeek(year=int(match.group(1)), week=int(match.group(2)))

    match = re.match(r"KW(\d{1,2})", week_str)
    if match:
        return RankingWeek(year=datetime.now().year, week=int(match.group(1)))

    if week_str.isdigit():
        return RankingWeek(year=datetime.now().year, week=int(week_str))

    return None


if __name__ == "__main__":
    main()

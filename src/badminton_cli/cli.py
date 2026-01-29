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
from .config import clear_poi, get_config_path, get_poi, set_poi
from .utils.json_output import (
    comparison_to_json,
    graph_history_to_json,
    history_weeks_to_json,
    player_details_to_json,
    print_json,
    search_results_to_json,
    team_to_json,
    top_rankings_to_json,
)


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
@click.option("--json", "json_output", is_flag=True, help="Output data as JSON")
@click.pass_context
def main(ctx: click.Context, json_output: bool) -> None:
    """Badminton CLI - German U19 Rankings Explorer.

    Run without arguments to start interactive mode.
    """
    ctx.ensure_object(dict)
    ctx.obj["db"] = Database()
    ctx.obj["downloader"] = Downloader()
    ctx.obj["json"] = json_output

    if ctx.invoked_subcommand is None:
        if json_output:
            console.print("[error]--json flag requires a subcommand.[/]")
            return
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


@main.group()
def poi() -> None:
    """Manage Player of Interest (POI) for default player ID."""


@poi.command("set")
@click.argument("player_id")
def poi_set(player_id: str) -> None:
    """Set the Player of Interest."""
    set_poi(player_id)
    console.print(f"[success]POI set to {player_id}[/]")


@poi.command("show")
def poi_show() -> None:
    """Show the current Player of Interest."""
    player_id = get_poi()
    if player_id:
        console.print(f"POI: [bold]{player_id}[/]")
        console.print(f"Config: {get_config_path()}")
    else:
        console.print("[warning]No POI configured.[/]")


@poi.command("clear")
def poi_clear() -> None:
    """Clear the Player of Interest."""
    clear_poi()
    console.print("[success]POI cleared.[/]")


main.add_command(poi)


@main.command()
@click.argument("name")
@click.option("--limit", "-n", default=10, help="Maximum results to show")
@click.pass_context
def search(ctx: click.Context, name: str, limit: int) -> None:
    """Search for players by name."""
    db: Database = ctx.obj["db"]
    json_output: bool = ctx.obj["json"]

    if not ensure_data(db, ctx.obj["downloader"]):
        return

    fuzzy = FuzzySearch(db)
    fuzzy.build_index()

    results = fuzzy.search_with_details(name, limit=limit)

    if not results:
        if json_output:
            print_json([])
        else:
            console.print("[warning]No players found.[/]")
        return

    if json_output:
        print_json(search_results_to_json(results))
    else:
        table = RankingTable.create_search_results(results)
        console.print(table)


@main.command()
@click.argument("player_id", required=False, default=None)
@click.option("--week", "-w", help="Ranking week (e.g., 'KW2' or '2026-KW02')")
@click.option("--age-rank", "-a", is_flag=True, help="Show rank within age group")
@click.pass_context
def player(ctx: click.Context, player_id: str | None, week: str | None, age_rank: bool) -> None:
    """Show detailed information for a player by ID.

    If no PLAYER_ID is given, uses the configured POI (see 'poi set').
    """
    db: Database = ctx.obj["db"]

    if player_id is None:
        player_id = get_poi()
        if player_id is None:
            console.print("[error]No player ID given and no POI configured. Use 'poi set <id>' first.[/]")
            return
    json_output: bool = ctx.obj["json"]

    if not ensure_data(db, ctx.obj["downloader"]):
        return

    ranking_week = parse_week_arg(week) if week else None
    players = db.get_player_by_id(player_id, ranking_week, include_age_rank=age_rank)

    if not players:
        if json_output:
            print_json({"error": f"Player '{player_id}' not found"})
        else:
            console.print(f"[warning]Player '{player_id}' not found.[/]")
        return

    if json_output:
        print_json(player_details_to_json(players))
    else:
        console.print(PlayerPanel.create(players))


@main.command()
@click.argument("id1")
@click.argument("id2")
@click.option("--week", "-w", help="Ranking week")
@click.pass_context
def compare(ctx: click.Context, id1: str, id2: str, week: str | None) -> None:
    """Compare two players side by side."""
    db: Database = ctx.obj["db"]
    json_output: bool = ctx.obj["json"]

    if not ensure_data(db, ctx.obj["downloader"]):
        return

    ranking_week = parse_week_arg(week) if week else None

    player1 = db.get_player_by_id(id1, ranking_week)
    player2 = db.get_player_by_id(id2, ranking_week)

    if not player1:
        if json_output:
            print_json({"error": f"Player '{id1}' not found"})
        else:
            console.print(f"[warning]Player '{id1}' not found.[/]")
        return
    if not player2:
        if json_output:
            print_json({"error": f"Player '{id2}' not found"})
        else:
            console.print(f"[warning]Player '{id2}' not found.[/]")
        return

    if json_output:
        print_json(comparison_to_json(player1, player2))
    else:
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
    json_output: bool = ctx.obj["json"]

    if not ensure_data(db, ctx.obj["downloader"]):
        return

    ranking_week = parse_week_arg(week) if week else None

    player1 = db.get_player_by_id(id1, ranking_week)
    player2 = db.get_player_by_id(id2, ranking_week)

    if not player1:
        if json_output:
            print_json({"error": f"Player '{id1}' not found"})
        else:
            console.print(f"[warning]Player '{id1}' not found.[/]")
        return
    if not player2:
        if json_output:
            print_json({"error": f"Player '{id2}' not found"})
        else:
            console.print(f"[warning]Player '{id2}' not found.[/]")
        return

    if json_output:
        print_json(team_to_json(player1, player2, discipline))
    else:
        console.print(TeamPanel.create(player1, player2, discipline))


@main.command()
@click.option("--discipline", "-d", type=click.Choice(["HE", "HD", "DE", "DD", "HM", "DM"]),
              help="Filter by discipline")
@click.option("--limit", "-n", default=20, help="Number of results")
@click.option("--week", "-w", help="Ranking week")
@click.option("--age-rank", "-a", is_flag=True, help="Show rank within age group")
@click.pass_context
def top(ctx: click.Context, discipline: str | None, limit: int, week: str | None, age_rank: bool) -> None:
    """Show top ranked players."""
    db: Database = ctx.obj["db"]
    json_output: bool = ctx.obj["json"]

    if not ensure_data(db, ctx.obj["downloader"]):
        return

    ranking_week = parse_week_arg(week) if week else None
    disc = Discipline(discipline) if discipline else None

    players = db.get_players(
        week=ranking_week, discipline=disc, limit=limit, include_age_rank=age_rank
    )

    if not players:
        if json_output:
            print_json([])
        else:
            console.print("[warning]No rankings available.[/]")
        return

    if json_output:
        print_json(top_rankings_to_json(players, show_age_rank=age_rank))
    else:
        title = f"Top {limit}"
        if disc:
            title += f" - {disc.full_name}"

        table = RankingTable.create_top_rankings(players, title=title, show_age_rank=age_rank)
        console.print(table)


def parse_since_arg(since_str: str) -> tuple[int, int] | None:
    """Parse a --since argument like '1y', '6m', '3m' into (year, week) cutoff.

    Returns the (year, week) tuple representing the oldest week to include.
    """
    import re
    from datetime import datetime, timedelta

    since_str = since_str.strip().lower()

    match = re.match(r"(\d+)([ym])", since_str)
    if not match:
        return None

    value = int(match.group(1))
    unit = match.group(2)

    now = datetime.now()
    if unit == "y":
        cutoff = now - timedelta(days=value * 365)
    else:  # 'm' for months
        cutoff = now - timedelta(days=value * 30)

    return (cutoff.year, cutoff.isocalendar()[1])


def filter_history_since(
    history: list[tuple[RankingWeek, int, float]],
    since: tuple[int, int],
) -> list[tuple[RankingWeek, int, float]]:
    """Filter history to only include weeks after the given cutoff."""
    return [
        (week, rank, points)
        for week, rank, points in history
        if (week.year, week.week) >= since
    ]


@main.command()
@click.argument("player_ids", nargs=-1)
@click.option("--discipline", "-d", type=click.Choice(["HE", "HD", "DE", "DD", "HM", "DM"]),
              help="Discipline to show (defaults to player's best)")
@click.option("--points", "-p", is_flag=True, help="Show points instead of rank")
@click.option("--since", "-s", help="Show history since duration (e.g., '1y', '6m', '3m')")
@click.option("--age-rank", "-a", is_flag=True, help="Show rank within age group instead of overall")
@click.pass_context
def graph(
    ctx: click.Context,
    player_ids: tuple[str, ...],
    discipline: str | None,
    points: bool,
    since: str | None,
    age_rank: bool,
) -> None:
    """Show rank history graph for one or more players.

    If no PLAYER_IDS are given, uses the configured POI (see 'poi set').

    Examples:

        badminton-cli graph 01-150083

        badminton-cli graph 01-150083 06-153539 --discipline HE

        badminton-cli graph 01-150083 --since 6m --age-rank
    """
    from rich.progress import Progress, SpinnerColumn, TextColumn

    from .ui.graphs import plot_multi_player_history, plot_rank_history

    db: Database = ctx.obj["db"]
    json_output: bool = ctx.obj["json"]

    if not player_ids:
        poi_id = get_poi()
        if poi_id is None:
            console.print("[error]No player IDs given and no POI configured. Use 'poi set <id>' first.[/]")
            return
        player_ids = (poi_id,)

    if not ensure_data(db, ctx.obj["downloader"]):
        return

    weeks = db.get_weeks()
    if len(weeks) < 2:
        if json_output:
            print_json({"error": "Need at least 2 ranking weeks for history graph"})
        else:
            console.print("[warning]Need at least 2 ranking weeks for history graph.[/]")
            console.print("[info]Run 'update --all' to download historical data.[/]")
        return

    since_cutoff = None
    if since:
        since_cutoff = parse_since_arg(since)
        if since_cutoff is None:
            if json_output:
                print_json({"error": f"Invalid --since format: '{since}'"})
            else:
                console.print(f"[warning]Invalid --since format: '{since}'. Use e.g., '1y', '6m', '3m'.[/]")
            return

    disc = Discipline(discipline) if discipline else None
    y_label = "Age Rank" if age_rank else None

    if len(player_ids) == 1:
        player_id = player_ids[0]
        players = db.get_player_by_id(player_id)
        if not players:
            if json_output:
                print_json({"error": f"Player '{player_id}' not found"})
            else:
                console.print(f"[warning]Player '{player_id}' not found.[/]")
            return

        history = db.get_player_history(player_id, disc)
        if not history:
            if json_output:
                print_json({"error": f"No history data for '{player_id}'"})
            else:
                console.print(f"[warning]No history data for '{player_id}'.[/]")
            return

        if since_cutoff:
            history = filter_history_since(history, since_cutoff)
            if not history:
                if json_output:
                    print_json({"error": "No history data within the specified time range"})
                else:
                    console.print("[warning]No history data within the specified time range.[/]")
                return

        actual_disc = disc
        if actual_disc is None:
            first_week = history[0][0]
            entries = db.get_player_by_id(player_id, first_week)
            if entries:
                actual_disc = entries[0].discipline

        if age_rank and not points:
            if not json_output:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console,
                ) as progress:
                    task = progress.add_task(
                        f"Computing age-group ranks for {len(history)} weeks...", total=len(history)
                    )
                    age_class = players[0].age_class_2
                    new_history = []
                    for week, _, pts in history:
                        age_grp_rank = db.get_age_group_rank(
                            player_id, actual_disc or Discipline.HE, age_class, week
                        )
                        new_history.append((week, age_grp_rank, pts))
                        progress.advance(task)
                    history = new_history
            else:
                age_class = players[0].age_class_2
                new_history = []
                for week, _, pts in history:
                    age_grp_rank = db.get_age_group_rank(
                        player_id, actual_disc or Discipline.HE, age_class, week
                    )
                    new_history.append((week, age_grp_rank, pts))
                history = new_history

        if json_output:
            histories = [(players[0].full_name, history)]
            print_json(graph_history_to_json(
                histories, actual_disc or Discipline.HE,
                show_points=points, show_age_rank=age_rank
            ))
        else:
            plot_rank_history(
                history, players[0].full_name, actual_disc or Discipline.HE,
                show_points=points, y_label_override=y_label
            )
    else:
        histories: list[tuple[str, list[tuple[RankingWeek, int, float]]]] = []
        actual_disc = disc

        for player_id in player_ids:
            players = db.get_player_by_id(player_id)
            if not players:
                if not json_output:
                    console.print(f"[warning]Player '{player_id}' not found, skipping.[/]")
                continue

            history = db.get_player_history(player_id, disc)
            if not history:
                if not json_output:
                    console.print(f"[warning]No history for '{player_id}', skipping.[/]")
                continue

            if since_cutoff:
                history = filter_history_since(history, since_cutoff)
                if not history:
                    if not json_output:
                        console.print(f"[warning]No history for '{player_id}' in time range, skipping.[/]")
                    continue

            if actual_disc is None:
                first_week = history[0][0]
                entries = db.get_player_by_id(player_id, first_week)
                if entries:
                    actual_disc = entries[0].discipline

            if age_rank and not points:
                age_class = players[0].age_class_2
                new_history = []
                for week, _, pts in history:
                    age_grp_rank = db.get_age_group_rank(
                        player_id, actual_disc or Discipline.HE, age_class, week
                    )
                    new_history.append((week, age_grp_rank, pts))
                history = new_history

            histories.append((players[0].full_name, history))

        if not histories:
            if json_output:
                print_json({"error": "No valid player histories found"})
            else:
                console.print("[warning]No valid player histories found.[/]")
            return

        if json_output:
            print_json(graph_history_to_json(
                histories, actual_disc or Discipline.HE,
                show_points=points, show_age_rank=age_rank
            ))
        else:
            plot_multi_player_history(
                histories, actual_disc or Discipline.HE,
                show_points=points, y_label_override=y_label
            )


@main.command()
@click.pass_context
def history(ctx: click.Context) -> None:
    """List available ranking weeks."""
    db: Database = ctx.obj["db"]
    json_output: bool = ctx.obj["json"]

    weeks = db.get_weeks()

    if not weeks:
        if json_output:
            print_json([])
        else:
            console.print("[warning]No ranking data available. Run 'update --all' first.[/]")
        return

    week_tuples = [(w.year, w.week) for w in weeks]

    if json_output:
        print_json(history_weeks_to_json(week_tuples))
    else:
        table = RankingTable.create_history_list(week_tuples)
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

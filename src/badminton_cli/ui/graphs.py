"""Terminal graph visualization for rank history."""

import plotext as plt

from ..models.player import Discipline, RankingWeek


def plot_rank_history(
    history: list[tuple[RankingWeek, int, float]],
    player_name: str,
    discipline: Discipline,
    show_points: bool = False,
) -> None:
    """Plot a player's rank history as a terminal graph.

    Args:
        history: List of (RankingWeek, rank, points) tuples.
        player_name: Name of the player for the title.
        discipline: The discipline being plotted.
        show_points: If True, plot points instead of rank.
    """
    if not history:
        return

    x_labels = [f"KW{w.week}" for w, _, _ in history]
    x_values = list(range(len(history)))

    if show_points:
        y_values = [points for _, _, points in history]
        y_label = "Points"
    else:
        y_values = [rank for _, rank, _ in history]
        y_label = "Rank"

    plt.clear_figure()
    plt.plot(x_values, y_values, marker="braille")
    plt.scatter(x_values, y_values)

    plt.title(f"{player_name} - {discipline.full_name}")
    plt.xlabel("Week")
    plt.ylabel(y_label)

    if not show_points:
        plt.yreverse()

    plt.xticks(x_values, x_labels)
    plt.show()


def plot_multi_player_history(
    histories: list[tuple[str, list[tuple[RankingWeek, int, float]]]],
    discipline: Discipline,
    show_points: bool = False,
) -> None:
    """Plot multiple players' rank histories on the same graph.

    Args:
        histories: List of (player_name, history) tuples.
        discipline: The discipline being plotted.
        show_points: If True, plot points instead of rank.
    """
    if not histories:
        return

    all_weeks: set[tuple[int, int]] = set()
    for _, history in histories:
        for week, _, _ in history:
            all_weeks.add((week.year, week.week))

    sorted_weeks = sorted(all_weeks)
    week_to_x = {w: i for i, w in enumerate(sorted_weeks)}

    plt.clear_figure()

    for player_name, history in histories:
        x_values = [week_to_x[(w.year, w.week)] for w, _, _ in history]
        if show_points:
            y_values = [points for _, _, points in history]
        else:
            y_values = [rank for _, rank, _ in history]

        plt.plot(x_values, y_values, label=player_name, marker="braille")
        plt.scatter(x_values, y_values)

    x_labels = [f"KW{w}" for _, w in sorted_weeks]
    x_positions = list(range(len(sorted_weeks)))

    plt.title(f"Rank Comparison - {discipline.full_name}")
    plt.xlabel("Week")
    plt.ylabel("Points" if show_points else "Rank")

    if not show_points:
        plt.yreverse()

    plt.xticks(x_positions, x_labels)
    plt.show()

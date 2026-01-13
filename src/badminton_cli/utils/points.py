"""Team points calculation utilities."""

from ..models.player import Discipline, Player


def calculate_team_points(
    player1_entries: list[Player],
    player2_entries: list[Player],
    discipline: Discipline | None = None,
) -> dict[Discipline, float]:
    """Calculate combined team points for doubles disciplines.

    Args:
        player1_entries: First player's ranking entries.
        player2_entries: Second player's ranking entries.
        discipline: Specific discipline to calculate, or None for all doubles.

    Returns:
        Dictionary mapping discipline to combined points.
    """
    doubles_disciplines = [Discipline.HD, Discipline.DD, Discipline.HM, Discipline.DM]

    if discipline:
        if not discipline.is_doubles():
            return {}
        doubles_disciplines = [discipline]

    results: dict[Discipline, float] = {}

    for disc in doubles_disciplines:
        p1_entry = next(
            (p for p in player1_entries if p.discipline == disc), None
        )
        p2_entry = next(
            (p for p in player2_entries if p.discipline == disc), None
        )

        if p1_entry and p2_entry:
            results[disc] = p1_entry.points + p2_entry.points

    return results


def get_best_team_discipline(
    player1_entries: list[Player],
    player2_entries: list[Player],
) -> tuple[Discipline, float] | None:
    """Find the discipline where the team has the highest combined points.

    Args:
        player1_entries: First player's ranking entries.
        player2_entries: Second player's ranking entries.

    Returns:
        Tuple of (discipline, combined_points) or None if no common disciplines.
    """
    team_points = calculate_team_points(player1_entries, player2_entries)

    if not team_points:
        return None

    best_disc = max(team_points, key=team_points.get)  # type: ignore
    return (best_disc, team_points[best_disc])

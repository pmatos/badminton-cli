"""JSON output utilities for CLI commands."""

import json
from dataclasses import asdict
from typing import Any

from ..models.player import Discipline, Player, RankingWeek


def player_to_dict(player: Player) -> dict[str, Any]:
    """Convert a Player dataclass to a JSON-serializable dict."""
    d = asdict(player)
    d["discipline"] = player.discipline.value
    d["full_name"] = player.full_name
    d["display_name"] = player.display_name
    return d


def ranking_week_to_dict(week: RankingWeek) -> dict[str, Any]:
    """Convert a RankingWeek dataclass to a JSON-serializable dict."""
    return {
        "year": week.year,
        "week": week.week,
        "label": week.label,
        "is_current": week.is_current,
    }


def print_json(data: Any) -> None:
    """Print data as formatted JSON to stdout."""
    print(json.dumps(data, indent=2, ensure_ascii=False))


def search_results_to_json(results: Any) -> list[dict[str, Any]]:
    """Convert search results to JSON format.

    Results is list[tuple[SearchResult, list[Player]]] from FuzzySearch.
    """
    output = []
    for search_result, players in results:
        best_player = min(players, key=lambda p: p.rank) if players else None
        entry = {
            "player_id": search_result.player_id,
            "name": search_result.full_name,
            "score": round(search_result.score, 2),
            "club": best_player.club if best_player else "",
            "best_rank": best_player.rank if best_player else None,
            "best_discipline": best_player.discipline.value if best_player else None,
        }
        output.append(entry)
    return output


def player_details_to_json(players: list[Player]) -> dict[str, Any]:
    """Convert player details (multiple disciplines) to JSON format."""
    if not players:
        return {}

    first = players[0]
    output = {
        "player_id": first.player_id,
        "first_name": first.first_name,
        "last_name": first.last_name,
        "full_name": first.full_name,
        "birth_year": first.birth_year,
        "club": first.club,
        "district": first.district,
        "age_class_1": first.age_class_1,
        "age_class_2": first.age_class_2,
        "ranking_week": first.ranking_week,
        "rankings": [],
    }

    for p in players:
        ranking = {
            "discipline": p.discipline.value,
            "rank": p.rank,
            "federation_rank": p.federation_rank,
            "points": p.points,
            "tournaments": p.tournaments,
        }
        if p.age_group_rank is not None:
            ranking["age_group_rank"] = p.age_group_rank
        output["rankings"].append(ranking)

    return output


def comparison_to_json(
    player1: list[Player], player2: list[Player]
) -> dict[str, Any]:
    """Convert player comparison to JSON format."""
    return {
        "player1": player_details_to_json(player1),
        "player2": player_details_to_json(player2),
    }


def team_to_json(
    player1: list[Player],
    player2: list[Player],
    discipline_filter: str | None = None,
) -> dict[str, Any]:
    """Convert team calculation to JSON format."""
    from ..utils.points import calculate_team_points

    p1_dict = player_details_to_json(player1)
    p2_dict = player_details_to_json(player2)

    disc_obj = Discipline(discipline_filter) if discipline_filter else None
    team_points = calculate_team_points(player1, player2, disc_obj)

    p1_by_disc = {p.discipline: p for p in player1}
    p2_by_disc = {p.discipline: p for p in player2}

    team_data = []
    for disc, total in team_points.items():
        p1 = p1_by_disc.get(disc)
        p2 = p2_by_disc.get(disc)

        team_data.append({
            "discipline": disc.value,
            "player1_points": p1.points if p1 else 0.0,
            "player2_points": p2.points if p2 else 0.0,
            "team_total": total,
        })

    return {
        "player1": {
            "player_id": p1_dict.get("player_id"),
            "full_name": p1_dict.get("full_name"),
        },
        "player2": {
            "player_id": p2_dict.get("player_id"),
            "full_name": p2_dict.get("full_name"),
        },
        "team": team_data,
    }


def top_rankings_to_json(
    players: list[Player], show_age_rank: bool = False
) -> list[dict[str, Any]]:
    """Convert top rankings to JSON format."""
    output = []
    for p in players:
        entry = {
            "rank": p.rank,
            "player_id": p.player_id,
            "name": p.full_name,
            "club": p.club,
            "points": p.points,
            "birth_year": p.birth_year,
            "tournaments": p.tournaments,
            "discipline": p.discipline.value,
        }
        if show_age_rank and p.age_group_rank is not None:
            entry["age_group_rank"] = p.age_group_rank
        output.append(entry)
    return output


def graph_history_to_json(
    histories: list[tuple[str, list[tuple[RankingWeek, int, float]]]],
    discipline: Discipline,
    show_points: bool = False,
    show_age_rank: bool = False,
) -> dict[str, Any]:
    """Convert graph history data to JSON format."""
    y_type = "points" if show_points else ("age_rank" if show_age_rank else "rank")

    players_data = []
    for name, history in histories:
        data_points = []
        for week, rank, points in history:
            point = {
                "week": week.week,
                "year": week.year,
                "label": week.label,
                "rank": rank,
                "points": points,
            }
            data_points.append(point)

        players_data.append({
            "name": name,
            "data": data_points,
        })

    return {
        "discipline": discipline.value,
        "y_axis": y_type,
        "players": players_data,
    }


def history_weeks_to_json(weeks: list[tuple[int, int]]) -> list[dict[str, Any]]:
    """Convert history weeks list to JSON format."""
    return [{"year": year, "week": week} for year, week in weeks]

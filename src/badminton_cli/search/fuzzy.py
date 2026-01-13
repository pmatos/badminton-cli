"""Fuzzy search for players using rapidfuzz."""

from dataclasses import dataclass

from rapidfuzz import fuzz, process

from ..data.database import Database
from ..models.player import Player, RankingWeek


@dataclass
class SearchResult:
    """A fuzzy search result with score."""

    player_id: str
    first_name: str
    last_name: str
    score: float

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"


class FuzzySearch:
    """Fuzzy search for players."""

    def __init__(self, db: Database):
        self.db = db
        self._index: list[tuple[str, str, str]] = []
        self._choices: list[str] = []

    def build_index(self, week: RankingWeek | None = None) -> None:
        """Build the search index from database.

        Args:
            week: The ranking week to index. If None, uses current week.
        """
        self._index = self.db.get_unique_players(week)
        self._choices = [
            f"{first} {last}" for _, first, last in self._index
        ]

    def search(
        self,
        query: str,
        limit: int = 10,
        score_cutoff: float = 50.0,
    ) -> list[SearchResult]:
        """Search for players by name.

        Args:
            query: The search query (name or partial name).
            limit: Maximum number of results.
            score_cutoff: Minimum score (0-100) to include in results.

        Returns:
            List of SearchResult objects sorted by score.
        """
        if not self._choices:
            return []

        results = process.extract(
            query,
            self._choices,
            scorer=fuzz.WRatio,
            limit=limit,
            score_cutoff=score_cutoff,
        )

        search_results: list[SearchResult] = []
        for match_str, score, idx in results:
            player_id, first_name, last_name = self._index[idx]
            search_results.append(
                SearchResult(
                    player_id=player_id,
                    first_name=first_name,
                    last_name=last_name,
                    score=score,
                )
            )

        return search_results

    def search_with_details(
        self,
        query: str,
        week: RankingWeek | None = None,
        limit: int = 10,
        score_cutoff: float = 50.0,
    ) -> list[tuple[SearchResult, list[Player]]]:
        """Search for players and return full details.

        Args:
            query: The search query.
            week: The ranking week. If None, uses current week.
            limit: Maximum number of results.
            score_cutoff: Minimum score to include.

        Returns:
            List of (SearchResult, list[Player]) tuples.
        """
        results = self.search(query, limit=limit, score_cutoff=score_cutoff)

        detailed: list[tuple[SearchResult, list[Player]]] = []
        for result in results:
            players = self.db.get_player_by_id(result.player_id, week)
            if players:
                detailed.append((result, players))

        return detailed

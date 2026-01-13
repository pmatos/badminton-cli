"""SQLite database for indexed player queries."""

import sqlite3
from pathlib import Path

from platformdirs import user_data_dir

from ..models.player import Discipline, Player, RankingWeek

SCHEMA = """
CREATE TABLE IF NOT EXISTS ranking_weeks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    year INTEGER NOT NULL,
    week INTEGER NOT NULL,
    filename TEXT NOT NULL,
    UNIQUE(year, week)
);

CREATE TABLE IF NOT EXISTS players (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ranking_week_id INTEGER NOT NULL,
    discipline TEXT NOT NULL,
    rank INTEGER NOT NULL,
    federation_rank INTEGER NOT NULL,
    last_name TEXT NOT NULL,
    first_name TEXT NOT NULL,
    gender TEXT NOT NULL,
    player_id TEXT NOT NULL,
    birth_year INTEGER NOT NULL,
    age_class_1 TEXT NOT NULL,
    age_class_2 TEXT NOT NULL,
    points REAL NOT NULL,
    tournaments INTEGER NOT NULL,
    club TEXT NOT NULL,
    district TEXT NOT NULL,
    FOREIGN KEY (ranking_week_id) REFERENCES ranking_weeks(id)
);

CREATE INDEX IF NOT EXISTS idx_players_player_id ON players(player_id);
CREATE INDEX IF NOT EXISTS idx_players_name ON players(last_name, first_name);
CREATE INDEX IF NOT EXISTS idx_players_discipline ON players(discipline);
CREATE INDEX IF NOT EXISTS idx_players_rank ON players(rank);
CREATE INDEX IF NOT EXISTS idx_players_ranking_week ON players(ranking_week_id);
"""


class Database:
    """SQLite database for player queries."""

    def __init__(self, db_path: Path | None = None):
        if db_path is None:
            data_dir = Path(user_data_dir("badminton-cli"))
            data_dir.mkdir(parents=True, exist_ok=True)
            db_path = data_dir / "rankings.db"
        self.db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript(SCHEMA)

    def _get_connection(self) -> sqlite3.Connection:
        """Get a database connection with row factory."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def has_week(self, week: RankingWeek) -> bool:
        """Check if a ranking week is already indexed."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT 1 FROM ranking_weeks WHERE year = ? AND week = ?",
                (week.year, week.week),
            )
            return cursor.fetchone() is not None

    def index_week(self, week: RankingWeek, players: list[Player]) -> None:
        """Index a ranking week's players into the database.

        If the week already exists, it will be replaced.
        """
        with self._get_connection() as conn:
            conn.execute(
                "DELETE FROM players WHERE ranking_week_id IN "
                "(SELECT id FROM ranking_weeks WHERE year = ? AND week = ?)",
                (week.year, week.week),
            )
            conn.execute(
                "DELETE FROM ranking_weeks WHERE year = ? AND week = ?",
                (week.year, week.week),
            )

            cursor = conn.execute(
                "INSERT INTO ranking_weeks (year, week, filename) VALUES (?, ?, ?)",
                (week.year, week.week, week.filename),
            )
            week_id = cursor.lastrowid

            for player in players:
                conn.execute(
                    """
                    INSERT INTO players (
                        ranking_week_id, discipline, rank, federation_rank,
                        last_name, first_name, gender, player_id, birth_year,
                        age_class_1, age_class_2, points, tournaments, club, district
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        week_id,
                        player.discipline.value,
                        player.rank,
                        player.federation_rank,
                        player.last_name,
                        player.first_name,
                        player.gender,
                        player.player_id,
                        player.birth_year,
                        player.age_class_1,
                        player.age_class_2,
                        player.points,
                        player.tournaments,
                        player.club,
                        player.district,
                    ),
                )
            conn.commit()

    def get_weeks(self) -> list[RankingWeek]:
        """Get all indexed ranking weeks."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT year, week FROM ranking_weeks ORDER BY year DESC, week DESC"
            )
            return [
                RankingWeek(year=row["year"], week=row["week"]) for row in cursor
            ]

    def get_current_week(self) -> RankingWeek | None:
        """Get the most recent indexed week."""
        weeks = self.get_weeks()
        return weeks[0] if weeks else None

    def _row_to_player(
        self, row: sqlite3.Row, week_label: str | None, age_group_rank: int | None = None
    ) -> Player:
        """Convert a database row to a Player object."""
        return Player(
            discipline=Discipline(row["discipline"]),
            rank=row["rank"],
            federation_rank=row["federation_rank"],
            last_name=row["last_name"],
            first_name=row["first_name"],
            gender=row["gender"],
            player_id=row["player_id"],
            birth_year=row["birth_year"],
            age_class_1=row["age_class_1"],
            age_class_2=row["age_class_2"],
            points=row["points"],
            tournaments=row["tournaments"],
            club=row["club"],
            district=row["district"],
            ranking_week=week_label,
            age_group_rank=age_group_rank,
        )

    def get_age_group_rank(
        self,
        player_id: str,
        discipline: Discipline,
        age_class: str,
        week: RankingWeek,
    ) -> int:
        """Calculate a player's rank within their age group.

        Args:
            player_id: The player's ID.
            discipline: The discipline to check.
            age_class: The age class to filter by (e.g., 'U15').
            week: The ranking week.

        Returns:
            The player's rank within their age group (1-indexed).
        """
        query = """
            SELECT COUNT(*) + 1 as age_rank
            FROM players p
            JOIN ranking_weeks rw ON p.ranking_week_id = rw.id
            WHERE rw.year = ? AND rw.week = ?
            AND p.discipline = ?
            AND p.age_class_2 = ?
            AND p.points > (
                SELECT points FROM players p2
                JOIN ranking_weeks rw2 ON p2.ranking_week_id = rw2.id
                WHERE rw2.year = ? AND rw2.week = ?
                AND p2.player_id = ? AND p2.discipline = ?
            )
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                query,
                (
                    week.year,
                    week.week,
                    discipline.value,
                    age_class,
                    week.year,
                    week.week,
                    player_id,
                    discipline.value,
                ),
            )
            row = cursor.fetchone()
            return row[0] if row else 1

    def get_players(
        self,
        week: RankingWeek | None = None,
        discipline: Discipline | None = None,
        limit: int | None = None,
        include_age_rank: bool = False,
    ) -> list[Player]:
        """Get players with optional filters.

        Args:
            week: Filter by ranking week. If None, uses current week.
            discipline: Filter by discipline.
            limit: Maximum number of results.
            include_age_rank: Whether to include age-group rank for each player.

        Returns:
            List of matching Player objects.
        """
        if week is None:
            week = self.get_current_week()
        if week is None:
            return []

        week_label = week.label

        query = """
            SELECT p.* FROM players p
            JOIN ranking_weeks rw ON p.ranking_week_id = rw.id
            WHERE rw.year = ? AND rw.week = ?
        """
        params: list[int | str] = [week.year, week.week]

        if discipline:
            query += " AND p.discipline = ?"
            params.append(discipline.value)

        query += " ORDER BY p.rank"

        if limit:
            query += f" LIMIT {limit}"

        with self._get_connection() as conn:
            cursor = conn.execute(query, params)
            players = []
            for row in cursor:
                age_rank = None
                if include_age_rank:
                    age_rank = self.get_age_group_rank(
                        row["player_id"],
                        Discipline(row["discipline"]),
                        row["age_class_2"],
                        week,
                    )
                players.append(self._row_to_player(row, week_label, age_rank))
            return players

    def get_player_by_id(
        self,
        player_id: str,
        week: RankingWeek | None = None,
        include_age_rank: bool = False,
    ) -> list[Player]:
        """Get all entries for a player by their ID.

        Args:
            player_id: The player's ID (e.g., '01-150083').
            week: Filter by ranking week. If None, uses current week.
            include_age_rank: Whether to include age-group rank for each entry.

        Returns:
            List of Player objects (one per discipline the player is ranked in).
        """
        if week is None:
            week = self.get_current_week()
        if week is None:
            return []

        week_label = week.label

        query = """
            SELECT p.* FROM players p
            JOIN ranking_weeks rw ON p.ranking_week_id = rw.id
            WHERE rw.year = ? AND rw.week = ? AND p.player_id = ?
            ORDER BY p.discipline
        """

        with self._get_connection() as conn:
            cursor = conn.execute(query, (week.year, week.week, player_id))
            players = []
            for row in cursor:
                age_rank = None
                if include_age_rank:
                    age_rank = self.get_age_group_rank(
                        player_id,
                        Discipline(row["discipline"]),
                        row["age_class_2"],
                        week,
                    )
                players.append(self._row_to_player(row, week_label, age_rank))
            return players

    def search_players(
        self,
        query_text: str,
        week: RankingWeek | None = None,
        limit: int = 50,
    ) -> list[Player]:
        """Search for players by name or club (simple SQL LIKE search).

        For fuzzy search, use the FuzzySearch class instead.

        Args:
            query_text: Search text.
            week: Filter by ranking week. If None, uses current week.
            limit: Maximum number of results.

        Returns:
            List of matching Player objects.
        """
        if week is None:
            week = self.get_current_week()
        if week is None:
            return []

        week_label = week.label
        search_pattern = f"%{query_text}%"

        query = """
            SELECT DISTINCT p.* FROM players p
            JOIN ranking_weeks rw ON p.ranking_week_id = rw.id
            WHERE rw.year = ? AND rw.week = ?
            AND (
                p.first_name LIKE ? OR
                p.last_name LIKE ? OR
                p.club LIKE ? OR
                p.player_id LIKE ?
            )
            ORDER BY p.points DESC
            LIMIT ?
        """

        with self._get_connection() as conn:
            cursor = conn.execute(
                query,
                (
                    week.year,
                    week.week,
                    search_pattern,
                    search_pattern,
                    search_pattern,
                    search_pattern,
                    limit,
                ),
            )
            return [self._row_to_player(row, week_label) for row in cursor]

    def get_unique_players(
        self,
        week: RankingWeek | None = None,
    ) -> list[tuple[str, str, str]]:
        """Get unique player (id, first_name, last_name) tuples.

        Useful for fuzzy search indexing.
        """
        if week is None:
            week = self.get_current_week()
        if week is None:
            return []

        query = """
            SELECT DISTINCT p.player_id, p.first_name, p.last_name
            FROM players p
            JOIN ranking_weeks rw ON p.ranking_week_id = rw.id
            WHERE rw.year = ? AND rw.week = ?
        """

        with self._get_connection() as conn:
            cursor = conn.execute(query, (week.year, week.week))
            return [(row[0], row[1], row[2]) for row in cursor]

    def clear(self) -> None:
        """Clear all data from the database."""
        with self._get_connection() as conn:
            conn.execute("DELETE FROM players")
            conn.execute("DELETE FROM ranking_weeks")
            conn.commit()

    def get_player_history(
        self,
        player_id: str,
        discipline: Discipline | None = None,
    ) -> list[tuple[RankingWeek, int, float]]:
        """Get a player's rank history across all indexed weeks.

        Args:
            player_id: The player's ID (e.g., '01-150083').
            discipline: Filter by discipline. If None, uses the player's best discipline.

        Returns:
            List of (RankingWeek, rank, points) tuples sorted by week chronologically.
        """
        with self._get_connection() as conn:
            disc: Discipline
            if discipline is None:
                cursor = conn.execute(
                    """
                    SELECT discipline, MIN(rank) as best_rank
                    FROM players WHERE player_id = ?
                    GROUP BY discipline
                    ORDER BY best_rank
                    LIMIT 1
                    """,
                    (player_id,),
                )
                row = cursor.fetchone()
                if row is None:
                    return []
                disc = Discipline(row["discipline"])
            else:
                disc = discipline

            cursor = conn.execute(
                """
                SELECT rw.year, rw.week, p.rank, p.points
                FROM players p
                JOIN ranking_weeks rw ON p.ranking_week_id = rw.id
                WHERE p.player_id = ? AND p.discipline = ?
                ORDER BY rw.year, rw.week
                """,
                (player_id, disc.value),
            )

            return [
                (RankingWeek(year=row["year"], week=row["week"]), row["rank"], row["points"])
                for row in cursor
            ]

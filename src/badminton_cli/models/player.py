"""Player and ranking data models."""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class Discipline(Enum):
    """Badminton disciplines."""

    HE = "HE"  # Herren Einzel (Men's Singles)
    HD = "HD"  # Herren Doppel (Men's Doubles)
    DE = "DE"  # Damen Einzel (Women's Singles)
    DD = "DD"  # Damen Doppel (Women's Doubles)
    HM = "HM"  # Herren Mixed (Men's Mixed Doubles)
    DM = "DM"  # Damen Mixed (Women's Mixed Doubles)

    @property
    def full_name(self) -> str:
        """Return full German name of discipline."""
        names = {
            "HE": "Herren Einzel",
            "HD": "Herren Doppel",
            "DE": "Damen Einzel",
            "DD": "Damen Doppel",
            "HM": "Mixed (Herren)",
            "DM": "Mixed (Damen)",
        }
        return names[self.value]

    @property
    def short_name(self) -> str:
        """Return short English name."""
        names = {
            "HE": "MS",  # Men's Singles
            "HD": "MD",  # Men's Doubles
            "DE": "WS",  # Women's Singles
            "DD": "WD",  # Women's Doubles
            "HM": "XD",  # Mixed Doubles
            "DM": "XD",  # Mixed Doubles
        }
        return names[self.value]

    def is_doubles(self) -> bool:
        """Check if this is a doubles discipline."""
        return self in (Discipline.HD, Discipline.DD, Discipline.HM, Discipline.DM)


@dataclass
class Player:
    """A player's ranking entry in a specific discipline."""

    discipline: Discipline
    rank: int
    federation_rank: int
    last_name: str
    first_name: str
    gender: str
    player_id: str
    birth_year: int
    age_class_1: str
    age_class_2: str
    points: float
    tournaments: int
    club: str
    district: str
    ranking_week: Optional[str] = None

    @property
    def full_name(self) -> str:
        """Return player's full name."""
        return f"{self.first_name} {self.last_name}"

    @property
    def display_name(self) -> str:
        """Return name in 'Last, First' format."""
        return f"{self.last_name}, {self.first_name}"

    def __str__(self) -> str:
        return f"{self.full_name} ({self.player_id})"


@dataclass
class RankingWeek:
    """Represents a ranking week."""

    year: int
    week: int
    url: Optional[str] = None
    is_current: bool = False

    @property
    def label(self) -> str:
        """Return display label like 'KW 2 2026'."""
        return f"KW {self.week} {self.year}"

    @property
    def filename(self) -> str:
        """Return filename for storing this week's data."""
        return f"{self.year}_KW{self.week:02d}.xlsx"

    def __str__(self) -> str:
        return self.label

"""Download Excel ranking files from DBV."""

import re
from collections.abc import Callable
from pathlib import Path

import httpx
from platformdirs import user_data_dir

from ..models.player import RankingWeek

type ProgressCallback = Callable[[RankingWeek, int, int], None]

BASE_URL = "https://turniere.badminton.de"
RANKING_URL = f"{BASE_URL}/ranking"
HISTORY_URL = f"{BASE_URL}/ranking/embed/history"
DOWNLOAD_URL = f"{BASE_URL}/ranking/download"
EXCEL_URL_PATTERN = f"{BASE_URL}/uploads/ranking/Ranking_{{year}}_KW{{week:02d}}.xlsx"


class Downloader:
    """Download and manage ranking Excel files."""

    def __init__(self, data_dir: Path | None = None):
        if data_dir is None:
            data_dir = Path(user_data_dir("badminton-cli"))
        self.data_dir = data_dir
        self.excel_dir = data_dir / "excel"
        self.excel_dir.mkdir(parents=True, exist_ok=True)

    def get_available_weeks(self) -> list[RankingWeek]:
        """Fetch list of available ranking weeks from the server."""
        seen: set[tuple[int, int]] = set()
        weeks = []
        with httpx.Client(timeout=30.0) as client:
            response = client.get(HISTORY_URL)
            response.raise_for_status()

            pattern = r"Ranking_(\d{4})_KW(\d{2})\.xlsx"
            matches = re.findall(pattern, response.text)

            for year_str, week_str in matches:
                year = int(year_str)
                week = int(week_str)
                key = (year, week)
                if key in seen:
                    continue
                seen.add(key)
                url = EXCEL_URL_PATTERN.format(year=year, week=week)
                weeks.append(RankingWeek(year=year, week=week, url=url))

        if weeks:
            weeks[0].is_current = True

        return weeks

    def get_local_weeks(self) -> list[RankingWeek]:
        """Get list of locally cached ranking weeks."""
        weeks = []
        pattern = re.compile(r"Ranking_(\d{4})_KW(\d{2})\.xlsx")

        for file in self.excel_dir.glob("Ranking_*.xlsx"):
            match = pattern.match(file.name)
            if match:
                year = int(match.group(1))
                week = int(match.group(2))
                weeks.append(RankingWeek(year=year, week=week))

        weeks.sort(key=lambda w: (w.year, w.week), reverse=True)
        return weeks

    def get_excel_path(self, week: RankingWeek) -> Path:
        """Get local path for a ranking week's Excel file."""
        return self.excel_dir / f"Ranking_{week.year}_KW{week.week:02d}.xlsx"

    def is_downloaded(self, week: RankingWeek) -> bool:
        """Check if a ranking week's Excel file is already downloaded."""
        return self.get_excel_path(week).exists()

    def download_week(
        self, week: RankingWeek, force: bool = False
    ) -> Path:
        """Download a single ranking week's Excel file.

        Args:
            week: The ranking week to download.
            force: If True, re-download even if file exists.

        Returns:
            Path to the downloaded file.
        """
        path = self.get_excel_path(week)

        if path.exists() and not force:
            return path

        url = week.url or EXCEL_URL_PATTERN.format(year=week.year, week=week.week)

        with httpx.Client(timeout=60.0) as client:
            response = client.get(url)
            response.raise_for_status()
            path.write_bytes(response.content)

        return path

    def download_all(
        self,
        force_current: bool = True,
        progress_callback: ProgressCallback | None = None,
    ) -> list[Path]:
        """Download all available ranking weeks.

        Args:
            force_current: If True, always re-download the current week.
            progress_callback: Optional callback(week, index, total) for progress.

        Returns:
            List of paths to downloaded files.
        """
        weeks = self.get_available_weeks()
        downloaded = []

        for i, week in enumerate(weeks):
            if progress_callback:
                progress_callback(week, i, len(weeks))

            force = force_current and week.is_current
            if self.is_downloaded(week) and not force:
                downloaded.append(self.get_excel_path(week))
                continue

            try:
                path = self.download_week(week, force=force)
                downloaded.append(path)
            except httpx.HTTPError:
                pass

        return downloaded

    def get_live_current_week(self) -> RankingWeek | None:
        """Fetch the current week from the live ranking page."""
        from datetime import datetime

        with httpx.Client(timeout=30.0, follow_redirects=True) as client:
            response = client.get(RANKING_URL)
            response.raise_for_status()

            match = re.search(r"Rangliste\s+KW\s*(\d+)", response.text)
            if not match:
                return None

            week = int(match.group(1))
            year = datetime.now().year
            return RankingWeek(
                year=year, week=week, url=DOWNLOAD_URL, is_current=True
            )

    def get_current_week(self) -> RankingWeek | None:
        """Get the current (most recent) ranking week."""
        try:
            live = self.get_live_current_week()
            if live is not None:
                return live
        except (httpx.HTTPError, Exception):
            pass
        weeks = self.get_available_weeks()
        return weeks[0] if weeks else None

    def ensure_current(self) -> Path | None:
        """Ensure current week's data is downloaded.

        Returns:
            Path to current week's Excel file, or None if unavailable.
        """
        week = self.get_current_week()
        if week is None:
            return None
        return self.download_week(week, force=True)

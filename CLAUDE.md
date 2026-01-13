# Badminton CLI

Console application for exploring German U19 badminton rankings.

## Build and Run

This project uses `uv` for dependency management.

```bash
# Install dependencies
uv sync

# Run the CLI
uv run badminton-cli

# Run with a specific command
uv run badminton-cli search "player name"
uv run badminton-cli top --discipline HE
uv run badminton-cli graph 01-150083 --since 6m

# Run tests
uv run pytest

# Type checking
uv run pyright
```

## Project Structure

```
src/badminton_cli/
├── cli.py              # Click CLI commands (main entry point)
├── data/
│   ├── database.py     # SQLite database for indexed player queries
│   ├── downloader.py   # Downloads ranking Excel files from DBV
│   └── parser.py       # Parses Excel files into Player objects
├── models/
│   └── player.py       # Player dataclass and Discipline enum
├── search/
│   └── fuzzy.py        # Fuzzy search using rapidfuzz
├── ui/
│   ├── console.py      # Rich console configuration and styles
│   ├── graphs.py       # Terminal graphs using plotext
│   ├── interactive.py  # Interactive TUI mode
│   ├── panels.py       # Rich panels for player/comparison display
│   └── tables.py       # Rich tables for rankings/search results
└── utils/
    └── points.py       # Points calculation utilities
```

## Key Components

- **CLI (`cli.py`)**: Main entry point using Click. Supports commands: `update`, `search`, `player`, `compare`, `team`, `top`, `graph`, `history`.
- **Database (`data/database.py`)**: SQLite storage with indexes for fast player lookups. Stores multiple ranking weeks for historical tracking.
- **Player Model (`models/player.py`)**: Core dataclass with discipline enum (HE, HD, DE, DD, HM, DM).
- **Interactive Mode (`ui/interactive.py`)**: TUI launched when running without arguments.

## Code Patterns

- Use Rich library for all terminal output (tables, panels, progress spinners)
- Database queries return `Player` objects, never raw rows
- Age-group rank is computed on-demand via SQL subquery (can be slow for large datasets)
- Graph command supports `--since` duration filters (e.g., "1y", "6m", "3m")

## Disciplines

- **HE**: Herren Einzel (Men's Singles)
- **DE**: Damen Einzel (Women's Singles)
- **HD**: Herren Doppel (Men's Doubles)
- **DD**: Damen Doppel (Women's Doubles)
- **HM**: Herren Mixed (Mixed with male player)
- **DM**: Damen Mixed (Mixed with female player)

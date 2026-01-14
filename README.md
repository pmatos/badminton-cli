# Badminton CLI

A beautiful console application for exploring German U19 badminton rankings from the German Badminton Association (DBV).

## Features

- **Search players** by name with fuzzy matching
- **View player details** including rankings across all disciplines
- **Compare players** side-by-side
- **Calculate team points** for doubles partnerships
- **View top rankings** filtered by discipline
- **Track ranking history** with terminal graphs
- **JSON output** for all commands for programmatic access

## Installation

```bash
# Using uv (recommended)
uv tool install badminton-cli

# Or using pipx
pipx install badminton-cli

# Or using pip
pip install badminton-cli
```

## Quick Start

```bash
# Download ranking data
badminton-cli update

# Search for a player
badminton-cli search "Max Mustermann"

# View player details
badminton-cli player 01-150083

# Show top rankings in Men's Singles
badminton-cli top --discipline HE

# Compare two players
badminton-cli compare 01-150083 01-150084

# View ranking history graph
badminton-cli graph 01-150083 --since 6m
```

## Commands

| Command | Description |
|---------|-------------|
| `update` | Download and index ranking data from DBV |
| `search <name>` | Fuzzy search for players |
| `player <id>` | Show detailed player information |
| `compare <id1> <id2>` | Side-by-side player comparison |
| `team <id1> <id2>` | Calculate combined team points |
| `top` | Show top-ranked players |
| `graph <id>` | Show ranking history graph |
| `history` | List available ranking weeks |

All commands support `--json` for structured output.

## Disciplines

| Code | German | English |
|------|--------|---------|
| HE | Herren Einzel | Men's Singles |
| DE | Damen Einzel | Women's Singles |
| HD | Herren Doppel | Men's Doubles |
| DD | Damen Doppel | Women's Doubles |
| HM | Herren Mixed | Mixed (male player) |
| DM | Damen Mixed | Mixed (female player) |

## Interactive Mode

Run without arguments for an interactive TUI:

```bash
badminton-cli
```

## Claude Code Plugin

A Claude Code plugin is available for AI-assisted ranking exploration. See the [claude-plugin](./claude-plugin/) directory.

## Requirements

- Python 3.12+

## License

MIT License - see [LICENSE](./LICENSE) for details.

## Links

- [PyPI](https://pypi.org/project/badminton-cli/)
- [GitHub](https://github.com/pmatos/badminton-cli)
- [Issues](https://github.com/pmatos/badminton-cli/issues)

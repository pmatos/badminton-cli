# Badminton CLI Plugin for Claude Code

A Claude Code plugin for exploring German U19 badminton rankings using the `badminton-cli` tool.

## Features

- **Search players** by name with fuzzy matching
- **View player details** including rankings across all disciplines
- **Compare players** side-by-side
- **Calculate team points** for doubles partnerships
- **View top rankings** filtered by discipline
- **Analyze trends** with historical ranking data
- **Specialized agent** for in-depth ranking analysis

## Installation

### Step 1: Install badminton-cli

The plugin requires `badminton-cli` to be installed. Install it from PyPI:

```bash
# Using uv (recommended)
uv tool install badminton-cli

# Or using pipx
pipx install badminton-cli
```

### Step 2: Install the Plugin

In Claude Code, run:

```
/plugin marketplace add pmatos/badminton-cli
/plugin install badminton-cli@badminton-cli
```

The first command adds the marketplace, the second installs the plugin.

#### Alternative: Development Mode

For local development or testing:

```bash
git clone https://github.com/pmatos/badminton-cli.git
claude --plugin-dir ./badminton-cli/plugin
```

### Step 3: Enable the Plugin (if not auto-enabled)

```
/plugin enable badminton-cli
```

### Step 4: Initialize Ranking Data

Before using the plugin, download the ranking data:

```bash
/badminton:update
```

Or for historical data:

```bash
/badminton:update --all
```

## Usage

### Slash Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/badminton:search <name>` | Search for players | `/badminton:search Mustermann` |
| `/badminton:player <id>` | Show player details | `/badminton:player 01-150083` |
| `/badminton:top [discipline]` | Top rankings | `/badminton:top HE` |
| `/badminton:compare <id1> <id2>` | Compare two players | `/badminton:compare 01-150083 01-150084` |
| `/badminton:update [flags]` | Update ranking data | `/badminton:update --all` |

### Natural Language Queries

With the plugin installed, Claude understands badminton ranking queries:

- "Who are the top 10 players in men's singles?"
- "Show me details for player 01-150083"
- "Compare these two players and tell me who's better"
- "Find the best mixed doubles partner for this player"
- "How has this player's ranking changed over the past 6 months?"

### Ranking Analyst Agent

For complex analysis tasks, Claude can use the specialized ranking analyst agent:

- Trend analysis across multiple players
- Finding optimal doubles partnerships
- Age-group performance comparisons
- Rising star identification

## Disciplines

| Code | German | English |
|------|--------|---------|
| HE | Herren Einzel | Men's Singles |
| DE | Damen Einzel | Women's Singles |
| HD | Herren Doppel | Men's Doubles |
| DD | Damen Doppel | Women's Doubles |
| HM | Herren Mixed | Mixed (male player) |
| DM | Damen Mixed | Mixed (female player) |

## Dependencies

- **badminton-cli**: The underlying CLI tool (install from PyPI)
- **Python 3.12+**: Required by badminton-cli
- **Claude Code**: The AI coding assistant

## Plugin Structure

```
plugin/
├── .claude-plugin/
│   └── plugin.json           # Plugin manifest
├── commands/
│   ├── search.md             # /badminton:search
│   ├── player.md             # /badminton:player
│   ├── top.md                # /badminton:top
│   ├── compare.md            # /badminton:compare
│   └── update.md             # /badminton:update
├── skills/
│   └── badminton-cli/
│       ├── SKILL.md          # CLI usage skill
│       └── references/       # Detailed documentation
├── agents/
│   └── ranking-analyst.md    # Analysis agent
└── README.md                 # This file
```

## Troubleshooting

### "Command not found: badminton-cli"

Install the CLI tool:

```bash
uv tool install badminton-cli
```

### "No data available"

Download ranking data first:

```bash
badminton-cli update
```

### "Player not found"

- Check the player ID format (XX-XXXXXX)
- Use `/badminton:search` to find the correct ID
- The player may not be in U19 rankings

## Development

To modify the plugin:

1. Edit files in the `plugin/` directory
2. Test with Claude Code using `--plugin-dir`:
   ```bash
   claude --plugin-dir /path/to/badminton-cli/plugin
   ```

## License

MIT License - see [LICENSE](../LICENSE) for details.

## Links

- [badminton-cli on PyPI](https://pypi.org/project/badminton-cli/)
- [GitHub Repository](https://github.com/pmatos/badminton-cli)
- [Issue Tracker](https://github.com/pmatos/badminton-cli/issues)

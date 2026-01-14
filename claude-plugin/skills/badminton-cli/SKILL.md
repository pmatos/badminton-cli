# Badminton CLI Skill

Use this skill when the user asks about German U19 badminton rankings, player statistics, ranking history, or wants to explore badminton data. This skill enables interaction with the `badminton-cli` tool for querying the German Badminton Association (DBV) U19 rankings.

## Prerequisites Check

Before using any badminton-cli commands, verify the tool is installed:

```bash
which badminton-cli || echo "NOT_INSTALLED"
```

If NOT_INSTALLED, install it:

```bash
uv tool install badminton-cli
```

Or with pipx:

```bash
pipx install badminton-cli
```

## Available Commands

All commands support `--json` flag for structured output. **Always use `--json`** when you need to process the data programmatically.

### 1. Update Rankings Data

Download and index the latest ranking data from DBV:

```bash
badminton-cli update
```

Options:
- `--all`: Download all historical ranking weeks
- `--force`: Force re-download of all files

**Run this first** if data hasn't been downloaded yet.

### 2. Search for Players

Fuzzy search for players by name:

```bash
badminton-cli search "Max Mustermann" --json
```

Options:
- `--limit, -n`: Maximum results (default: 10)

JSON output structure:
```json
[
  {
    "player_id": "01-150083",
    "name": "Max Mustermann",
    "fuzzy_score": 95.5,
    "club": "BC Example",
    "best_rank": 5,
    "best_discipline": "HE"
  }
]
```

### 3. Get Player Details

Show detailed information for a specific player:

```bash
badminton-cli player 01-150083 --json
```

Options:
- `--week, -w`: Specific ranking week (e.g., 'KW2', '2026-KW02')
- `--age-rank, -a`: Include rank within player's age group

JSON output structure:
```json
{
  "player_id": "01-150083",
  "full_name": "Max Mustermann",
  "birth_year": 2008,
  "club": "BC Example",
  "district": "Bayern",
  "age_class_1": "U17",
  "age_class_2": "U19",
  "ranking_week": "KW 2 2026",
  "rankings": [
    {
      "discipline": "HE",
      "rank": 15,
      "federation_rank": 25,
      "points": 3500.5,
      "tournaments": 12,
      "age_group_rank": 8
    }
  ]
}
```

### 4. Compare Two Players

Side-by-side comparison of two players:

```bash
badminton-cli compare 01-150083 01-150084 --json
```

Options:
- `--week, -w`: Specific ranking week

### 5. Calculate Team Points

Calculate combined points for a doubles partnership:

```bash
badminton-cli team 01-150083 01-150084 --json
```

Options:
- `--discipline, -d`: Filter to specific doubles (HD, DD, HM, DM)
- `--week, -w`: Specific ranking week

JSON output structure:
```json
{
  "player1": {"player_id": "01-150083", "full_name": "Max Mustermann"},
  "player2": {"player_id": "01-150084", "full_name": "Erika Musterfrau"},
  "team": [
    {
      "discipline": "HM",
      "player1_points": 2500.0,
      "player2_points": 2200.0,
      "team_total": 4700.0
    }
  ]
}
```

### 6. Top Rankings

Show top-ranked players:

```bash
badminton-cli top --discipline HE --limit 20 --json
```

Options:
- `--discipline, -d`: Filter by discipline (HE, HD, DE, DD, HM, DM)
- `--limit, -n`: Number of results (default: 20)
- `--week, -w`: Specific ranking week
- `--age-rank, -a`: Include age-group ranks

### 7. Ranking History Graph

Get historical ranking data for visualization:

```bash
badminton-cli graph 01-150083 --discipline HE --json
```

Options:
- Multiple player IDs supported for comparison
- `--discipline, -d`: Specific discipline
- `--points, -p`: Show points instead of rank
- `--since, -s`: Time filter ('1y', '6m', '3m')
- `--age-rank, -a`: Show age-group rank progression

JSON output structure:
```json
{
  "discipline": "HE",
  "y_axis": "rank",
  "players": [
    {
      "name": "Max Mustermann",
      "data": [
        {"week": 2, "year": 2026, "label": "KW 2 2026", "rank": 10, "points": 3500.5}
      ]
    }
  ]
}
```

### 8. Available Ranking Weeks

List all indexed ranking weeks:

```bash
badminton-cli history --json
```

## Disciplines

| Code | Full Name | English |
|------|-----------|---------|
| HE | Herren Einzel | Men's Singles |
| DE | Damen Einzel | Women's Singles |
| HD | Herren Doppel | Men's Doubles |
| DD | Damen Doppel | Women's Doubles |
| HM | Herren Mixed | Mixed (male player) |
| DM | Damen Mixed | Mixed (female player) |

## Common Workflows

### Find a player and show their details

1. Search by name: `badminton-cli search "name" --json`
2. Get player ID from results
3. Show details: `badminton-cli player <id> --json`

### Compare ranking progression

1. Get player IDs via search
2. Run: `badminton-cli graph <id1> <id2> --discipline HE --since 6m --json`
3. Analyze the historical data

### Find optimal doubles partner

1. Get player details to see their doubles points
2. Use team command to calculate combined points with potential partners
3. Compare team totals across different pairings

## Error Handling

If commands fail with "No data available":
1. Run `badminton-cli update` to download ranking data
2. Retry the command

If a player is not found:
1. Try a partial name search
2. Check spelling variations
3. The player may not be in U19 rankings

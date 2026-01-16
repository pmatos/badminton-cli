---
description: Show top-ranked badminton players
---

# Top Rankings

Show the top-ranked German U19 badminton players.

## Arguments

Optional discipline filter: `$ARGUMENTS`

Valid disciplines:
- `HE` - Men's Singles (Herren Einzel)
- `DE` - Women's Singles (Damen Einzel)
- `HD` - Men's Doubles (Herren Doppel)
- `DD` - Women's Doubles (Damen Doppel)
- `HM` - Mixed (male player)
- `DM` - Mixed (female player)

## Instructions

1. First, ensure badminton-cli is installed:
   ```bash
   which badminton-cli || uv tool install badminton-cli
   ```

2. Run the top command with JSON output (note: `--json` is a global flag that comes BEFORE the command):
   - If discipline specified:
     ```bash
     badminton-cli --json top --discipline "$ARGUMENTS" --limit 20 --age-rank
     ```
   - If no discipline specified, show top for all disciplines:
     ```bash
     badminton-cli --json top --limit 10 --age-rank
     ```

3. Present the rankings in a clear table format:
   - Rank
   - Player name
   - Club
   - Points
   - Tournaments played
   - Age-group rank (if available)

4. Offer to show detailed information for any player in the list.

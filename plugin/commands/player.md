---
description: Show detailed information for a badminton player
---

# Player Details

Show detailed ranking information for a specific German U19 badminton player.

## Arguments

The player ID is provided as: `$ARGUMENTS`

Player IDs are in the format `XX-XXXXXX` (e.g., `01-150083`).

## Instructions

1. First, ensure badminton-cli is installed:
   ```bash
   which badminton-cli || uv tool install badminton-cli
   ```

2. Get player details with JSON output and age-group ranking (note: `--json` is a global flag that comes BEFORE the command):
   ```bash
   badminton-cli --json player "$ARGUMENTS" --age-rank
   ```

3. Present the information clearly:
   - Player name, birth year, club, district
   - Age classes
   - For each discipline they're ranked in:
     - Overall rank and federation rank
     - Points and tournaments played
     - Age-group rank

4. If the player ID is not found:
   - Suggest using `/badminton:search` to find the correct ID
   - Check if the format is correct (XX-XXXXXX)

5. Offer follow-up actions:
   - Compare with another player
   - Show ranking history/graph
   - Find potential doubles partners

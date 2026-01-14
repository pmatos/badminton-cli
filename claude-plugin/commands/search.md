---
description: Search for badminton players by name
---

# Search Badminton Players

Search for German U19 badminton players using fuzzy name matching.

## Arguments

The search query is provided as: `$ARGUMENTS`

## Instructions

1. First, ensure badminton-cli is installed:
   ```bash
   which badminton-cli || uv tool install badminton-cli
   ```

2. Run the search with JSON output:
   ```bash
   badminton-cli search "$ARGUMENTS" --json
   ```

3. Parse the JSON results and present them in a readable format showing:
   - Player name and ID
   - Club
   - Best ranking and discipline
   - Match score (how well the name matched)

4. If no results found, suggest:
   - Checking spelling
   - Using partial names
   - The player may not be in U19 rankings

5. Offer to show detailed information for any player in the results.

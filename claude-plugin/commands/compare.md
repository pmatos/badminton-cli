---
description: Compare two badminton players side-by-side
---

# Compare Players

Compare two German U19 badminton players side-by-side across all their disciplines.

## Arguments

Two player IDs separated by space: `$ARGUMENTS`

Example: `01-150083 01-150084`

## Instructions

1. First, ensure badminton-cli is installed:
   ```bash
   which badminton-cli || uv tool install badminton-cli
   ```

2. Parse the two player IDs from the arguments.

3. Run the comparison with JSON output:
   ```bash
   badminton-cli compare <id1> <id2> --json
   ```

4. Present a side-by-side comparison:
   - Player names, clubs, birth years
   - For each discipline both players are ranked in:
     - Rank comparison
     - Points comparison
     - Tournaments played

5. Highlight:
   - Who is ranked higher in each discipline
   - Point differences
   - Common disciplines they could compete in

6. If either player ID is invalid:
   - Suggest using `/badminton:search` to find correct IDs

7. Offer follow-up actions:
   - Calculate team points if they could play doubles together
   - Show ranking history comparison

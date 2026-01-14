---
description: Update badminton ranking data from DBV
---

# Update Rankings

Download and index the latest German U19 badminton ranking data from the German Badminton Association (DBV).

## Arguments

Optional flags: `$ARGUMENTS`

- `--all`: Download all historical ranking weeks
- `--force`: Force re-download of all files

## Instructions

1. First, ensure badminton-cli is installed:
   ```bash
   which badminton-cli || uv tool install badminton-cli
   ```

2. Run the update command:
   - Default (current week only):
     ```bash
     badminton-cli update
     ```
   - With flags if specified:
     ```bash
     badminton-cli update $ARGUMENTS
     ```

3. Report the result:
   - How many ranking weeks were downloaded
   - How many players were indexed
   - Any errors encountered

4. After successful update, suggest next steps:
   - Search for players: `/badminton:search <name>`
   - View top rankings: `/badminton:top`
   - Check available weeks: `badminton-cli history --json`

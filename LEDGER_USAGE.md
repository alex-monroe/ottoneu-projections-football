# Import Ledger System

## Overview

The import ledger system tracks which NFL weeks have been imported into the database and which are still pending. It generates both human-readable (Markdown) and machine-readable (JSON) status reports.

## Files

- **`IMPORT_LEDGER.md`** - Human-readable status (commit to git)
- **`import_ledger.json`** - Machine-readable status (for automation)
- **`scripts/generate_import_ledger.py`** - Generator script
- **`update-ledger.sh`** - Quick update script

## Quick Usage

### View Current Status

```bash
# View the ledger
cat IMPORT_LEDGER.md

# Or view JSON
cat import_ledger.json | python -m json.tool
```

### Update the Ledger

```bash
# After importing new data, update the ledger
./update-ledger.sh

# Or run the script directly
python scripts/generate_import_ledger.py
```

## Ledger Format

### Markdown (IMPORT_LEDGER.md)

Shows:
- Total players and projections
- Status by season and week
- ✅ Imported weeks with data source
- ⏳ Pending weeks that need import
- Import commands

### JSON (import_ledger.json)

```json
{
  "last_updated": "2026-02-07T21:02:37",
  "summary": {
    "total_players": 438,
    "total_projections": 1264,
    "total_weeks_imported": 4
  },
  "seasons": {
    "2023": {
      "weeks_imported": 4,
      "weeks_pending": 14,
      "weeks": {
        "1": {"status": "imported", "sources": ["nflverse"]},
        "5": {"status": "pending", "sources": []}
      }
    }
  }
}
```

## Workflow

### 1. Check Status Before Import

```bash
./update-ledger.sh
cat IMPORT_LEDGER.md
```

### 2. Import Missing Weeks

```bash
# Start server
uvicorn src.main:app --reload

# Import a pending week
curl -X POST "http://localhost:8000/api/loaders/import/weekly" \
  -H "Content-Type: application/json" \
  -d '{"year": 2023, "week": 5, "source": "nflverse"}'
```

### 3. Update Ledger After Import

```bash
./update-ledger.sh
```

### 4. Commit Changes

```bash
git add IMPORT_LEDGER.md import_ledger.json
git commit -m "Update import ledger: added 2023 week 5"
```

## Automation Examples

### Check if Week is Imported (Bash)

```bash
#!/bin/bash
YEAR=2023
WEEK=5

if grep -q "| *${WEEK} | ✅ Imported" IMPORT_LEDGER.md; then
  echo "Week ${WEEK} is imported"
else
  echo "Week ${WEEK} needs import"
fi
```

### Check Status (Python)

```python
import json

with open('import_ledger.json') as f:
    ledger = json.load(f)

# Check if a week is imported
season = "2023"
week = "5"
status = ledger["seasons"][season]["weeks"][week]["status"]

if status == "imported":
    sources = ledger["seasons"][season]["weeks"][week]["sources"]
    print(f"Week {week} imported from: {sources}")
else:
    print(f"Week {week} is pending")
```

### Automated Import Script

```python
import json
import requests

# Load ledger
with open('import_ledger.json') as f:
    ledger = json.load(f)

# Find pending weeks for 2023
pending = []
for week, data in ledger["seasons"]["2023"]["weeks"].items():
    if data["status"] == "pending":
        pending.append(int(week))

# Import all pending weeks
for week in sorted(pending)[:5]:  # Import first 5 pending
    response = requests.post(
        "http://localhost:8000/api/loaders/import/weekly",
        json={"year": 2023, "week": week, "source": "nflverse"}
    )
    print(f"Week {week}: {response.status_code}")
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Update Import Ledger

on:
  schedule:
    - cron: '0 12 * * 2'  # Every Tuesday at noon
  workflow_dispatch:

jobs:
  update-ledger:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Update ledger
        run: python scripts/generate_import_ledger.py
        env:
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_KEY: ${{ secrets.SUPABASE_KEY }}
      - name: Commit changes
        run: |
          git config user.name "GitHub Actions"
          git config user.email "actions@github.com"
          git add IMPORT_LEDGER.md import_ledger.json
          git commit -m "chore: update import ledger" || exit 0
          git push
```

## Tips

1. **Update Regularly**: Run `./update-ledger.sh` after each import
2. **Version Control**: Commit ledger files to track import history
3. **Pre-Import Check**: Always check ledger before importing to avoid duplicates
4. **Automation**: Use JSON ledger for scripted imports

## Customization

### Add More Seasons

Edit `scripts/generate_import_ledger.py`:

```python
# Line ~80
seasons = [2022, 2023, 2024, 2025]  # Add more years
```

### Change Week Range

```python
# Line ~81
weeks = list(range(1, 19))  # 1-18 regular season
# Or include playoffs:
# weeks = list(range(1, 23))  # 1-22 including playoffs
```

## Troubleshooting

**Ledger shows wrong data:**
- Make sure .env has correct Supabase credentials
- Run `./update-ledger.sh` to regenerate

**Script fails:**
- Check database connection: `python scripts/generate_import_ledger.py`
- Verify Supabase credentials in `.env`

**Want to reset ledger:**
- Just re-run: `./update-ledger.sh`
- Ledger is generated fresh each time from database

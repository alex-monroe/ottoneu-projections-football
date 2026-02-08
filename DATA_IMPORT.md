# Data Import Guide

## Overview

The system loads historical NFL player statistics from public data sources:
- **Primary**: NFLVerse (via nfl-data-py Python library)
- **Backup**: Fantasy Football Data Pros CSV files from GitHub

## Quick Start

### Import a Single Week

```bash
# Start the server
source venv/bin/activate
uvicorn src.main:app --reload

# In another terminal, import data
curl -X POST "http://localhost:8000/api/loaders/import/weekly" \
  -H "Content-Type: application/json" \
  -d '{"year": 2023, "week": 1, "source": "nflverse"}'
```

### Import Multiple Weeks

```bash
# Import weeks 1-4 of the 2023 season
curl -X POST "http://localhost:8000/api/loaders/import/season?year=2023&start_week=1&end_week=4" \
  -H "Content-Type: application/json"
```

## API Endpoints

### POST /api/loaders/import/weekly

Import data for a single week.

**Request Body:**
```json
{
  "year": 2023,
  "week": 1,
  "source": "nflverse"
}
```

**Response:**
```json
{
  "success": true,
  "players_imported": 120,
  "players_updated": 5,
  "projections_imported": 450,
  "projections_updated": 0,
  "source": "nflverse",
  "year": 2023,
  "week": 1,
  "errors": [],
  "timestamp": "2024-01-15T10:30:00"
}
```

### POST /api/loaders/import/season

Import data for multiple weeks.

**Query Parameters:**
- `year` (required): NFL season year (1999-2030)
- `source` (optional): Data source (default: "nflverse")
- `start_week` (optional): First week to import (default: 1)
- `end_week` (optional): Last week to import (default: 18)

**Example:**
```bash
curl -X POST "http://localhost:8000/api/loaders/import/season?year=2023&start_week=1&end_week=18"
```

### GET /api/loaders/sources

Get list of available data sources.

**Response:**
```json
[
  {
    "name": "nflverse",
    "status": "available",
    "description": "NFLVerse historical player statistics"
  },
  {
    "name": "ffdp",
    "status": "available",
    "description": "Fantasy Football Data Pros CSV files"
  }
]
```

### GET /api/loaders/available-data

Get summary of what data exists in the database.

**Response:**
```json
{
  "total_weeks": 36,
  "seasons": [
    {
      "season": 2023,
      "weeks": [
        {"week": 1, "sources": ["nflverse"]},
        {"week": 2, "sources": ["nflverse"]}
      ],
      "week_count": 2
    }
  ],
  "sources": ["nflverse"]
}
```

## Using Swagger UI

1. Start the server: `uvicorn src.main:app --reload`
2. Visit http://localhost:8000/docs
3. Expand the "loaders" section
4. Try out the endpoints interactively

## Data Sources

### NFLVerse (Primary)

- **Library**: nfl-data-py
- **Type**: Historical actual stats (1999-present)
- **Format**: Returns pandas DataFrames
- **No authentication required**
- **Advantages**: Well-maintained, active project, structured data

### FFDP (Backup)

- **Source**: GitHub repository (fantasydatapros/data)
- **Type**: CSV files via HTTP
- **Format**: Weekly CSV files
- **Advantages**: No external library dependency, simple HTTP requests

### Automatic Fallback

If the primary source (NFLVerse) fails, the system automatically falls back to FFDP:

```python
# This will try NFLVerse first, then FFDP if it fails
result = service.import_weekly_data(year=2023, week=1, source="nflverse", use_fallback=True)
```

## Column Mapping

The system automatically maps columns from various sources to our database schema:

**NFLVerse Columns** → **Database Schema:**
- `passing_yards` → `pass_yds`
- `completions` → `pass_cmp`
- `attempts` → `pass_att`
- `rushing_yards` → `rush_yds`
- `receptions` → `receptions`
- etc.

**FFDP Columns** → **Database Schema:**
- `PassYds` → `pass_yds`
- `PassCmp` → `pass_cmp`
- `RushYds` → `rush_yds`
- etc.

## Troubleshooting

### Import Failed

If an import fails, check the error messages in the response:

```json
{
  "success": false,
  "errors": ["No data available for 2099 week 1"],
  ...
}
```

### Data Not Available (404)

Some weeks/years may not have data available. The API will return a 404 status code:

```bash
# This will likely return 404 (future year)
curl -X POST "http://localhost:8000/api/loaders/import/weekly" \
  -H "Content-Type: application/json" \
  -d '{"year": 2025, "week": 1}'
```

### Testing

Run the loader tests to verify everything is working:

```bash
pytest tests/loaders/ -v
pytest tests/api/test_loaders.py -v
```

## Next Steps

After importing data:
1. **Phase 3**: Implement scoring calculator to compute fantasy points
2. **Phase 4**: Build dashboard to view projections
3. **Phase 5**: Add scheduled jobs for automatic weekly updates

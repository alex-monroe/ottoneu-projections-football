# NFL Data Import Ledger

**Last Updated:** 2026-02-07 21:02:37

**Total Players:** 438
**Total Projections:** 1264


## 2024 Season

**Status:** 0/18 weeks imported (all pending)

⚠️ No data imported for this season yet.

**Action:** Run import for this season


## 2023 Season

**Status:** 4/18 weeks imported (14 pending)

| Week | Status | Source | Action |
|------|--------|--------|--------|
|  1 | ✅ Imported | nflverse | Re-import to update |
|  2 | ✅ Imported | nflverse | Re-import to update |
|  3 | ✅ Imported | nflverse | Re-import to update |
|  4 | ✅ Imported | nflverse | Re-import to update |
|  5 | ⏳ Pending | - | **Import needed** |
|  6 | ⏳ Pending | - | **Import needed** |
|  7 | ⏳ Pending | - | **Import needed** |
|  8 | ⏳ Pending | - | **Import needed** |
|  9 | ⏳ Pending | - | **Import needed** |
| 10 | ⏳ Pending | - | **Import needed** |
| 11 | ⏳ Pending | - | **Import needed** |
| 12 | ⏳ Pending | - | **Import needed** |
| 13 | ⏳ Pending | - | **Import needed** |
| 14 | ⏳ Pending | - | **Import needed** |
| 15 | ⏳ Pending | - | **Import needed** |
| 16 | ⏳ Pending | - | **Import needed** |
| 17 | ⏳ Pending | - | **Import needed** |
| 18 | ⏳ Pending | - | **Import needed** |

## Import Commands

```bash
# Start the server
uvicorn src.main:app --reload

# Import a single week
curl -X POST "http://localhost:8000/api/loaders/import/weekly" \
  -H "Content-Type: application/json" \
  -d '{"year": 2023, "week": 5, "source": "nflverse"}'

# Import an entire season
curl -X POST "http://localhost:8000/api/loaders/import/season?year=2023&start_week=1&end_week=18"
```


## Data Sources

- **nflverse**: Primary source (nfl-data-py library)
- **ffdp**: Backup source (Fantasy Football Data Pros CSV)

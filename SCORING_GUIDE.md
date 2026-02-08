# Fantasy Scoring Guide

## Overview

The scoring system calculates fantasy points from raw player statistics using configurable scoring formats. The system supports standard fantasy football scoring formats and custom configurations.

## Standard Scoring Formats

### PPR (Point Per Reception)
- **Passing**: 1 point per 25 yards, 4 points per TD, -2 per INT
- **Rushing**: 1 point per 10 yards, 6 points per TD
- **Receiving**: 1 point per reception, 1 point per 10 yards, 6 points per TD
- **Fumbles**: -2 points per fumble lost

### Half-PPR
- Same as PPR, except: **0.5 points per reception**

### Standard (No PPR)
- Same as PPR, except: **0 points per reception**

## API Usage

### Get Projections with Fantasy Points

```bash
GET /api/projections?season=2023&week=1&scoring=PPR (Point Per Reception)
```

**Parameters:**
- `season` (required): NFL season year (1999-2030)
- `week` (required): Week number (1-18)
- `scoring` (optional): Scoring format name (default: "PPR")
- `position` (optional): Filter by position (QB, RB, WR, TE)
- `team` (optional): Filter by team code
- `min_points` (optional): Minimum fantasy points threshold
- `sort_by` (optional): Sort field (fantasy_points, player_name)
- `order` (optional): Sort order (asc, desc)
- `limit` (optional): Number of results (default: 50, max: 500)
- `offset` (optional): Pagination offset

### Examples

#### Top 20 Players Overall (PPR)
```bash
curl "http://localhost:8000/api/projections?season=2023&week=1&scoring=PPR%20(Point%20Per%20Reception)&limit=20"
```

#### Top 10 Running Backs (Half-PPR)
```bash
curl "http://localhost:8000/api/projections?season=2023&week=1&scoring=Half-PPR&position=RB&limit=10"
```

#### Wide Receivers with 15+ Points (Standard)
```bash
curl "http://localhost:8000/api/projections?season=2023&week=1&scoring=Standard%20(No%20PPR)&position=WR&min_points=15"
```

#### Top Players by Position Shortcut
```bash
GET /api/projections/top/RB?season=2023&week=1&scoring=PPR&limit=20
```

## Response Format

```json
[
  {
    "player_id": "uuid",
    "player_name": "Christian McCaffrey",
    "team": "SF",
    "position": "RB",
    "week": 1,
    "season": 2023,
    "source": "nflverse",
    "fantasy_points": 25.90,
    "pass_yds": null,
    "pass_tds": null,
    "rush_yds": 152.0,
    "rush_tds": 1.0,
    "receptions": 5.0,
    "rec_yds": 39.0,
    "rec_tds": 0.0
  }
]
```

## Scoring Calculation Details

### Passing Points
```
points = (yards / 25) + (tds * 4) + (ints * -2)
```

**Example**: 300 yards, 3 TDs, 1 INT
```
(300/25) + (3*4) + (1*-2) = 12 + 12 - 2 = 22.00 points
```

### Rushing Points
```
points = (yards / 10) + (tds * 6)
```

**Example**: 120 yards, 2 TDs
```
(120/10) + (2*6) = 12 + 12 = 24.00 points
```

### Receiving Points
```
points = (receptions * ppr_value) + (yards / 10) + (tds * 6)
```

**Example (PPR)**: 8 receptions, 95 yards, 1 TD
```
(8*1) + (95/10) + (1*6) = 8 + 9.5 + 6 = 23.50 points
```

**Example (Standard)**: Same stats
```
(8*0) + (95/10) + (1*6) = 0 + 9.5 + 6 = 15.50 points
```

### Fumble Points
```
points = fumbles_lost * -2
```

## Python SDK Usage

### Calculate Points Programmatically

```python
from src.scoring.calculator import ScoringCalculator
from src.database.models import ScoringConfig, Projection
from decimal import Decimal

# Create a scoring configuration
ppr_config = ScoringConfig(
    name="PPR",
    pass_yds_per_point=Decimal("25"),
    pass_td_points=Decimal("4"),
    pass_int_points=Decimal("-2"),
    rush_yds_per_point=Decimal("10"),
    rush_td_points=Decimal("6"),
    rec_yds_per_point=Decimal("10"),
    rec_td_points=Decimal("6"),
    rec_points=Decimal("1"),  # PPR bonus
    fumble_points=Decimal("-2")
)

# Initialize calculator
calculator = ScoringCalculator(ppr_config)

# Calculate points from stats directly
points = calculator.calculate_points_from_stats(
    rush_yds=Decimal("100"),
    rush_tds=Decimal("1"),
    receptions=Decimal("5"),
    rec_yds=Decimal("50")
)
# Result: 10 + 6 + 5 + 5 = 26.00 points

# Or calculate from a Projection model
points = calculator.calculate_points(projection)

# Get detailed breakdown
breakdown = calculator.calculate_breakdown(projection)
# Returns: {'passing': 0.00, 'rushing': 16.00, 'receiving': 10.00, 'fumbles': 0.00, 'total': 26.00}
```

## Custom Scoring Configurations

### Create Custom Config via Database

```sql
INSERT INTO scoring_configs (
    name,
    pass_yds_per_point,
    pass_td_points,
    pass_int_points,
    rush_yds_per_point,
    rush_td_points,
    rec_yds_per_point,
    rec_td_points,
    rec_points,
    fumble_points,
    is_default
) VALUES (
    'My Custom League',
    20,    -- 1 point per 20 passing yards (more QB-friendly)
    6,     -- 6 points per passing TD
    -3,    -- -3 per interception (harsher)
    10,    -- 1 point per 10 rushing yards
    6,     -- 6 points per rushing TD
    10,    -- 1 point per 10 receiving yards
    6,     -- 6 points per receiving TD
    0.75,  -- 0.75 points per reception (between half and full PPR)
    -2,    -- -2 per fumble lost
    false
);
```

## Scoring Comparison

Example: Christian McCaffrey, Week 1, 2023
- Stats: 152 rush yards, 1 rush TD, 5 receptions, 39 rec yards

| Scoring Format | Fantasy Points | Breakdown |
|----------------|----------------|-----------|
| **PPR** | 25.90 | Rush: 16.2, Rec Yards: 3.9, Rec Bonus: 5.0, TD: 6.0 |
| **Half-PPR** | 24.40 | Rush: 16.2, Rec Yards: 3.9, Rec Bonus: 2.5, TD: 6.0 |
| **Standard** | 22.90 | Rush: 16.2, Rec Yards: 3.9, Rec Bonus: 0.0, TD: 6.0 |

## Seeding Standard Configs

The standard scoring configurations are automatically seeded when you run:

```bash
python scripts/seed_scoring_configs.py
```

This creates:
- PPR (Point Per Reception) - marked as default
- Half-PPR
- Standard (No PPR)

## Tips

### For Different League Types

**PPR Leagues**: Favor pass-catching running backs and slot receivers
- Examples: Austin Ekeler, Christian McCaffrey, Cooper Kupp

**Standard Leagues**: Favor high-volume rushers and deep threats
- Examples: Derrick Henry, Davante Adams, big-play receivers

**Dynasty/Keeper**: Consider using Half-PPR as a balanced middle ground

### Position Value by Scoring

**QB Value**: Consistent across formats (no receptions)
**RB Value**: Higher in PPR if they catch passes
**WR Value**: Slightly higher in PPR vs Standard
**TE Value**: Significantly higher in PPR (reception-dependent)

## Troubleshooting

### "Scoring configuration not found"
Make sure to use the full scoring name exactly as stored in the database:
- ✅ `PPR (Point Per Reception)`
- ❌ `PPR`
- ❌ `ppr`

### Points seem wrong
- Check which scoring format you're using
- Verify raw stats are accurate
- Use the breakdown endpoint to see category-by-category points

### No projections returned
- Verify data exists for that season/week (check `IMPORT_LEDGER.md`)
- Check your filters (position, team, min_points)
- Try without filters first

## Next Steps

- **Phase 4**: Build web dashboard to visualize projections
- **Phase 5**: Add scheduled weekly data updates
- **Future**: Custom projection models, player comparisons, trade analyzer

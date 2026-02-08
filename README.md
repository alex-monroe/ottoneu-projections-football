# NFL Fantasy Football Projections

A weekly NFL fantasy football projection system built with FastAPI and Supabase. Stores raw statistical projections and applies different scoring configurations (PPR, Half-PPR, Standard, custom) on top.

## Features

- **Multiple Data Sources**: Aggregates projections from ESPN, FantasyPros, and more
- **Flexible Scoring**: Apply any scoring configuration to raw stats (PPR, Half-PPR, Standard, custom)
- **REST API**: Full API access for integrations
- **Web Dashboard**: Simple dashboard for viewing and debugging projections
- **Automated Updates**: Scheduled weekly projection refreshes
- **Extensible**: Designed to evolve from aggregation to custom ML models

## Tech Stack

- **Backend**: FastAPI (Python 3.9+)
- **Database**: Supabase (PostgreSQL)
- **Data Sources**: ESPN API, FantasyPros
- **Scheduling**: APScheduler
- **Templates**: Jinja2

## Quick Start

### 1. Prerequisites

- Python 3.9 or higher
- A [Supabase](https://supabase.com) account (free tier works)
- Git

### 2. Clone and Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd ottoneu-projections-football

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Supabase

1. Create a new project in [Supabase](https://supabase.com)
2. Go to Settings → API to find your Project URL and anon/public key
3. Copy `.env.example` to `.env` and add your credentials:

```bash
cp .env.example .env
```

Edit `.env`:
```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key-here
ENVIRONMENT=development
```

### 4. Initialize Database

1. Open your Supabase project's SQL Editor
2. Copy and run the contents of `src/database/schema.sql`
3. Run the setup script to create default scoring configurations:

```bash
python scripts/setup_db.py
```

### 5. Run the Application

```bash
# Development server with auto-reload
uvicorn src.main:app --reload --port 8000
```

The application will be available at:
- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## Project Structure

```
ottoneu-projections-football/
├── src/
│   ├── main.py                    # FastAPI app entry point
│   ├── config.py                  # Environment config & Supabase client
│   ├── database/
│   │   ├── schema.sql             # Supabase table definitions
│   │   └── models.py              # Pydantic models for API
│   ├── scrapers/
│   │   ├── base.py                # Abstract base scraper
│   │   ├── espn.py                # ESPN API scraper
│   │   └── aggregator.py          # Combine multiple sources
│   ├── scoring/
│   │   ├── configs.py             # Scoring system definitions
│   │   └── calculator.py          # Point calculation logic
│   ├── api/
│   │   ├── routes.py              # API endpoints
│   │   └── dependencies.py        # Shared dependencies
│   ├── dashboard/
│   │   ├── routes.py              # Dashboard routes
│   │   └── templates/             # HTML templates
│   └── jobs/
│       └── scheduler.py           # Weekly update jobs
├── tests/                         # Test suite
├── scripts/                       # Utility scripts
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment template
└── README.md                      # This file
```

## Development Commands

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/test_scrapers.py -v
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint code
ruff check src/ tests/
```

### Manual Operations

```bash
# Update projections for current week
python -m src.jobs.manual_update --week current

# Seed initial data
python scripts/seed_data.py
```

## API Endpoints

### Projections
- `GET /api/projections` - List projections with filters
  - Query params: `week`, `season`, `position`, `team`, `scoring`, `min_points`, `limit`
- `GET /api/projections/{player_id}` - Single player projection
- `POST /api/projections/update` - Trigger data refresh

### Players
- `GET /api/players` - List players with filters
- `GET /api/players/{id}` - Player details

### Scoring Configurations
- `GET /api/scoring-configs` - List all scoring systems
- `POST /api/scoring-configs` - Create custom scoring config
- `PUT /api/scoring-configs/{id}` - Update config

### Dashboard
- `GET /dashboard` - Main projections view
- `GET /dashboard/player/{id}` - Player detail
- `GET /dashboard/compare` - Compare multiple players

## Database Schema

### Core Tables

**players**: NFL players with position, team, status
**projections**: Raw statistical projections by source, week, season
**scoring_configs**: Scoring system definitions (PPR, Half-PPR, etc.)
**calculated_points**: Pre-calculated fantasy points (optional caching)

See `src/database/schema.sql` for full schema details.

## Implementation Status

- [x] Phase 1: Foundation - Project structure, FastAPI setup, database schema
- [ ] Phase 2: Data Collection - ESPN scraper, player/projection management
- [ ] Phase 3: Scoring System - Point calculator, API endpoints
- [ ] Phase 4: Simple Dashboard - Web interface for viewing projections
- [ ] Phase 5: Automation - Scheduled weekly updates
- [ ] Phase 6: Enhancements - Multiple sources, ML models, advanced features

## Future Features

- Multiple data source aggregation (FantasyPros, etc.)
- Custom projection models using ML
- Historical accuracy tracking
- Player comparison tools
- Lineup optimizer
- DFS (Daily Fantasy Sports) tools
- Advanced dashboard with charts and trends

## Contributing

This is a personal project, but suggestions and feedback are welcome!

## License

MIT License - see LICENSE file for details

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Supabase Documentation](https://supabase.com/docs)
- [ESPN API Python Package](https://github.com/cwendt94/espn-api)
- [nfl_data_py](https://github.com/nflverse/nfl_data_py) (for historical data)

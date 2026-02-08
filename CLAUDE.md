# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a football projections system for Ottoneu fantasy football leagues. Built with FastAPI and Supabase, it stores raw statistical projections and applies different scoring configurations (PPR, Half-PPR, Standard, custom) on top of raw stats.

## Project Status

**Phase 1 Complete: Foundation**
- ✅ Project structure established
- ✅ FastAPI application with health check endpoints
- ✅ Supabase database schema defined
- ✅ Pydantic models for type safety
- ✅ Test framework configured with pytest
- ✅ Virtual environment and dependencies installed

**Next Phase: Data Collection (ESPN scraper, player management)**

## Quick Start

```bash
# Install dependencies
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your Supabase credentials

# Initialize database (run schema.sql in Supabase SQL editor first)
python scripts/setup_db.py

# Run development server
./run.sh
# OR: uvicorn src.main:app --reload --port 8000

# Run tests
pytest
```

## Build and Test Commands

- **Start dev server**: `./run.sh` or `uvicorn src.main:app --reload`
- **Run tests**: `pytest` or `pytest -v` for verbose
- **Test with coverage**: `pytest --cov=src tests/`
- **Format code**: `black src/ tests/`
- **Lint code**: `ruff check src/ tests/`

## Project Architecture

### Tech Stack
- **Backend**: FastAPI (Python 3.9+)
- **Database**: Supabase (PostgreSQL)
- **Data Sources**: ESPN API (via espn-api package)
- **Scheduler**: APScheduler for weekly updates
- **Templates**: Jinja2 for web dashboard

### Directory Structure
```
src/
├── main.py              # FastAPI app entry point
├── config.py            # Environment config & Supabase client
├── database/            # Schema and Pydantic models
├── scrapers/            # Data collection (ESPN, etc.)
├── scoring/             # Point calculation logic
├── api/                 # REST API endpoints
├── dashboard/           # Web UI routes and templates
└── jobs/                # Scheduled update jobs
```

## Database Schema

See `src/database/schema.sql` for the full schema. Core tables:

- **players**: NFL players with position, team, status
- **projections**: Raw statistical projections by source, week, season
- **scoring_configs**: Scoring system definitions (PPR, Half-PPR, Standard)
- **calculated_points**: Pre-calculated fantasy points (optional caching)

## Data Sources

- **ESPN Fantasy API**: Primary source via `espn-api` Python package
- **Future**: FantasyPros, nfl_data_py for historical data

## Development Notes

- Environment variables stored in `.env` (not committed to git)
- All database operations use Supabase client from `src/config.py`
- API auto-documentation available at `/docs` and `/redoc`
- Tests use dummy credentials (see `tests/conftest.py`)

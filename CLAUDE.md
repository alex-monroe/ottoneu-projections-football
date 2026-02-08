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

**Phase 2 Complete: Data Collection**
- ✅ Data loaders for NFLVerse (nfl-data-py) and FFDP CSV sources
- ✅ Automatic fallback from primary to backup source
- ✅ Column mapping from various data sources to database schema
- ✅ Service layer for data import orchestration
- ✅ API endpoints for triggering data imports
- ✅ Comprehensive test suite (50 tests passing)

**Phase 3 Complete: Scoring System**
- ✅ Fantasy points calculator with configurable scoring formats
- ✅ Standard scoring configs (PPR, Half-PPR, Standard)
- ✅ Projections API with filtering, sorting, pagination
- ✅ Support for custom scoring configurations

**Phase 4 Complete: Dashboard**
- ✅ Web UI routes for viewing projections
- ✅ Jinja2 templates (base, projections, player detail, error pages)
- ✅ Interactive filters (season, week, position, scoring format)
- ✅ Sortable/filterable tables
- ✅ Player detail pages

**Phase 5 Complete: Automated Jobs**
- ✅ APScheduler integration for automated data imports
- ✅ Weekly cron job (Tuesdays 8:00 AM UTC)
- ✅ Manual job triggers via API
- ✅ Job management endpoints

**Current Test Suite: 77 tests passing**

**Project Status: Production Ready**

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
- **Data Sources**: NFLVerse (nfl-data-py), FFDP CSV files
- **Data Processing**: pandas for data transformation
- **Scheduler**: APScheduler for automated weekly imports
- **Templates**: Jinja2 for web dashboard UI

### Directory Structure
```
src/
├── main.py              # FastAPI app entry point
├── config.py            # Environment config & Supabase client
├── database/            # Schema and Pydantic models
├── loaders/             # Data loading from various sources
│   ├── base.py          # Base loader interface
│   ├── nflverse.py      # NFLVerse (primary source)
│   ├── ffdp.py          # Fantasy Data Pros (backup)
│   ├── mapper.py        # Column mapping logic
│   ├── service.py       # Import orchestration
│   └── exceptions.py    # Custom exceptions
├── scoring/             # Point calculation logic
│   └── calculator.py    # Fantasy points calculator
├── api/                 # REST API endpoints
│   ├── loaders.py       # Data import endpoints
│   ├── projections.py   # Projections query endpoints
│   └── jobs.py          # Job management endpoints
├── dashboard/           # Web UI routes and templates
│   ├── routes.py        # Dashboard routes
│   └── templates/       # Jinja2 HTML templates
└── jobs/                # Scheduled update jobs
    └── scheduler.py     # APScheduler job definitions
```

## Database Schema

See `src/database/schema.sql` for the full schema. Core tables:

- **players**: NFL players with position, team, status
- **projections**: Raw statistical projections by source, week, season
- **scoring_configs**: Scoring system definitions (PPR, Half-PPR, Standard)
- **calculated_points**: Pre-calculated fantasy points (optional caching)

## Data Sources

- **NFLVerse (nfl-data-py)**: Primary source - historical NFL player statistics
- **Fantasy Football Data Pros (FFDP)**: Backup CSV source from GitHub
- **Automatic Fallback**: System tries primary source first, falls back to backup if unavailable
- **Data Mapping**: Automatic column mapping from source formats to our database schema

## Pull Request Workflow (Required)

**All changes to the `main` branch must go through pull requests. Direct pushes are blocked.**

### Local Development Workflow

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make changes and run local checks**
   ```bash
   # Run tests
   pytest

   # Check formatting
   black src/ tests/

   # Run linting
   ruff check src/ tests/ --fix

   # Verify build
   python -c "from src.main import app; print('✓ OK')"
   ```

3. **Commit and push**
   ```bash
   git add .
   git commit -m "Brief description of changes"
   git push -u origin feature/your-feature-name
   ```

4. **Create Pull Request on GitHub**
   - Fill out the PR template completely
   - Wait for automated checks to pass

### Pre-Commit Hooks (Recommended)

Install pre-commit hooks to catch issues before pushing:

```bash
pip install pre-commit
pre-commit install
```

This automatically runs Black formatting and Ruff linting on every commit.

### CI/CD Pipeline

When you create a PR to `main`, GitHub Actions automatically runs:

- ✅ **Tests**: All 77 tests must pass
- ✅ **Linting**: Ruff checks for code quality issues
- ✅ **Formatting**: Black verifies consistent code style
- ✅ **Build Check**: Verifies application imports successfully

All checks must pass before merging. Check results typically complete in 2-3 minutes.

### Deployment

After merging a PR to `main`, deploy to Fly.io:

```bash
flyctl deploy
```

The deployment process:
1. Builds Docker image from Dockerfile
2. Deploys to Fly.io with health check verification
3. Deployment completes in ~2-3 minutes

See `fly.toml` for deployment configuration.

### Branch Protection

The `main` branch is protected with the following rules:

- Cannot push directly (must use PRs)
- All CI checks must pass
- Branch must be up to date before merging

See `CONTRIBUTING.md` for complete workflow details.

## Development Notes

- Environment variables stored in `.env` (not committed to git)
- All database operations use Supabase client from `src/config.py`
- API auto-documentation available at `/docs` and `/redoc`
- Tests use dummy credentials (see `tests/conftest.py`)

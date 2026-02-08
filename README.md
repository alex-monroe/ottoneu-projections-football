# NFL Fantasy Football Projections System

A FastAPI-based system for managing NFL fantasy football projections with support for multiple scoring configurations.

## Project Status

### ✅ Phase 1: Foundation (Complete)
- FastAPI application structure
- Supabase database integration
- Pydantic models for type safety
- Test framework with pytest

### ✅ Phase 2: Data Collection (Complete)
- NFLVerse data loader (primary source)
- Fantasy Football Data Pros CSV loader (backup)
- Automatic fallback between sources
- Column mapping and data transformation
- REST API endpoints for data import
- 50 comprehensive tests (100% passing)

### ✅ Phase 3: Scoring System (Complete)
- Fantasy points calculator with configurable scoring
- Support for PPR, Half-PPR, Standard scoring formats
- Projections API with filtering, sorting, and pagination
- 60 comprehensive tests (100% passing)

### ✅ Phase 4: Dashboard (Complete)
- Web UI for viewing projections with filters
- Player detail pages with weekly stats
- Sortable/filterable tables with Tailwind CSS
- Error handling and responsive design
- 64 comprehensive tests (100% passing)

### ✅ Phase 5: Automation (Complete)
- Scheduled weekly data imports using APScheduler
- Automatic Tuesday 8:00 AM UTC imports
- Job execution tracking in database
- Job management API endpoints (status, trigger, history)
- 82 comprehensive tests (100% passing)

### 📋 Phase 6: Advanced Features (Planned)
- Custom projection models
- Player news integration
- Trade analyzer

## Quick Start

### Installation

```bash
# Clone the repository
cd ottoneu-projections-football

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your Supabase credentials
```

### Database Setup

1. Create a Supabase project at https://supabase.com
2. Run `src/database/schema.sql` in the Supabase SQL editor
3. Copy your project URL and anon key to `.env`

### Run the Application

```bash
# Start the development server
uvicorn src.main:app --reload

# Or use the convenience script
./run.sh
```

The API will be available at:
- http://localhost:8000 - API root
- http://localhost:8000/docs - Swagger UI documentation
- http://localhost:8000/redoc - ReDoc documentation

### Import Data

```bash
# Import week 1 of the 2023 season
curl -X POST "http://localhost:8000/api/loaders/import/weekly" \
  -H "Content-Type: application/json" \
  -d '{"year": 2023, "week": 1, "source": "nflverse"}'

# Import multiple weeks
curl -X POST "http://localhost:8000/api/loaders/import/season?year=2023&start_week=1&end_week=4"

# Check what data is available
curl "http://localhost:8000/api/loaders/available-data"

# Update the import ledger to see what's been imported
./update-ledger.sh
cat IMPORT_LEDGER.md
```

See [DATA_IMPORT.md](DATA_IMPORT.md) for detailed import instructions.

**Import Ledger:** Track import status with `IMPORT_LEDGER.md` - shows which weeks are imported and which are pending. Update it anytime with `./update-ledger.sh`.

### Get Projections with Fantasy Points

```bash
# Seed standard scoring configurations (PPR, Half-PPR, Standard)
python scripts/seed_scoring_configs.py

# Get top 20 players for week 1 (PPR scoring)
curl "http://localhost:8000/api/projections?season=2023&week=1&scoring=PPR%20(Point%20Per%20Reception)&limit=20"

# Get top 10 running backs (Half-PPR)
curl "http://localhost:8000/api/projections?season=2023&week=1&scoring=Half-PPR&position=RB&limit=10"
```

See [SCORING_GUIDE.md](SCORING_GUIDE.md) for detailed scoring documentation.

### Automated Jobs (Phase 5)

The application includes automated weekly data imports:

```bash
# Check job status (next run time, last execution)
curl "http://localhost:8000/api/jobs/status"

# View job execution history
curl "http://localhost:8000/api/jobs/history?job_id=weekly_import&limit=5"

# Manually trigger an import
curl -X POST "http://localhost:8000/api/jobs/trigger" \
  -H "Content-Type: application/json" \
  -d '{"year": 2023, "week": 1, "source": "nflverse"}'
```

**Automated Schedule:**
- **Every Tuesday at 8:00 AM UTC** - Automatic import of previous week's data
- Job execution tracked in `job_executions` table
- Automatic fallback to backup source if primary fails

See [AUTOMATION_GUIDE.md](AUTOMATION_GUIDE.md) for detailed automation documentation.

### Run Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/loaders/test_mapper.py -v

# Run with coverage
pytest --cov=src tests/
```

## Project Structure

```
ottoneu-projections-football/
├── src/
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Environment configuration
│   ├── database/            # Database schema and models
│   │   ├── schema.sql       # Supabase schema definition
│   │   └── models.py        # Pydantic models
│   ├── loaders/             # Data loading from various sources
│   │   ├── base.py          # Abstract base loader
│   │   ├── nflverse.py      # NFLVerse loader (primary)
│   │   ├── ffdp.py          # FFDP CSV loader (backup)
│   │   ├── mapper.py        # Column mapping logic
│   │   ├── service.py       # Import orchestration
│   │   └── exceptions.py    # Custom exceptions
│   ├── api/                 # REST API endpoints
│   │   ├── loaders.py       # Data import endpoints
│   │   ├── projections.py   # Projections with scoring
│   │   └── jobs.py          # Job management endpoints
│   ├── scoring/             # Point calculation (Phase 3)
│   ├── dashboard/           # Web UI (Phase 4)
│   └── jobs/                # Scheduled tasks (Phase 5)
│       └── scheduler.py     # APScheduler job management
├── tests/                   # Test suite
│   ├── loaders/             # Loader tests
│   └── api/                 # API tests
├── .env.example             # Example environment variables
├── requirements.txt         # Python dependencies
├── pytest.ini               # Pytest configuration
├── DATA_IMPORT.md           # Data import guide
├── PHASE2_SUMMARY.md        # Phase 2 completion summary
└── README.md                # This file
```

## Data Sources

### NFLVerse (Primary)
- **Library**: nfl-data-py
- **Type**: Historical NFL player statistics (1999-present)
- **Advantages**: Well-maintained, structured data, active community
- **Authentication**: None required

### Fantasy Football Data Pros (Backup)
- **Source**: GitHub CSV files
- **Type**: Historical stats in CSV format
- **Advantages**: No library dependency, simple HTTP
- **Fallback**: Used automatically if NFLVerse fails

## API Endpoints

### Health Check
- `GET /` - API health check
- `GET /health` - Detailed health status

### Data Loading
- `POST /api/loaders/import/weekly` - Import single week
- `POST /api/loaders/import/season` - Import multiple weeks
- `GET /api/loaders/sources` - List available sources
- `GET /api/loaders/available-data` - Summary of imported data

### Projections
- `GET /api/projections` - Get projections with fantasy points (supports filtering, sorting)
- `GET /api/projections/{player_id}` - Get single player projection

### Job Management (Phase 5)
- `GET /api/jobs/status` - Get scheduled job status and next run times
- `POST /api/jobs/trigger` - Manually trigger a data import
- `GET /api/jobs/history` - View job execution history
- `GET /api/jobs/history/{execution_id}` - Get specific execution details

### Dashboard
- `GET /dashboard` - Web UI for viewing projections
- `GET /dashboard/player/{player_id}` - Player detail page

See interactive API docs at http://localhost:8000/docs

## Database Schema

### Core Tables

**players**
- Player information (name, position, team, status)
- Unique constraint on (name, position)

**projections**
- Raw statistical projections by source/week/season
- Passing, rushing, receiving stats
- Unique constraint on (player_id, week, season, source)

**scoring_configs**
- Fantasy scoring configurations (PPR, Standard, etc.)
- Point values for each stat category

**job_executions** (Phase 5)
- Tracks all scheduled and manual job executions
- Logs success/failure status and execution results
- Indexed by job_id, status, and executed_at

**calculated_points** (future)
- Pre-calculated fantasy points cache
- Combines projections + scoring configs

## Development

### Code Style

```bash
# Format code
black src/ tests/

# Lint code
ruff check src/ tests/
```

### Testing

All features have comprehensive test coverage:
- **Unit tests**: Individual components
- **Integration tests**: API endpoints
- **Mock fixtures**: External dependencies
- **Current status**: 64/64 tests passing

### Environment Variables

Required in `.env`:
```
SUPABASE_URL=your-project-url
SUPABASE_KEY=your-anon-key
ENVIRONMENT=development
```

## Tech Stack

- **Backend**: FastAPI 0.104.1
- **Database**: Supabase (PostgreSQL)
- **Data Processing**: pandas 2.1.3
- **Data Sources**: nfl-data-py 0.3.2
- **Testing**: pytest 7.4.3
- **Python**: 3.9+

## Deployment

This project is deployed to **Fly.io** using Docker.

Quick deploy:
```bash
# First time setup
flyctl launch

# Deploy updates
flyctl deploy
```

Configuration:
- See `fly.toml` for Fly.io configuration
- See `Dockerfile` for build configuration
- Set secrets: `flyctl secrets set SUPABASE_URL=... SUPABASE_KEY=...`

Alternative platforms: See [DEPLOYMENT.md](DEPLOYMENT.md) for Railway.app, Render.com, etc.

## Contributing

**All changes must go through pull requests with automated quality checks.**

### Quick Start for Contributors

1. **Fork and clone the repository**
2. **Create a feature branch**: `git checkout -b feature/your-feature-name`
3. **Install pre-commit hooks** (optional but recommended):
   ```bash
   pip install pre-commit
   pre-commit install
   ```
4. **Make your changes** following our code quality standards
5. **Run local checks before pushing**:
   ```bash
   pytest                    # All 82 tests must pass
   black src/ tests/         # Format code
   ruff check src/ tests/    # Lint code
   ```
6. **Push and create PR**: GitHub Actions will automatically run CI checks
7. **Merge when ready**: Deployment to Fly.io happens automatically

### CI/CD Pipeline

Every pull request automatically runs:
- ✅ Tests (pytest with coverage)
- ✅ Linting (Ruff)
- ✅ Formatting (Black)
- ✅ Build verification

After merging, GitHub Actions automatically deploys to Fly.io (~2-3 minutes).

**See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed workflow, code standards, and testing requirements.**

## License

This project is for educational purposes.

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Supabase Documentation](https://supabase.com/docs)
- [NFLVerse/nfl_data_py](https://github.com/nflverse/nfl_data_py)
- [Fantasy Data Pros](https://github.com/fantasydatapros/data)

## Support

For questions or issues:
1. Check [DATA_IMPORT.md](DATA_IMPORT.md) for data import help
2. Review [PHASE2_SUMMARY.md](PHASE2_SUMMARY.md) for implementation details
3. See API docs at http://localhost:8000/docs
4. Open an issue on GitHub

---

**Current Version**: Phase 4 Complete
**Last Updated**: 2026-02-07
**Status**: ✅ Ready for Phase 5 (Automation)

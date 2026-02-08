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

### 🚧 Phase 3: Scoring System (Next)
- Calculate fantasy points from raw stats
- Support PPR, Half-PPR, Standard scoring
- Custom scoring configurations

### 📋 Phase 4: Dashboard (Planned)
- Web UI for viewing projections
- Player comparison tools
- Sortable/filterable tables

### 📋 Phase 5: Automation (Planned)
- Scheduled weekly data updates
- Job monitoring and logging

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
```

See [DATA_IMPORT.md](DATA_IMPORT.md) for detailed import instructions.

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
│   │   └── loaders.py       # Data import endpoints
│   ├── scoring/             # Point calculation (Phase 3)
│   ├── dashboard/           # Web UI (Phase 4)
│   └── jobs/                # Scheduled tasks (Phase 5)
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
- **Current status**: 50/50 tests passing

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

## Contributing

This is a personal project, but feel free to:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `pytest`
5. Submit a pull request

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

**Current Version**: Phase 2 Complete
**Last Updated**: 2026-02-07
**Status**: ✅ Ready for Phase 3 (Scoring System)

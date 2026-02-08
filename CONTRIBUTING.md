# Contributing to NFL Projections System

Thank you for your interest in contributing! This document provides guidelines and workflows for contributing to this project.

## Table of Contents

- [Development Environment Setup](#development-environment-setup)
- [Pull Request Workflow](#pull-request-workflow)
- [Code Quality Standards](#code-quality-standards)
- [Testing Requirements](#testing-requirements)
- [Commit Guidelines](#commit-guidelines)
- [Project Structure](#project-structure)
- [Getting Help](#getting-help)

---

## Development Environment Setup

### Prerequisites

- Python 3.9 or higher
- Git
- A Supabase account (for local development with real database)

### Initial Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/ottoneu-projections-football.git
   cd ottoneu-projections-football
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your Supabase credentials
   ```

5. **Install pre-commit hooks** (recommended)
   ```bash
   pip install pre-commit
   pre-commit install
   ```

6. **Verify setup**
   ```bash
   pytest  # Should see 77 tests passing
   ./run.sh  # Start dev server at http://localhost:8000
   ```

---

## Pull Request Workflow

All changes must go through pull requests. Direct pushes to `main` are blocked.

### Step-by-Step Process

1. **Create a feature branch**
   ```bash
   git checkout main
   git pull origin main
   git checkout -b feature/your-feature-name
   ```

   **Branch naming conventions:**
   - `feature/` - New features
   - `fix/` - Bug fixes
   - `refactor/` - Code refactoring
   - `docs/` - Documentation updates
   - `test/` - Test improvements

2. **Make your changes**
   - Write code following our [Code Quality Standards](#code-quality-standards)
   - Add/update tests for your changes
   - Update documentation if needed

3. **Run local checks** (before committing)
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

   **Note:** If you installed pre-commit hooks, formatting and linting run automatically on `git commit`.

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "Brief description of changes"
   ```

   See [Commit Guidelines](#commit-guidelines) for commit message standards.

5. **Push to GitHub**
   ```bash
   git push -u origin feature/your-feature-name
   ```

6. **Create Pull Request**
   - Go to GitHub repository
   - Click "Compare & pull request"
   - Fill out the PR template completely
   - Submit the PR

7. **Wait for CI checks**
   - GitHub Actions will automatically run:
     - ✅ Tests (82 tests must pass)
     - ✅ Linting (Ruff)
     - ✅ Formatting (Black)
     - ✅ Build verification
   - All checks must pass before merging
   - Check results usually complete in 2-3 minutes

8. **Merge when ready**
   - Once all checks pass, click "Merge pull request"
   - GitHub Actions automatically deploys to Fly.io
   - Deployment takes ~2-3 minutes
   - Monitor deployment: `flyctl status` or check GitHub Actions tab

---

## Code Quality Standards

### Formatting

We use **Black** for code formatting:
```bash
black src/ tests/
```

- Line length: 88 characters (Black default)
- Automatically formats on commit (if using pre-commit hooks)

### Linting

We use **Ruff** for linting:
```bash
ruff check src/ tests/ --fix
```

- Fix auto-fixable issues with `--fix`
- Manually fix remaining issues

### Type Hints

- Add type hints to all function signatures
- Use `Optional[Type]` for nullable parameters
- Import types from `typing` module

Example:
```python
from typing import Optional, List
from decimal import Decimal

def calculate_points(
    pass_yds: Optional[int],
    scoring_config: dict
) -> Decimal:
    """Calculate fantasy points."""
    ...
```

### Documentation

- Add docstrings to all public functions/classes
- Use Google-style docstrings
- Document complex logic with inline comments

Example:
```python
def load_projections(season: int, week: Optional[int] = None) -> pd.DataFrame:
    """Load projections from NFLVerse.

    Args:
        season: NFL season year (e.g., 2024)
        week: Optional week number (1-18). If None, loads all weeks.

    Returns:
        DataFrame with player projections

    Raises:
        DataSourceError: If data cannot be loaded
    """
    ...
```

---

## Testing Requirements

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_loaders.py

# Run specific test
pytest tests/test_loaders.py::test_nflverse_load
```

### Writing Tests

**Required for all new code:**
- Unit tests for new functions/classes
- Integration tests for API endpoints
- Mock external dependencies (Supabase, nfl-data-py, HTTP requests)

**Test structure:**
```python
# tests/test_mymodule.py
import pytest
from unittest.mock import MagicMock
from src.mymodule import my_function

def test_my_function_success():
    """Test successful case."""
    result = my_function(valid_input)
    assert result == expected_output

def test_my_function_error():
    """Test error handling."""
    with pytest.raises(ValueError):
        my_function(invalid_input)
```

**Use fixtures from `tests/conftest.py`:**
```python
def test_api_endpoint(client, mock_supabase):
    """Test API with mocked dependencies."""
    response = client.get("/api/projections")
    assert response.status_code == 200
```

### Test Coverage

- Aim for >80% coverage on new code
- 100% coverage on critical paths (scoring, data import)
- Coverage reports generated in `htmlcov/` directory

---

## Commit Guidelines

### Commit Message Format

```
Brief summary (50 chars or less)

More detailed explanation if needed. Wrap at 72 characters.
Explain what changed and why, not how (code shows how).

- Bullet points are okay
- Use present tense ("Add feature" not "Added feature")
- Reference issues with #issue-number
```

### Good Examples

```
Add filtering by position to projections API

Implements position filter query parameter for /api/projections
endpoint. Filters applied after database query to maintain
compatibility with existing caching.

Closes #42
```

```
Fix scoring calculation for negative yardage

Previous implementation didn't handle negative rushing yards
correctly. Now treats negative yards as 0 for scoring purposes
to match ESPN/Yahoo behavior.
```

### Bad Examples

```
Fixed stuff  # Too vague
```

```
Updated src/api/projections.py and src/scoring/calculator.py and tests/test_scoring.py  # Describes files, not changes
```

```
WIP  # Never commit work-in-progress to PR
```

---

## Project Structure

### Directory Layout

```
src/
├── main.py              # FastAPI app entry point
├── config.py            # Environment config & Supabase client
├── database/            # Database schema and models
│   ├── schema.sql       # PostgreSQL schema
│   └── models.py        # Pydantic models
├── loaders/             # Data loading from sources
│   ├── base.py          # Base loader interface
│   ├── nflverse.py      # NFLVerse loader (primary)
│   ├── ffdp.py          # FFDP loader (backup)
│   ├── mapper.py        # Column mapping logic
│   ├── service.py       # Import orchestration
│   └── exceptions.py    # Custom exceptions
├── scoring/             # Fantasy points calculation
│   └── calculator.py    # Calculator with scoring configs
├── api/                 # REST API endpoints
│   ├── loaders.py       # Data import endpoints
│   ├── projections.py   # Projections query endpoints
│   └── jobs.py          # Job management endpoints
├── dashboard/           # Web UI
│   ├── routes.py        # Dashboard routes
│   └── templates/       # Jinja2 templates
└── jobs/                # Scheduled tasks
    └── scheduler.py     # APScheduler job definitions

tests/
├── conftest.py          # Shared fixtures
├── test_*.py            # Test files (mirror src/ structure)
```

### Adding New Modules

1. Create module in appropriate `src/` subdirectory
2. Create corresponding test file in `tests/`
3. Update `src/main.py` if adding API routes
4. Update `CLAUDE.md` if changing architecture

### Common Patterns

**Service Layer Pattern:**
```python
# src/mymodule/service.py
class MyService:
    def __init__(self, supabase_client):
        self.supabase = supabase_client

    def do_something(self) -> Result:
        # Business logic here
        ...
```

**Mapper Pattern:**
```python
# src/mymodule/mapper.py
def map_to_schema(source_data: dict) -> dict:
    """Transform source format to database schema."""
    return {
        'db_field': source_data.get('source_field'),
        ...
    }
```

**Calculator Pattern:**
```python
# src/scoring/calculator.py
class FantasyPointsCalculator:
    def calculate(self, stats: dict, config: dict) -> Decimal:
        """Calculate points from stats and config."""
        ...
```

---

## Getting Help

### Questions?

- Check existing documentation:
  - `README.md` - Quick start guide
  - `CLAUDE.md` - Architecture overview
  - `DATA_IMPORT.md` - Data import guide
  - `SCORING_GUIDE.md` - Scoring system guide

- Open an issue on GitHub with the `question` label

### Found a Bug?

1. Check if issue already exists
2. If not, create new issue with:
   - Clear title
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (Python version, OS)

### Want to Propose a Feature?

1. Open an issue with the `enhancement` label
2. Describe the feature and use case
3. Wait for feedback before implementing
4. Once approved, follow the PR workflow above

---

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Supabase Python Client](https://github.com/supabase-community/supabase-py)
- [NFLVerse Data](https://github.com/nflverse/nflverse-data)
- [pytest Documentation](https://docs.pytest.org/)

---

Thank you for contributing! 🏈

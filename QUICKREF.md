# Quick Reference

Quick command reference for common development tasks.

## Setup Commands

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate              # macOS/Linux
venv\Scripts\activate                 # Windows

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env
# Then edit .env with your Supabase credentials

# Initialize database (after running schema.sql in Supabase)
python scripts/setup_db.py

# Verify setup
python scripts/verify_setup.py
```

## Development Commands

```bash
# Start development server
./run.sh                              # Convenience script
# OR
uvicorn src.main:app --reload         # Direct command
uvicorn src.main:app --reload --port 8080  # Custom port

# Run with specific host
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

## Testing Commands

```bash
# Run all tests
pytest

# Verbose output
pytest -v

# Run specific test file
pytest tests/test_api.py -v

# Run tests with coverage
pytest --cov=src tests/

# Generate HTML coverage report
pytest --cov=src --cov-report=html tests/
# Open htmlcov/index.html in browser

# Run tests matching pattern
pytest -k "test_health"

# Stop on first failure
pytest -x
```

## Code Quality Commands

```bash
# Format code with Black
black src/ tests/

# Check formatting without making changes
black src/ tests/ --check

# Lint code with Ruff
ruff check src/ tests/

# Auto-fix linting issues
ruff check src/ tests/ --fix

# Type checking (if mypy is installed)
mypy src/
```

## Database Commands

```bash
# Initialize database with default scoring configs
python scripts/setup_db.py

# Verify database connection
python -c "from src.config import get_supabase_client; print(get_supabase_client())"
```

## API Access

Once the server is running (on http://localhost:8000):

```bash
# Health check
curl http://localhost:8000/health

# Interactive API docs
open http://localhost:8000/docs          # macOS
xdg-open http://localhost:8000/docs      # Linux
start http://localhost:8000/docs         # Windows

# Alternative docs (ReDoc)
open http://localhost:8000/redoc

# Get OpenAPI schema
curl http://localhost:8000/openapi.json | jq
```

## Git Commands

```bash
# Check status
git status

# Stage all changes
git add .

# Commit changes
git commit -m "Your message"

# View commit log
git log --oneline

# Create new branch
git checkout -b feature/new-feature

# Push to remote
git push origin main
```

## Virtual Environment Management

```bash
# Activate environment
source venv/bin/activate              # macOS/Linux
venv\Scripts\activate                 # Windows

# Deactivate environment
deactivate

# Recreate virtual environment
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Update requirements file (after installing new packages)
pip freeze > requirements.txt
```

## Dependency Management

```bash
# Install new package
pip install package-name

# Install with specific version
pip install package-name==1.2.3

# Update package
pip install --upgrade package-name

# List installed packages
pip list

# Show package details
pip show package-name

# Update all packages (be careful!)
pip list --outdated
pip install --upgrade <package-name>
```

## Troubleshooting Commands

```bash
# Clear Python cache
find . -type d -name "__pycache__" -exec rm -r {} +
find . -type f -name "*.pyc" -delete

# Clear pytest cache
rm -rf .pytest_cache

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check Python version
python --version

# Check pip version
pip --version

# List what port 8000 is using
lsof -i :8000                         # macOS/Linux
netstat -ano | findstr :8000          # Windows

# Kill process on port 8000
kill $(lsof -t -i:8000)              # macOS/Linux
```

## Development Workflow

```bash
# 1. Start development session
source venv/bin/activate

# 2. Create feature branch
git checkout -b feature/my-feature

# 3. Make changes to code

# 4. Run tests
pytest -v

# 5. Format and lint
black src/ tests/
ruff check src/ tests/

# 6. Commit changes
git add .
git commit -m "Add new feature"

# 7. Push changes
git push origin feature/my-feature

# 8. Deactivate when done
deactivate
```

## Environment Variables

Required in `.env` file:

```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
ENVIRONMENT=development
ESPN_LEAGUE_ID=                       # Optional
```

## Project URLs

- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## Common File Locations

```
Configuration:
  .env                          Environment variables
  requirements.txt              Python dependencies
  pytest.ini                    Test configuration

Code:
  src/main.py                   FastAPI app entry point
  src/config.py                 Settings and Supabase client
  src/database/schema.sql       Database schema
  src/database/models.py        Pydantic models

Scripts:
  scripts/setup_db.py           Initialize database
  scripts/verify_setup.py       Verify setup
  run.sh                        Start dev server

Tests:
  tests/conftest.py             Test configuration
  tests/test_api.py             API tests

Documentation:
  README.md                     Project overview
  SETUP.md                      Setup guide
  STATUS.md                     Implementation status
  QUICKREF.md                   This file
```

## Keyboard Shortcuts (in terminal)

```
Ctrl+C                          Stop running server
Ctrl+D                          Exit Python shell
Ctrl+L                          Clear terminal
Ctrl+R                          Search command history
```

## Next Phase: Data Collection

When ready for Phase 2:

```bash
# Create ESPN scraper
touch src/scrapers/base.py
touch src/scrapers/espn.py

# Create tests
touch tests/test_scrapers.py

# Run tests
pytest tests/test_scrapers.py -v
```

---

**Tip**: Keep this file open in a split pane for quick reference while developing!

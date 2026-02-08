# Setup Guide

Complete setup guide for the NFL Fantasy Football Projections system.

## Prerequisites

- Python 3.9 or higher
- A [Supabase](https://supabase.com) account (free tier works fine)
- Git (for version control)

## Step-by-Step Setup

### 1. Install Python Dependencies

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install all required packages
pip install -r requirements.txt
```

This will install:
- FastAPI (web framework)
- Uvicorn (ASGI server)
- Supabase client
- ESPN API client
- Pydantic (data validation)
- Pytest (testing)
- And more...

### 2. Set Up Supabase

#### Create a Supabase Project

1. Go to [supabase.com](https://supabase.com)
2. Sign in or create an account
3. Click "New Project"
4. Fill in project details:
   - **Name**: `nfl-projections` (or your choice)
   - **Database Password**: Generate a strong password (save it!)
   - **Region**: Choose closest to you
5. Wait for project to be created (~2 minutes)

#### Get Your Credentials

1. In your Supabase project dashboard, go to **Settings → API**
2. Copy two values:
   - **Project URL** (under "Project URL")
   - **anon/public key** (under "Project API keys")

#### Create the Database Schema

1. In your Supabase dashboard, go to **SQL Editor**
2. Click "New Query"
3. Open the file `src/database/schema.sql` in your code editor
4. Copy all the SQL code
5. Paste it into the Supabase SQL editor
6. Click "Run" or press Cmd+Enter / Ctrl+Enter
7. You should see "Success. No rows returned" - this is correct!

### 3. Configure Environment Variables

```bash
# Copy the example file
cp .env.example .env

# Edit the .env file with your credentials
nano .env  # or use your preferred editor
```

Update these values in `.env`:
```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-key-here
ENVIRONMENT=development
```

**Security Note**: Never commit your `.env` file to git. It's already in `.gitignore`.

### 4. Initialize Database with Default Data

```bash
python scripts/setup_db.py
```

This will:
- Insert default scoring configurations (PPR, Half-PPR, Standard)
- Verify database connection works

Expected output:
```
✓ Created/updated scoring config: PPR
✓ Created/updated scoring config: Half-PPR
✓ Created/updated scoring config: Standard
✓ Database setup complete!
```

### 5. Verify Setup

Run the verification script to ensure everything is configured correctly:

```bash
python scripts/verify_setup.py
```

All checks should pass:
```
✓ PASS: Dependencies
✓ PASS: Environment Variables
✓ PASS: Database Schema
✓ PASS: Tests
```

### 6. Run the Application

```bash
# Option 1: Use the convenience script
./run.sh

# Option 2: Run uvicorn directly
uvicorn src.main:app --reload --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 7. Test the API

Open your browser and visit:

- **Interactive API docs**: http://localhost:8000/docs
- **Alternative docs**: http://localhost:8000/redoc
- **Health check**: http://localhost:8000/health

You should see a JSON response:
```json
{
  "status": "healthy",
  "environment": "development",
  "timestamp": "2026-02-07T12:00:00.000000"
}
```

## Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=src tests/

# Run specific test file
pytest tests/test_api.py -v
```

## Troubleshooting

### Issue: "Field required" error for Supabase credentials

**Solution**: Make sure you have a `.env` file in the root directory with valid credentials.

```bash
# Check if .env exists
ls -la .env

# If missing, copy from example
cp .env.example .env
```

### Issue: Can't connect to Supabase

**Solutions**:
1. Verify your `SUPABASE_URL` and `SUPABASE_KEY` are correct
2. Check if your Supabase project is active (not paused)
3. Ensure you're using the **anon/public** key, not the service_role key
4. Try pinging the URL: `curl https://your-project.supabase.co`

### Issue: Database tables don't exist

**Solution**: Make sure you ran the schema.sql in Supabase SQL editor:
1. Go to Supabase dashboard → SQL Editor
2. Paste contents of `src/database/schema.sql`
3. Click Run

### Issue: Tests failing

**Solution**:
```bash
# Clear any cached settings
rm -rf __pycache__ .pytest_cache
source venv/bin/activate
pytest tests/ -v
```

### Issue: Port 8000 already in use

**Solution**: Either:
1. Stop the other process using port 8000
2. Use a different port: `uvicorn src.main:app --reload --port 8080`

### Issue: Import errors

**Solution**: Make sure virtual environment is activated:
```bash
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Next Steps

Now that your setup is complete, you can:

1. **Phase 2**: Implement ESPN scraper to fetch player projections
2. **Phase 3**: Build scoring calculator and API endpoints
3. **Phase 4**: Create web dashboard for viewing projections
4. **Phase 5**: Add scheduled weekly updates

See the main `README.md` for the full implementation roadmap.

## Getting Help

- Check `CLAUDE.md` for project-specific development notes
- Review `README.md` for architecture details
- Examine `src/database/schema.sql` for database structure
- Browse the interactive API docs at `/docs` when the server is running

## Development Workflow

```bash
# 1. Activate virtual environment
source venv/bin/activate

# 2. Make code changes

# 3. Run tests
pytest

# 4. Format code
black src/ tests/

# 5. Check linting
ruff check src/ tests/

# 6. Test the API
./run.sh
# Visit http://localhost:8000/docs

# 7. Commit changes
git add .
git commit -m "Your commit message"
```

Happy coding! 🏈

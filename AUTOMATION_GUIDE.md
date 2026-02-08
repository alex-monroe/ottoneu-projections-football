# Automation Guide

This guide explains the automated job scheduling system for NFL Fantasy Football Projections.

## Overview

Phase 5 implements automated weekly data imports using APScheduler. The system:
- **Automatically imports** NFL player data every Tuesday at 8:00 AM UTC
- **Tracks job execution** history in the database
- **Provides API endpoints** for manual triggers and monitoring
- **Integrates with FastAPI** lifecycle management

## Scheduled Jobs

### Weekly Import Job

**Schedule**: Every Tuesday at 8:00 AM UTC  
**Job ID**: `weekly_import`  
**Purpose**: Automatically import previous week's NFL data

The job:
1. Determines the current NFL season and week
2. Imports data from NFLVerse (primary source)
3. Falls back to FFDP if NFLVerse fails
4. Logs execution results to `job_executions` table

**Why Tuesday?**
- NFL games occur Sunday/Monday
- Data is typically available by Tuesday morning
- Gives time for stat corrections

### Week Calculation Logic

The scheduler uses a simplified week calculation:
- **Off-season** (Jan-Aug): Imports last year's week 18
- **Regular season** (Sep-Dec): Estimates current week based on date

**Note**: Production systems should use an actual NFL schedule API for accurate week numbers.

## Job Monitoring

### Database Tracking

All job executions are logged in the `job_executions` table:

```sql
CREATE TABLE job_executions (
  id UUID PRIMARY KEY,
  job_id TEXT NOT NULL,           -- 'weekly_import', 'manual_import'
  status TEXT NOT NULL,            -- 'success', 'failed', 'error'
  executed_at TIMESTAMP NOT NULL,
  result JSONB,                    -- Execution details
  season INTEGER,
  week INTEGER,
  created_at TIMESTAMP DEFAULT NOW()
);
```

**Status Values**:
- `success`: Job completed successfully
- `failed`: Job completed but had errors (e.g., no data found)
- `error`: Job threw an exception

**Result JSONB**: Contains import statistics:
```json
{
  "success": true,
  "players_imported": 50,
  "players_updated": 10,
  "projections_imported": 100,
  "projections_updated": 20,
  "source": "nflverse",
  "year": 2023,
  "week": 1,
  "errors": []
}
```

## API Endpoints

### Get Job Status

Get information about all scheduled jobs including next run time.

```bash
GET /api/jobs/status
```

**Response**:
```json
[
  {
    "job_id": "weekly_import",
    "name": "Weekly NFL Data Import",
    "next_run": "2026-02-11T08:00:00Z",
    "trigger": "cron[day_of_week='tue']",
    "last_execution": {
      "id": "uuid-here",
      "job_id": "weekly_import",
      "status": "success",
      "executed_at": "2026-02-04T08:00:00Z",
      "result": {...},
      "season": 2025,
      "week": 18
    }
  }
]
```

### Trigger Manual Import

Manually trigger a data import for a specific week/season.

```bash
POST /api/jobs/trigger
Content-Type: application/json

{
  "year": 2023,
  "week": 1,
  "source": "nflverse"
}
```

**Response**:
```json
{
  "success": true,
  "players_imported": 50,
  "players_updated": 10,
  "projections_imported": 100,
  "projections_updated": 20,
  "source": "nflverse",
  "year": 2023,
  "week": 1,
  "errors": [],
  "timestamp": "2026-02-07T12:00:00Z"
}
```

**Use Cases**:
- Import historical data
- Re-import a week if initial import failed
- Test import functionality
- Backfill missing weeks

### Get Job History

View execution history for all jobs or a specific job.

```bash
# All jobs (last 50)
GET /api/jobs/history

# Specific job (last 10)
GET /api/jobs/history?job_id=weekly_import&limit=10
```

**Response**:
```json
[
  {
    "id": "uuid-here",
    "job_id": "weekly_import",
    "status": "success",
    "executed_at": "2026-02-04T08:00:00Z",
    "result": {...},
    "season": 2025,
    "week": 18,
    "created_at": "2026-02-04T08:00:05Z"
  },
  ...
]
```

### Get Specific Execution

Get detailed information about a specific job execution.

```bash
GET /api/jobs/history/{execution_id}
```

**Response**:
```json
{
  "id": "execution-uuid",
  "job_id": "weekly_import",
  "status": "success",
  "executed_at": "2026-02-04T08:00:00Z",
  "result": {
    "success": true,
    "players_imported": 50,
    "projections_imported": 100,
    "errors": []
  },
  "season": 2025,
  "week": 18,
  "created_at": "2026-02-04T08:00:05Z"
}
```

## Architecture

### Components

1. **JobScheduler** (`src/jobs/scheduler.py`)
   - Manages APScheduler instance
   - Registers scheduled jobs
   - Provides manual import method
   - Logs executions to database

2. **Jobs API** (`src/api/jobs.py`)
   - Exposes job management endpoints
   - Provides status and history queries
   - Allows manual job triggering

3. **FastAPI Lifespan** (`src/main.py`)
   - Starts scheduler on application startup
   - Shuts down scheduler on application shutdown
   - Ensures clean lifecycle management

### Lifecycle Flow

```
App Start → lifespan() → scheduler.start() → APScheduler running
                                           ↓
                          Tuesday 8AM UTC → weekly_import_job()
                                           ↓
                          LoaderService.import_weekly_data()
                                           ↓
                          Log to job_executions table
                                           
App Stop  → lifespan() → scheduler.shutdown() → APScheduler stopped
```

## Configuration

### Changing Schedule

To modify the weekly import schedule, edit `src/jobs/scheduler.py`:

```python
# Current: Tuesday 8:00 AM UTC
CronTrigger(day_of_week='tue', hour=8, minute=0, timezone='UTC')

# Examples:
# Every day at 6:00 AM UTC
CronTrigger(hour=6, minute=0, timezone='UTC')

# Every Sunday at 22:00 UTC (after MNF)
CronTrigger(day_of_week='sun', hour=22, minute=0, timezone='UTC')

# Every Wednesday at 12:00 PM EST
CronTrigger(day_of_week='wed', hour=17, minute=0, timezone='UTC')  # 17 UTC = 12 EST
```

### Adding New Scheduled Jobs

To add a new scheduled job:

1. **Create the job method** in `JobScheduler`:
   ```python
   async def daily_cleanup_job(self):
       """Clean up old cached data."""
       try:
           logger.info("Starting daily cleanup...")
           # Your cleanup logic here
           await self._log_job_execution(
               job_id='daily_cleanup',
               status='success',
               result={'cleaned': 100}
           )
       except Exception as e:
           logger.error(f"Cleanup failed: {e}")
   ```

2. **Register the job** in `start()` method:
   ```python
   self.scheduler.add_job(
       self.daily_cleanup_job,
       trigger=CronTrigger(hour=2, minute=0, timezone='UTC'),
       id='daily_cleanup',
       name='Daily Data Cleanup',
       replace_existing=True
   )
   ```

3. **Add API endpoint** (optional) in `src/api/jobs.py` to trigger manually

## Troubleshooting

### Job Not Running

**Check scheduler status**:
```bash
curl http://localhost:8000/api/jobs/status
```

Look for:
- `next_run` should have a future datetime
- Scheduler should be in `running` state

**Check logs**:
```bash
# Application logs will show:
# "Starting job scheduler..."
# "Job scheduler started successfully"
```

**Common issues**:
- Application not running (scheduler only runs when app is running)
- Server timezone mismatch
- APScheduler not installed: `pip install APScheduler==3.10.4`

### Job Failed

**Check execution history**:
```bash
curl http://localhost:8000/api/jobs/history?job_id=weekly_import&limit=1
```

Look at `result.errors` array for error messages.

**Common failures**:
- Network error connecting to data source
- Invalid week/season numbers
- Database connection issues

**Resolution**:
1. Check application logs for stack traces
2. Verify data source availability (NFLVerse, FFDP)
3. Manually trigger import to test: `POST /api/jobs/trigger`
4. Check Supabase connection

### Event Loop Errors

If you see "Event loop is closed" errors:
- This typically happens in testing environments
- Tests mock the scheduler to avoid event loop conflicts
- In production, FastAPI manages the event loop correctly

## Monitoring Best Practices

1. **Check job status regularly**:
   ```bash
   curl http://localhost:8000/api/jobs/status
   ```

2. **Review execution history weekly**:
   ```bash
   curl http://localhost:8000/api/jobs/history?job_id=weekly_import&limit=7
   ```

3. **Set up alerts** (future):
   - Alert if job status is 'failed' or 'error'
   - Alert if next_run is null (scheduler stopped)
   - Alert if no executions in past 7 days

4. **Monitor database growth**:
   - `job_executions` table will grow over time
   - Consider adding cleanup job for executions older than 90 days

5. **Verify data freshness**:
   - Check `projections` table for recent data
   - Ensure latest week is imported

## Testing

### Unit Tests

Run scheduler tests:
```bash
pytest tests/jobs/test_scheduler.py -v
```

Tests cover:
- Scheduler initialization
- Job registration
- Manual imports
- Execution logging
- Error handling

### API Tests

Run jobs API tests:
```bash
pytest tests/api/test_jobs.py -v
```

Tests cover:
- Status endpoint
- Manual trigger endpoint
- History queries
- Error responses

### Integration Testing

1. **Start application**:
   ```bash
   uvicorn src.main:app --reload
   ```

2. **Verify scheduler started**:
   ```bash
   # Check logs for: "Job scheduler started successfully"
   ```

3. **Get job status**:
   ```bash
   curl http://localhost:8000/api/jobs/status | jq
   ```

4. **Trigger manual import**:
   ```bash
   curl -X POST http://localhost:8000/api/jobs/trigger \
     -H "Content-Type: application/json" \
     -d '{"year": 2023, "week": 1, "source": "nflverse"}' | jq
   ```

5. **Check execution was logged**:
   ```bash
   curl http://localhost:8000/api/jobs/history?limit=1 | jq
   ```

## Production Considerations

### Deployment

When deploying to production:

1. **Environment Variables**: No additional env vars needed, scheduler uses existing Supabase config

2. **Server Uptime**: Scheduler only runs when application is running
   - Use process manager (systemd, supervisor)
   - Or containerized deployment (Docker, Kubernetes)
   - Cloud platforms (Fly.io, Render) keep app running

3. **Timezone**: All times are UTC
   - No configuration needed
   - Consistent across deployments

4. **Resource Usage**: APScheduler is lightweight
   - Minimal CPU when idle
   - Spikes only during job execution

### Alternative Approaches

If you prefer external scheduling:

1. **Cron + Manual Trigger**:
   ```bash
   # Add to crontab:
   0 8 * * 2 curl -X POST http://your-app/api/jobs/trigger -d '{"year":2023,"week":1}'
   ```

2. **GitHub Actions**:
   ```yaml
   # .github/workflows/weekly-import.yml
   on:
     schedule:
       - cron: '0 8 * * 2'
   jobs:
     import:
       runs-on: ubuntu-latest
       steps:
         - name: Trigger Import
           run: |
             curl -X POST ${{ secrets.API_URL }}/api/jobs/trigger \
               -d '{"year":2023,"week":1}'
   ```

3. **Cloud Scheduler** (GCP, AWS EventBridge):
   - Configure HTTP target to `/api/jobs/trigger`
   - Set cron expression
   - Add authentication if needed

## Future Enhancements

Possible improvements:

1. **Smarter Week Detection**:
   - Integrate with NFL schedule API
   - Auto-detect current week accurately
   - Handle bye weeks, playoffs

2. **Multi-Source Import**:
   - Import from multiple sources simultaneously
   - Aggregate and average projections
   - Weight by source reliability

3. **Error Notifications**:
   - Email/Slack alerts on failures
   - Webhook integration
   - PagerDuty for critical errors

4. **Job Dependencies**:
   - Chain jobs (import → calculate → notify)
   - Conditional execution
   - Retry logic with exponential backoff

5. **Performance Optimization**:
   - Batch imports (multiple weeks)
   - Parallel processing
   - Caching frequently accessed data

6. **Historical Backfill**:
   - Job to import multiple seasons
   - Progress tracking UI
   - Resume on failure

## References

- [APScheduler Documentation](https://apscheduler.readthedocs.io/)
- [FastAPI Lifespan Events](https://fastapi.tiangolo.com/advanced/events/)
- [Cron Expression Format](https://crontab.guru/)
- [NFLVerse Data Repository](https://github.com/nflverse/nfl_data_py)

## Support

For issues or questions:
1. Check application logs
2. Review `/api/jobs/history` for execution details
3. Test manually with `/api/jobs/trigger`
4. Open GitHub issue with error details

# Deployment Guide

## Overview

This guide covers deploying the NFL Fantasy Football Projections dashboard to various cloud platforms. We'll cover Vercel (requested) and also recommend better alternatives for FastAPI applications.

---

## ⚠️ Important: Vercel Limitations

**Vercel is NOT recommended for this application** because:

1. **Serverless Architecture**: Vercel uses serverless functions with cold starts, not ideal for FastAPI
2. **Execution Time Limits**: 10-60 second timeout limits (depending on plan)
3. **No Persistent Connections**: Each request creates a new connection to Supabase
4. **Cold Start Delays**: First request after inactivity can be very slow
5. **Python Support**: Limited compared to Node.js on Vercel

**Recommended alternatives**: Render, Railway, or Fly.io (see below)

However, if you still want to deploy to Vercel, here's how:

---

## Option 1: Vercel Deployment (Not Recommended)

### Prerequisites

- Vercel account (free tier available)
- Supabase project with credentials
- Git repository for the project

### Step 1: Install Vercel CLI

```bash
npm install -g vercel
```

### Step 2: Create Vercel Configuration

Create `vercel.json` in project root:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "src/main.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "src/main.py"
    }
  ],
  "env": {
    "SUPABASE_URL": "@supabase_url",
    "SUPABASE_KEY": "@supabase_key",
    "ENVIRONMENT": "production"
  }
}
```

### Step 3: Create Requirements for Vercel

Create `requirements.txt` in project root (if not already present):

```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
supabase==2.0.3
pydantic==2.5.0
python-dotenv==1.0.0
nfl-data-py==0.3.2
pandas==2.1.3
jinja2==3.1.2
mangum==0.17.0
```

### Step 4: Create Vercel Entry Point

Create `api/index.py`:

```python
"""
Vercel serverless entry point.
"""
from mangum import Mangum
from src.main import app

# Wrap FastAPI app for serverless
handler = Mangum(app, lifespan="off")
```

### Step 5: Update Project Structure

Your structure should look like:
```
ottoneu-projections-football/
├── api/
│   └── index.py          # Vercel entry point
├── src/
│   ├── main.py
│   ├── config.py
│   └── ...
├── requirements.txt
├── vercel.json
└── .env (not committed)
```

### Step 6: Set Environment Variables

```bash
# Add secrets to Vercel
vercel secrets add supabase_url "your-supabase-url"
vercel secrets add supabase_key "your-supabase-anon-key"
```

Or set them in Vercel Dashboard:
1. Go to your project settings
2. Navigate to "Environment Variables"
3. Add:
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
   - `ENVIRONMENT` = "production"

### Step 7: Deploy

```bash
# Login to Vercel
vercel login

# Deploy
vercel

# Or deploy to production
vercel --prod
```

### Step 8: Access Your Dashboard

After deployment, Vercel provides a URL like:
```
https://your-project-name.vercel.app/dashboard
```

### Known Issues with Vercel

1. **Cold Starts**: First request after ~5 minutes of inactivity will be slow (5-10 seconds)
2. **Import Timeouts**: Data import endpoints may timeout on large imports
3. **No Background Jobs**: Can't run scheduled tasks (Phase 5 won't work)
4. **Memory Limits**: 1024 MB default limit
5. **No WebSockets**: Real-time features won't work

---

## ✅ Option 2: Render.com (RECOMMENDED)

### Why Render?

- ✅ Free tier with 750 hours/month
- ✅ Native Python/FastAPI support
- ✅ Persistent server (no cold starts)
- ✅ Background workers support
- ✅ Automatic HTTPS
- ✅ Simple deployment from Git

### Deployment Steps

#### 1. Create `render.yaml`

```yaml
services:
  - type: web
    name: nfl-projections
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn src.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: SUPABASE_URL
        sync: false
      - key: SUPABASE_KEY
        sync: false
      - key: ENVIRONMENT
        value: production
```

#### 2. Push to GitHub

```bash
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

#### 3. Deploy on Render

1. Go to https://render.com
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Render auto-detects settings from `render.yaml`
5. Add environment variables in dashboard:
   - `SUPABASE_URL`: Your Supabase project URL
   - `SUPABASE_KEY`: Your Supabase anon key
6. Click "Create Web Service"

#### 4. Access Your App

Render provides a URL like:
```
https://nfl-projections.onrender.com/dashboard
```

### Render Advantages

- **No Cold Starts**: Server stays warm on free tier (spins down after 15 min inactivity)
- **Build Logs**: Clear deployment logs
- **Auto-Deploy**: Automatically deploys on git push
- **Custom Domains**: Easy to add your own domain
- **Cron Jobs**: Can schedule tasks (Phase 5)

---

## Option 3: Railway.app

### Why Railway?

- ✅ $5 free credit monthly
- ✅ Excellent Python support
- ✅ Simple dashboard
- ✅ Great for hobby projects
- ✅ Fast deployments

### Deployment Steps

#### 1. Install Railway CLI

```bash
npm install -g @railway/cli
```

#### 2. Login and Initialize

```bash
railway login
railway init
```

#### 3. Add Start Command

Create `Procfile`:

```
web: uvicorn src.main:app --host 0.0.0.0 --port $PORT
```

#### 4. Deploy

```bash
railway up
```

#### 5. Set Environment Variables

```bash
railway variables set SUPABASE_URL="your-url"
railway variables set SUPABASE_KEY="your-key"
railway variables set ENVIRONMENT="production"
```

Or set them in Railway dashboard.

#### 6. Access Your App

Railway provides a URL like:
```
https://nfl-projections-production.up.railway.app/dashboard
```

---

## Option 4: Fly.io

### Why Fly.io?

- ✅ Free tier: 3 shared-cpu VMs
- ✅ Global edge network
- ✅ Great performance
- ✅ Docker-based (full control)

### Deployment Steps

#### 1. Install Fly CLI

```bash
curl -L https://fly.io/install.sh | sh
```

#### 2. Login and Launch

```bash
flyctl auth login
flyctl launch
```

Follow prompts:
- Choose app name
- Choose region (closest to you)
- Don't deploy yet

#### 3. Create `fly.toml`

Fly generates this, but verify:

```toml
app = "nfl-projections"

[build]
  builder = "paketobuildpacks/builder:base"

[env]
  PORT = "8000"
  ENVIRONMENT = "production"

[http_service]
  internal_port = 8000
  force_https = true
  auto_stop_machines = true
  auto_start_machines = true
  min_machines_running = 0

[[vm]]
  cpu_kind = "shared"
  cpus = 1
  memory_mb = 256
```

#### 4. Set Secrets

```bash
flyctl secrets set SUPABASE_URL="your-url"
flyctl secrets set SUPABASE_KEY="your-key"
```

#### 5. Deploy

```bash
flyctl deploy
```

#### 6. Access Your App

```
https://nfl-projections.fly.dev/dashboard
```

---

## Platform Comparison

| Feature | Vercel | Render | Railway | Fly.io |
|---------|--------|--------|---------|--------|
| **FastAPI Support** | ⚠️ Limited | ✅ Excellent | ✅ Excellent | ✅ Excellent |
| **Free Tier** | ✅ Yes | ✅ 750 hrs | ⚠️ $5 credit | ✅ 3 VMs |
| **Cold Starts** | ❌ Yes | ⚠️ After 15min | ⚠️ Varies | ⚠️ Yes |
| **Background Jobs** | ❌ No | ✅ Yes | ✅ Yes | ✅ Yes |
| **Setup Difficulty** | Easy | Easy | Easy | Medium |
| **Custom Domains** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| **HTTPS** | ✅ Auto | ✅ Auto | ✅ Auto | ✅ Auto |
| **Our Recommendation** | ❌ No | ✅✅✅ Best | ✅✅ Great | ✅ Advanced |

---

## Production Checklist

Before deploying to production:

### Security

- [ ] Change `SUPABASE_KEY` from anon to service_role if needed
- [ ] Enable CORS restrictions in Supabase
- [ ] Add authentication (if needed)
- [ ] Review Row Level Security policies in Supabase
- [ ] Don't commit `.env` file

### Performance

- [ ] Enable gzip compression
- [ ] Set up CDN for static assets (if added later)
- [ ] Configure database connection pooling
- [ ] Add caching headers for dashboard pages
- [ ] Monitor memory usage

### Monitoring

- [ ] Set up error tracking (Sentry, Rollbar)
- [ ] Configure logging (LogDNA, Papertrail)
- [ ] Add uptime monitoring (UptimeRobot)
- [ ] Set up alerts for failures

### Database

- [ ] Verify Supabase project is NOT paused
- [ ] Back up Supabase data regularly
- [ ] Set up connection pooling in Supabase
- [ ] Review and optimize slow queries

### Testing

- [ ] Run all tests before deploy: `pytest tests/`
- [ ] Test on staging environment first
- [ ] Verify all environment variables are set
- [ ] Check health endpoint: `/health`

---

## Troubleshooting

### Issue: "502 Bad Gateway" on Vercel

**Cause**: Serverless function timeout or memory exceeded

**Solution**:
- Reduce import batch sizes
- Move to Render/Railway/Fly.io

### Issue: "Module not found" errors

**Cause**: Missing dependencies in `requirements.txt`

**Solution**:
```bash
pip freeze > requirements.txt
git add requirements.txt
git commit -m "Update dependencies"
git push
```

### Issue: Database connection errors

**Cause**: Wrong Supabase credentials or URL

**Solution**:
- Verify `SUPABASE_URL` format: `https://xxx.supabase.co`
- Check `SUPABASE_KEY` is the anon key (starts with `eyJ...`)
- Test connection locally first

### Issue: Dashboard loads but shows no data

**Cause**: Database is empty or query failing

**Solution**:
1. Check Supabase dashboard - verify data exists
2. Check logs for error messages
3. Test API directly: `/api/projections?season=2023&week=1`

### Issue: Cold start takes 10+ seconds

**Cause**: Platform spins down inactive apps

**Solution**:
- Render: Upgrade to paid tier for always-on
- Use uptime monitor to ping app every 5 minutes
- Accept cold starts on free tier

---

## Custom Domain Setup

### Render

1. Go to Settings → Custom Domains
2. Add your domain (e.g., `projections.yourdomain.com`)
3. Add CNAME record in your DNS:
   ```
   projections.yourdomain.com → your-app.onrender.com
   ```

### Railway

1. Go to Settings → Domains
2. Click "Add Custom Domain"
3. Follow DNS setup instructions

### Fly.io

```bash
flyctl certs add projections.yourdomain.com
```

Then add DNS A/AAAA records as instructed.

---

## Cost Estimates

### Free Tier (Good for MVP)

**Render Free**:
- 750 hours/month web service
- Spins down after 15 min inactivity
- **Cost**: $0/month

**Supabase Free**:
- 500 MB database
- 2 GB bandwidth
- **Cost**: $0/month

**Total**: **$0/month** (with limitations)

### Production (Recommended)

**Render Starter**:
- Always-on web service
- 512 MB RAM
- **Cost**: $7/month

**Supabase Pro**:
- 8 GB database
- 250 GB bandwidth
- **Cost**: $25/month

**Total**: **$32/month**

---

## Recommended Deployment Strategy

1. **Start**: Deploy to **Render free tier** for testing
2. **Validate**: Ensure app works well in production
3. **Scale**: Upgrade to Render paid tier when ready
4. **Monitor**: Set up error tracking and uptime monitoring
5. **Iterate**: Add features and optimize based on usage

---

## Next Steps After Deployment

1. **Share URL**: Send dashboard link to users
2. **Import Data**: Use API to import historical data
3. **Monitor Usage**: Check logs and error rates
4. **Add Features**: Implement Phase 5 (automation)
5. **Get Feedback**: Iterate based on user feedback

---

## Support & Resources

- **Render Docs**: https://render.com/docs
- **Railway Docs**: https://docs.railway.app
- **Fly.io Docs**: https://fly.io/docs
- **FastAPI Deployment**: https://fastapi.tiangolo.com/deployment/
- **Supabase Docs**: https://supabase.com/docs

---

## Conclusion

While Vercel CAN host FastAPI apps, it's not optimal. We strongly recommend:

1. **Best Choice**: **Render.com** - Easy, reliable, great free tier
2. **Runner-up**: **Railway.app** - Simple, good DX
3. **Advanced**: **Fly.io** - Best performance, more control

All three provide better FastAPI support than Vercel and will give you a much better experience.

Choose Render if you want simplicity and reliability. It's the best fit for this project.

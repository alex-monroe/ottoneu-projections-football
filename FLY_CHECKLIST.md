# Fly.io Deployment Checklist

## ✅ Pre-Deployment Setup

### 1. Install Fly CLI
- [x] Installed flyctl v0.4.7
- [x] Added to PATH

### 2. Authenticate
- [ ] Run: `flyctl auth login`
- [ ] Sign up/log in via browser
- [ ] Verify with: `flyctl auth whoami`

### 3. Prepare Environment Variables

You'll need these from Supabase:
- [ ] `SUPABASE_URL` - Your project URL
- [ ] `SUPABASE_KEY` - Your anon/public key

**Where to find them:**
1. Go to https://supabase.com/dashboard
2. Select your project
3. Settings → API
4. Copy **URL** and **anon public** key

## 🚀 Deployment Commands

Once authenticated, run these commands:

```bash
# Set PATH (if in a new terminal)
export FLYCTL_INSTALL="/Users/alexmonroe/.fly"
export PATH="$FLYCTL_INSTALL/bin:$PATH"

# Launch app (creates app on Fly.io)
flyctl launch --no-deploy

# Answer prompts:
# - App name: nfl-projections (or choose your own)
# - Region: Choose closest to you (e.g., sjc for San Jose)
# - Would you like to set up a Postgresql database? NO
# - Would you like to set up an Upstash Redis database? NO
# - Create .dockerignore? YES (already exists, will skip)
# - Would you like to deploy now? NO

# Set secrets (replace with your actual values)
flyctl secrets set SUPABASE_URL="https://your-project.supabase.co"
flyctl secrets set SUPABASE_KEY="eyJhbGc..."

# Deploy!
flyctl deploy

# Open in browser
flyctl open
```

## 📋 After Deployment

### Verify Everything Works

```bash
# Check app status
flyctl status

# View logs
flyctl logs

# Check health endpoint
curl https://your-app.fly.dev/health

# Visit dashboard
open https://your-app.fly.dev/dashboard
```

### Import Some Data

```bash
# Import week 1 of 2023
curl -X POST "https://your-app.fly.dev/api/loaders/import/weekly" \
  -H "Content-Type: application/json" \
  -d '{"year": 2023, "week": 1, "source": "nflverse"}'
```

## 🐛 Troubleshooting

### "Could not find App"
Run: `flyctl apps create nfl-projections`

### "Out of memory"
Edit fly.toml, change `memory_mb = 512`, redeploy

### "App is slow"
First request after idle takes 1-2 seconds (normal for scale-to-0)

### "Build failed"
Check logs: `flyctl logs`

## 💰 Cost Monitoring

```bash
# Check usage
flyctl dashboard

# View billing (should show $0)
flyctl billing
```

## 🔄 Updates

To update your app after making changes:

```bash
git add .
git commit -m "Update app"
flyctl deploy
```

## 📍 Your App URLs

After deployment, you'll have:
- **Dashboard**: https://nfl-projections.fly.dev/dashboard
- **API Docs**: https://nfl-projections.fly.dev/docs
- **Health Check**: https://nfl-projections.fly.dev/health

## ✨ Next Steps

- [ ] Share your dashboard URL
- [ ] Import historical data
- [ ] Set up custom domain (optional)
- [ ] Monitor usage and costs

# Quick Deploy to Render (5 Minutes)

This is the fastest way to get your dashboard live on the internet.

## Prerequisites

- GitHub account
- Render account (free): https://render.com
- Supabase project with credentials

## Step 1: Push to GitHub

```bash
# Initialize git if you haven't already
git init
git add .
git commit -m "Initial commit"

# Create a new repository on GitHub, then:
git remote add origin https://github.com/yourusername/nfl-projections.git
git push -u origin main
```

## Step 2: Deploy on Render

1. Go to https://render.com/dashboard
2. Click **"New +"** → **"Web Service"**
3. Click **"Connect GitHub"** and authorize Render
4. Select your `nfl-projections` repository
5. Render will auto-detect settings from `render.yaml`

## Step 3: Set Environment Variables

In the Render dashboard, add these environment variables:

| Key | Value | Example |
|-----|-------|---------|
| `SUPABASE_URL` | Your Supabase project URL | `https://abcdefg.supabase.co` |
| `SUPABASE_KEY` | Your Supabase anon key | `eyJhbGc...` |
| `ENVIRONMENT` | `production` | _(auto-filled)_ |

To find your Supabase credentials:
1. Go to https://supabase.com/dashboard
2. Select your project
3. Click Settings → API
4. Copy **URL** and **anon/public key**

## Step 4: Deploy!

Click **"Create Web Service"**

Render will:
- Install dependencies (`pip install -r requirements.txt`)
- Start your FastAPI server
- Provide a live URL

⏱️ **First deploy takes 2-3 minutes**

## Step 5: Access Your Dashboard

Once deployed, Render shows your app URL:
```
https://nfl-projections.onrender.com
```

Visit your dashboard at:
```
https://nfl-projections.onrender.com/dashboard
```

## Step 6: Import Some Data

Use the API to import data:

```bash
# Replace with your actual Render URL
curl -X POST "https://nfl-projections.onrender.com/api/loaders/import/weekly" \
  -H "Content-Type: application/json" \
  -d '{"year": 2023, "week": 1, "source": "nflverse"}'
```

Now refresh your dashboard - you should see projections!

## Troubleshooting

### "Service Unavailable" after deployment

**Cause**: App is still starting up

**Solution**: Wait 30 seconds and refresh

### "Database connection error"

**Cause**: Wrong Supabase credentials

**Solution**:
1. Go to Render → Settings → Environment
2. Verify `SUPABASE_URL` and `SUPABASE_KEY` are correct
3. Save and redeploy

### Dashboard loads but shows no data

**Cause**: Database is empty

**Solution**: Import data using the curl command above

### Free tier limitations

- App spins down after 15 minutes of inactivity
- First request after spin-down takes 30-60 seconds (cold start)
- 750 hours/month limit (enough for hobby use)

**Upgrade**: $7/month for always-on service

## Auto-Deploy Setup

Render automatically deploys when you push to GitHub:

```bash
# Make changes to your code
git add .
git commit -m "Add new feature"
git push

# Render detects push and deploys automatically!
```

## Custom Domain (Optional)

1. In Render dashboard, go to **Settings → Custom Domains**
2. Click **"Add Custom Domain"**
3. Enter your domain: `projections.yourdomain.com`
4. Add CNAME record in your DNS provider:
   ```
   projections.yourdomain.com → your-app.onrender.com
   ```
5. Wait 5-10 minutes for DNS propagation

## Monitoring

### View Logs

In Render dashboard:
1. Go to **Logs** tab
2. See real-time server logs
3. Filter by error/warning

### Check Health

Visit: `https://your-app.onrender.com/health`

Should return:
```json
{
  "status": "healthy",
  "environment": "production",
  "timestamp": "2026-02-07T..."
}
```

### Metrics

Free tier includes:
- CPU usage
- Memory usage
- Request count
- Response times

## Cost Breakdown

### Free Tier
- Web service: **$0/month** (750 hours)
- Supabase: **$0/month** (500 MB database)
- **Total**: **$0/month**

### Paid (Recommended for Production)
- Render Starter: **$7/month** (always-on)
- Supabase Pro: **$25/month** (8 GB, better support)
- **Total**: **$32/month**

## Next Steps

1. ✅ Deploy to Render (you just did this!)
2. 📊 Import historical data for multiple weeks
3. 🎨 Customize the dashboard styling
4. 🔄 Set up automatic weekly imports (Phase 5)
5. 📱 Share the URL with friends

## Need Help?

- **Full deployment guide**: See [DEPLOYMENT.md](DEPLOYMENT.md)
- **Render docs**: https://render.com/docs
- **Supabase docs**: https://supabase.com/docs
- **FastAPI docs**: https://fastapi.tiangolo.com

---

**Congratulations! Your dashboard is live! 🎉**

Share it: `https://your-app.onrender.com/dashboard`

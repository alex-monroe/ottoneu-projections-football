# Deploy to Fly.io (Free Tier)

The most cost-efficient option if you've already used Render/Railway free tiers.

## Why Fly.io?

- ✅ **Truly free**: 3 VMs, 3GB storage, 160GB transfer
- ✅ **No hour limits** (unlike Render's 750 hours)
- ✅ **No credit card** required for free tier
- ✅ **Auto-scaling**: Can scale to 0 when not in use
- ✅ **Global edge network**: Fast everywhere

## Prerequisites

- Fly.io account: https://fly.io/app/sign-up
- Supabase credentials

## Quick Deploy (5 Minutes)

### Step 1: Install Fly CLI

**macOS/Linux:**
```bash
curl -L https://fly.io/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"
```

### Step 2: Login

```bash
flyctl auth login
```

### Step 3: Create Fly Configuration

Create `fly.toml` in project root:

```toml
app = "nfl-projections"
primary_region = "sjc"  # San Jose - change to region closest to you

[build]
  builder = "paketobuildpacks/builder:base"

[env]
  PORT = "8000"
  ENVIRONMENT = "production"

[http_service]
  internal_port = 8000
  force_https = true
  auto_stop_machines = true    # Scale to 0 when idle
  auto_start_machines = true   # Wake up on request
  min_machines_running = 0     # Allow scaling to 0

[[vm]]
  cpu_kind = "shared"
  cpus = 1
  memory_mb = 256  # Free tier
```

### Step 4: Launch App

```bash
flyctl launch --no-deploy
```

Answer the prompts:
- ✅ Copy configuration? **Yes**
- ✅ Create .dockerignore? **Yes**
- ✅ Would you like to deploy now? **No** (we need to set secrets first)

### Step 5: Set Secrets

```bash
flyctl secrets set SUPABASE_URL="your-supabase-url"
flyctl secrets set SUPABASE_KEY="your-supabase-anon-key"
```

### Step 6: Deploy

```bash
flyctl deploy
```

⏱️ First deploy takes 2-3 minutes

### Step 7: Open Your App

```bash
flyctl open
```

Your dashboard will be at:
```
https://nfl-projections.fly.dev/dashboard
```

## Free Tier Limits

| Resource | Free Allowance | Notes |
|----------|---------------|-------|
| VMs | 3 shared-cpu VMs | 256MB RAM each |
| Storage | 3 GB | Persistent volumes |
| Bandwidth | 160 GB/month | Outbound data |
| Requests | Unlimited | No request limits! |

**For this toy project**: You'll easily stay within limits.

## Auto-Scaling to $0

With the config above, Fly will:
- **Scale to 0** after ~5 minutes of no traffic
- **Auto-wake** when someone visits (takes 1-2 seconds)
- **Cost**: $0 when idle, $0 when active (within free tier)

## Monitoring

### Check Status
```bash
flyctl status
```

### View Logs
```bash
flyctl logs
```

### Check Usage
```bash
flyctl dashboard
```

Go to Billing → see your usage (should be $0)

## Regions

Choose the region closest to you or your users:

| Code | Location |
|------|----------|
| `sjc` | San Jose, CA |
| `iad` | Ashburn, VA |
| `lhr` | London |
| `fra` | Frankfurt |
| `syd` | Sydney |

Update `primary_region` in `fly.toml`

## Custom Domain

```bash
flyctl certs add projections.yourdomain.com
```

Then add DNS records as instructed.

## Import Data

Once deployed:

```bash
# Get your Fly URL
FLY_URL=$(flyctl info --json | jq -r .hostname)

# Import data
curl -X POST "https://${FLY_URL}/api/loaders/import/weekly" \
  -H "Content-Type: application/json" \
  -d '{"year": 2023, "week": 1, "source": "nflverse"}'
```

## Troubleshooting

### "Could not find App"

**Solution**: Run `flyctl apps create nfl-projections` first

### "Out of memory"

**Solution**: Increase memory in fly.toml:
```toml
[[vm]]
  memory_mb = 512  # Still free tier
```

Then: `flyctl deploy`

### App is slow to wake up

**Solution**: This is normal for scale-to-0. First request takes 1-2 seconds.

To keep 1 machine always running (still free):
```toml
[http_service]
  min_machines_running = 1  # Change from 0 to 1
```

## Cost Estimate

**Current usage (toy project):**
- 1 VM (256MB)
- Minimal traffic
- Scale to 0 when idle

**Cost**: **$0/month** ✅

**If you grow:**
- Up to 3 VMs: $0/month
- 4th VM: ~$1.94/month (shared-cpu-1x)

## Comparison: Fly.io vs Others

| Feature | Fly.io Free | Vercel | Render Free |
|---------|------------|--------|-------------|
| **VMs** | 3 VMs | Serverless | 750 hours |
| **Memory** | 256MB each | 1GB | 512MB |
| **Cold Start** | 1-2 sec | 5-10 sec | 30-60 sec |
| **Hour Limit** | ❌ None | ❌ None | ⚠️ 750/month |
| **Background Jobs** | ✅ Yes | ❌ No | ✅ Yes |
| **FastAPI Support** | ✅ Excellent | ⚠️ Limited | ✅ Excellent |

**Winner for toy projects**: **Fly.io** 🏆

## Update Your App

```bash
# Make code changes
git add .
git commit -m "Update dashboard"

# Deploy
flyctl deploy
```

## Cleanup (If Needed)

```bash
# Delete app
flyctl apps destroy nfl-projections

# This frees up all resources
```

## Why This Beats Vercel

For this FastAPI app:
- ✅ Faster cold starts (1-2s vs 5-10s)
- ✅ Better FastAPI support (real VM vs serverless)
- ✅ Can run background jobs (Phase 5)
- ✅ More control over resources
- ✅ No timeout limits for long imports

## Resources

- Fly.io Docs: https://fly.io/docs
- Fly.io Pricing: https://fly.io/docs/about/pricing
- Community Forum: https://community.fly.io

---

**Total Cost**: **$0/month** for this toy project 🎉

**Deployment Time**: 5 minutes

**Ongoing Maintenance**: Zero (auto-deploys, auto-scales)

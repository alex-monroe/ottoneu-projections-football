# Cost Comparison for Toy Projects

Since you've already used Render and Railway free tiers, here are your best options ranked by cost.

## 🏆 Winner: Fly.io - $0/month

### What You Get
- 3 shared-cpu VMs (256MB RAM each)
- 3 GB persistent storage
- 160 GB outbound bandwidth/month
- **No hour limits** (unlike Render)
- Auto-scales to 0 when idle

### Why It's Perfect
- ✅ Truly free (no credit card required initially)
- ✅ No time limits
- ✅ Proper VM (not serverless)
- ✅ Great for FastAPI
- ✅ Can run background jobs

### Limitations
- Cold start: 1-2 seconds when scaled to 0
- Need to stay within 3 VMs
- 256MB RAM per VM (upgradable)

**Deploy Guide**: [FLY_DEPLOY.md](FLY_DEPLOY.md)

---

## 🥈 Runner-up: Vercel - $0/month

### What You Get
- Unlimited serverless function invocations
- 100GB bandwidth/month
- 6000 build minutes/month
- Automatic scaling

### Why It Could Work
- ✅ Truly unlimited on hobby tier
- ✅ Good for low-traffic toy projects
- ✅ Automatic deployments
- ✅ Simple setup

### Limitations
- ⚠️ Serverless = cold starts (5-10 seconds)
- ⚠️ 10 second execution limit (60s on pro)
- ⚠️ Not ideal for FastAPI
- ⚠️ No background jobs (Phase 5 won't work)

**For a toy project with minimal traffic**: Could work fine!

**Deploy Guide**: See [DEPLOYMENT.md](DEPLOYMENT.md#option-1-vercel-deployment-not-recommended)

---

## 🥉 Alternative: Google Cloud Run - ~$1-2/month

### What You Get
- Pay-per-use pricing
- 2 million requests/month free
- Always-on first 2 months
- Proper container runtime

### Costs
- First 2 million requests: **Free**
- CPU time: $0.00002400/vCPU-second
- Memory: $0.00000250/GiB-second
- **Estimated**: $1-2/month for toy project

### Why It's Good
- ✅ Proper container (not serverless)
- ✅ Great FastAPI support
- ✅ Pay only for what you use
- ✅ Generous free tier
- ✅ Background jobs work

### Limitations
- ⚠️ Requires credit card
- ⚠️ Requires Docker knowledge
- ⚠️ More complex setup

---

## 💸 Full Cost Breakdown

### Fly.io (Recommended)
| Resource | Usage | Cost |
|----------|-------|------|
| 1 VM (256MB) | Always on | **$0** |
| Or: Scale to 0 | Auto-wake | **$0** |
| Storage (3GB) | Included | **$0** |
| Bandwidth (160GB) | Included | **$0** |
| **Total** | | **$0/month** |

### Vercel
| Resource | Usage | Cost |
|----------|-------|------|
| Function invocations | Unlimited | **$0** |
| Bandwidth (100GB) | Included | **$0** |
| Build time | Included | **$0** |
| **Total** | | **$0/month** |

### Google Cloud Run
| Resource | Usage | Cost |
|----------|-------|------|
| Requests (10k/month) | Free tier | **$0** |
| CPU time (~2 hrs) | ~$0.17 | **$0.17** |
| Memory (~0.5 GB) | ~$0.13 | **$0.13** |
| Bandwidth (5GB) | Free tier | **$0** |
| **Total** | | **~$0.30-2/month** |

### PythonAnywhere (Free)
| Resource | Usage | Cost |
|----------|-------|------|
| Web app | 1 app | **$0** |
| CPU seconds | 100/day limit | **$0** |
| Storage | 512MB | **$0** |
| **Total** | | **$0/month** |

**Limitations**: Very restricted (100 CPU seconds/day)

### Paid Options (If Free Doesn't Work)
| Platform | Cost | Notes |
|----------|------|-------|
| Railway Hobby | $5/month | You already use free tier |
| Render Starter | $7/month | You already use free tier |
| DigitalOcean | $6/month | Droplet (requires management) |
| Heroku Basic | $7/month | No free tier anymore |

---

## 📊 Recommendation by Use Case

### Toy Project (You!)
**Choose**: **Fly.io** 🏆
- Free forever
- No limits for your use case
- Proper VM for FastAPI
- Auto-scales to 0 = $0 cost when idle

### Very Low Traffic
**Choose**: **Vercel**
- Works fine despite limitations
- Completely free
- Easy setup

### Need Background Jobs
**Choose**: **Fly.io**
- Only free option that supports cron jobs
- Important for Phase 5 (automation)

### Want to Learn Containers
**Choose**: **Google Cloud Run**
- Great learning experience
- Minimal cost (~$1/month)
- Industry-standard platform

---

## 🎯 My Final Recommendation

For your situation (already used Render/Railway free tiers):

### 1st Choice: Fly.io
```bash
# 5 minute setup
flyctl launch
flyctl secrets set SUPABASE_URL="..." SUPABASE_KEY="..."
flyctl deploy

# Cost: $0/month ✅
```

**Pros**: Free, no limits, perfect for FastAPI
**Cons**: Need to install flyctl CLI

### 2nd Choice: Vercel
```bash
# 3 minute setup
vercel

# Cost: $0/month ✅
```

**Pros**: Easiest setup, free
**Cons**: Cold starts, not ideal for FastAPI

---

## 🧮 Cost Calculator

For your toy project, assuming:
- **Traffic**: 100 requests/day
- **Active time**: 1 hour/day
- **Users**: Just you + a few friends

### Fly.io
- VMs: 1 (free tier)
- Auto-scales to 0 when idle
- **Total**: **$0/month** ✅

### Vercel
- Function invocations: ~3,000/month
- Well under free tier limits
- **Total**: **$0/month** ✅

### Google Cloud Run
- Requests: ~3,000/month (free)
- CPU time: ~30 minutes
- Memory: ~0.25 GB-hour
- **Total**: **~$0.10-0.30/month** 💵

### Render (if you had free tier available)
- Active: ~30 hours/month
- Well under 750 hour limit
- **Total**: **$0/month** ✅
- But you already use this!

---

## 💡 Pro Tip: Use Fly.io

Since your project is literally described as a "tiny toy project":

1. **Deploy to Fly.io** (takes 5 minutes)
2. **Scale to 0** when idle (automatic)
3. **Pay**: $0/month forever
4. **Enjoy**: Full FastAPI support, no limitations

If you ever outgrow free tier (need 4+ VMs):
- 4th VM = +$1.94/month
- Still cheaper than paid alternatives

---

## 🚀 Quick Start

```bash
# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Deploy (5 minutes)
flyctl launch
flyctl secrets set SUPABASE_URL="..." SUPABASE_KEY="..."
flyctl deploy

# Done! Your app is live at:
# https://nfl-projections.fly.dev
```

**Total cost**: $0/month

**Total time**: 5 minutes

**Total regret**: Zero! 😊

---

See full deployment guide: [FLY_DEPLOY.md](FLY_DEPLOY.md)

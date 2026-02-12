# Deployment Guide - Autonomous Literary Agent

This guide covers deployment options for running the Literary Agent 24/7 in the cloud.

## Quick Deployment Comparison

| Platform | Free Tier | Best For | Setup Time |
|----------|-----------|----------|------------|
| GitHub Actions | 2000 min/month | Scheduled tasks | 5 min |
| Render | 750 hours/month | Web service | 10 min |
| Railway | $5 credit | Background worker | 10 min |
| Google Cloud Run | 2M requests | Serverless | 15 min |
| Koyeb | 512MB RAM | Simple deploy | 5 min |

---

## Option 1: GitHub Actions (Recommended for Scheduling)

**Best for:** Running agent on schedule (every 6 hours)

### Setup

1. Push code to GitHub repository
2. Go to Settings → Secrets and variables → Actions
3. Add your API keys as secrets:
   - `GEMINI_API_KEY_1`
   - `GROQ_API_KEY_1`
   - etc.
4. Enable GitHub Actions
5. The workflow in `.github/workflows/agent.yml` will run automatically

### Schedule

Edit `.github/workflows/agent.yml` to change frequency:
```yaml
on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours
```

---

## Option 2: Render (Recommended for Web Service)

**Best for:** Continuous 24/7 operation with web dashboard

### Setup

1. Go to [render.com](https://render.com) and sign up
2. Click "New" → "Blueprint"
3. Connect your GitHub repository
4. Render will detect `render.yaml` automatically
5. Add environment variables in the dashboard

### Free Tier Limits
- 750 hours/month (enough for 1 service 24/7)
- 512MB RAM
- 0.1 CPU
- Service spins down after inactivity

### Keeping Service Alive

Add a cron job to ping the health endpoint:
```bash
# Using cron-job.org or similar
curl https://your-app.onrender.com/health
```

---

## Option 3: Railway

**Best for:** Background workers with persistent storage

### Setup

1. Go to [railway.app](https://railway.app)
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repository
4. Railway detects `railway.json` automatically
5. Add environment variables

### Free Tier
- $5 free credit monthly
- 512MB RAM
- Shared CPU

---

## Option 4: Google Cloud Run

**Best for:** Serverless with auto-scaling

### Setup

1. Install Google Cloud CLI
2. Enable Cloud Run API
3. Deploy:

```bash
# Build and deploy
gcloud run deploy literary-agent \
  --source . \
  --platform managed \
  --region europe-west1 \
  --allow-unauthenticated \
  --set-env-vars GEMINI_API_KEY_1=your_key
```

### Free Tier
- 2 million requests/month
- 360,000 vCPU-seconds
- 180,000 GB-seconds memory

---

## Option 5: Koyeb

**Best for:** Simple deployment with global edge

### Setup

1. Go to [koyeb.com](https://www.koyeb.com)
2. Create new app
3. Connect GitHub repository
4. Add environment variables
5. Deploy

### Free Tier
- 512MB RAM
- 0.1 vCPU
- Free subdomain

---

## Option 6: Vercel (Serverless Functions)

**Best for:** HTTP-triggered tasks

### Setup

1. Install Vercel CLI: `npm i -g vercel`
2. Run `vercel` in project directory
3. Add environment variables in Vercel dashboard

### Limitations
- 10 second timeout (50s for Pro)
- Not ideal for long-running tasks
- Use with external cron service

---

## Environment Variables

All platforms need these environment variables:

### Required (at least one LLM)
```env
GEMINI_API_KEY_1=your_key
# or
GROQ_API_KEY_1=your_key
```

### Optional (Social Media)
```env
TWITTER_API_KEY=your_key
TWITTER_API_SECRET=your_secret
TWITTER_ACCESS_TOKEN=your_token
TWITTER_ACCESS_SECRET=your_secret
REDDIT_CLIENT_ID=your_id
REDDIT_CLIENT_SECRET=your_secret
REDDIT_USERNAME=your_username
REDDIT_PASSWORD=your_password
```

### Optional (Email)
```env
SMTP_HOST=smtp.zoho.eu
SMTP_USER=your_email
SMTP_PASSWORD=your_password
```

### Optional (State Persistence)
```env
GITHUB_TOKEN=your_token
GIST_STATE_ID=your_gist_id
```

---

## Monitoring

### Health Endpoints

All deployments expose:
- `GET /health` - Health check
- `GET /status` - Agent status

### Logs

- **GitHub Actions**: Actions tab → Workflow → Logs
- **Render**: Dashboard → Service → Logs
- **Railway**: Dashboard → Project → Deployments → Logs
- **Google Cloud Run**: Cloud Console → Cloud Run → Logs

### Alerts

Set up alerts for:
1. Service down (health check failures)
2. High error rates
3. API quota exhaustion

---

## Cost Optimization

### Free Tier Strategy

1. **Use GitHub Actions for scheduled tasks** (most efficient)
2. **Use Render/Railway for continuous operation**
3. **Rotate between multiple free tiers** if needed

### API Cost Management

1. Use free tier APIs first (Gemini, Groq)
2. Rotate between multiple API keys
3. Cache responses when possible
4. Use smaller models for simple tasks

---

## Troubleshooting

### Service Keeps Crashing
- Check memory usage (upgrade if needed)
- Review logs for errors
- Ensure environment variables are set

### API Rate Limits
- Add more API keys
- Implement backoff strategy
- Switch to alternative provider

### Service Sleeps (Render)
- Add external ping service
- Use cron-job.org to ping `/health`
- Upgrade to paid plan

---

## Recommended Setup

For maximum reliability with zero cost:

1. **Primary:** GitHub Actions (runs every 6 hours)
2. **Backup:** Render web service (for manual triggers)
3. **Monitoring:** UptimeRobot pinging both

This gives you:
- Scheduled automation
- Manual control
- High availability
- Zero cost

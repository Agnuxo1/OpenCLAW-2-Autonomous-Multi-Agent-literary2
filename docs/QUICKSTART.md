# Quick Start Guide - Autonomous Literary Agent

## Prerequisites

- Python 3.10 or higher
- pip package manager
- Git (for cloning)
- API keys (at least one LLM provider)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Agnuxo1/OpenCLAW-2-Autonomous-Multi-Agent-literary2.git
cd OpenCLAW-2-Autonomous-Multi-Agent-literary2
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate  # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```env
# At minimum, add one LLM provider
GEMINI_API_KEY_1=your_key_here
# or
GROQ_API_KEY_1=your_key_here
```

## Running the Agent

### Development Mode

```bash
python main.py
```

### Docker Mode

```bash
docker build -t literary-agent .
docker run -d --name literary-agent literary-agent
```

### GitHub Actions (24/7 Cloud)

1. Fork the repository
2. Add secrets in Settings > Secrets and variables > Actions
3. Enable GitHub Actions
4. The agent will run every 6 hours automatically

## First Run

When you first run the agent, you'll see:

```
╔═══════════════════════════════════════════════════════════════╗
║     📚 AUTONOMOUS LITERARY AGENT - Francisco Angulo          ║
║                                                               ║
║     The World's Most Advanced AI Literary Agent               ║
║     Operating 24/7 for Author Marketing & Promotion           ║
╚═══════════════════════════════════════════════════════════════╝

Initializing Autonomous Literary Agent...
LLM Provider initialized with 5 providers
Memory system loaded: 0 memories
Agent initialization complete!
Starting main agent loop...
```

## What the Agent Does

### Every 8 Hours (3x Daily)
- Generates social media posts for Twitter, Reddit, LinkedIn
- Posts about different books from the catalog
- Uses optimized hashtags and CTAs

### Daily
- Checks upcoming contest deadlines
- Runs self-improvement analysis
- Generates status reports

### Weekly
- Contacts new libraries worldwide
- Sends follow-up emails to previous contacts

## Monitoring

### Check Logs

```bash
tail -f literary_agent.log
```

### View Status Report

```bash
cat config/status_report.json
```

### Memory State

```bash
cat memory/memories.json
```

## Customization

### Add New Books

Edit `config/author_catalog.json`:

```json
{
  "novels": [
    {
      "id": "new_book",
      "title": "Your New Book",
      "genre": "Science Fiction",
      "hook_en": "Your hook here",
      ...
    }
  ]
}
```

### Modify Schedule

Edit `main.py`:

```python
self.schedules = {
    "social_media_morning": TaskSchedule("social_media_morning", 480),  # minutes
    ...
}
```

### Add New Platforms

1. Add credentials to `.env`
2. Update `skills/social_media.py`
3. Add new `post_to_<platform>()` method

## Troubleshooting

### "No API keys found"
- Ensure `.env` file exists and has at least one API key
- Check that keys are not wrapped in quotes

### "Rate limited"
- Agent will automatically rotate to next provider
- Add more API keys for better availability

### "Module not found"
- Run `pip install -r requirements.txt`
- Ensure virtual environment is activated

## Getting API Keys

### Free Tier APIs

| Provider | Free Tier | Get Key |
|----------|-----------|---------|
| Google Gemini | 15M tokens/day | [AI Studio](https://aistudio.google.com/) |
| Groq | 500K tokens/day | [Groq Console](https://console.groq.com/) |
| HuggingFace | 30K tokens/month | [HF Settings](https://huggingface.co/settings/tokens) |

### Social Media APIs

| Platform | Get Access |
|----------|------------|
| Twitter/X | [Developer Portal](https://developer.twitter.com/) |
| Reddit | [App Preferences](https://www.reddit.com/prefs/apps) |
| LinkedIn | [Developer Portal](https://www.linkedin.com/developers/) |

## Next Steps

1. Add your API keys
2. Run the agent locally to test
3. Deploy to GitHub Actions for 24/7 operation
4. Monitor logs and adjust settings
5. Add more books to the catalog

## Support

- GitHub Issues: [Report a bug](https://github.com/Agnuxo1/OpenCLAW-2-Autonomous-Multi-Agent-literary2/issues)
- Documentation: [Full docs](./docs/ARCHITECTURE.md)
- Author: [franciscoangulo.com](https://www.franciscoangulo.com)

# Autonomous Literary Agent - Architecture Documentation

## System Overview

The Autonomous Literary Agent is a sophisticated AI-powered system designed to operate 24/7, handling all professional literary agency tasks for author Francisco Angulo de Lafuente. It represents the world's most advanced AI literary agent implementation.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    AUTONOMOUS LITERARY AGENT                             │
│                         (main.py)                                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                     CORE COMPONENTS                               │   │
│  │  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐     │   │
│  │  │ LLM Provider   │  │ Memory System  │  │ Self-Improvement│     │   │
│  │  │ Rotator        │  │                │  │ Engine          │     │   │
│  │  │                │  │  - Episodic    │  │                 │     │   │
│  │  │ - Gemini (6)   │  │  - Semantic    │  │ - Analysis      │     │   │
│  │  │ - Groq (4)     │  │  - Procedural  │  │ - Strategy Gen  │     │   │
│  │  │ - NVIDIA (2)   │  │  - Strategic   │  │ - Reflection    │     │   │
│  │  │ - Z.ai (6)     │  │                │  │                 │     │   │
│  │  │ - HF (4)       │  │                │  │                 │     │   │
│  │  └────────────────┘  └────────────────┘  └────────────────┘     │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                     SKILL MODULES                                 │   │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌────────────┐ │   │
│  │  │ Social Media│ │ Library     │ │ Contest     │ │ Blog       │ │   │
│  │  │ Manager     │ │ Outreach    │ │ Submission  │ │ Writer     │ │   │
│  │  │             │ │             │ │             │ │            │ │   │
│  │  │ - Twitter   │ │ - Email     │ │ - Query     │ │ - Content  │ │   │
│  │  │ - Reddit    │ │ - Database  │ │ - Cover     │ │ - SEO      │ │   │
│  │  │ - LinkedIn  │ │ - Templates │ │ - Tracking  │ │ - Keywords │ │   │
│  │  │ - Facebook  │ │ - Campaigns │ │ - Calendar  │ │ - Research │ │   │
│  │  └─────────────┘ └─────────────┘ └─────────────┘ └────────────┘ │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                   TASK SCHEDULER                                  │   │
│  │  ┌─────────────────────────────────────────────────────────────┐ │   │
│  │  │ Task                  │ Interval    │ Schedule              │ │   │
│  │  ├─────────────────────────────────────────────────────────────┤ │   │
│  │  │ Social Media Morning  │ 8 hours     │ 09:00 CET             │ │   │
│  │  │ Social Media Afternoon│ 8 hours     │ 13:00 CET             │ │   │
│  │  │ Social Media Evening  │ 8 hours     │ 18:00 CET             │ │   │
│  │  │ Library Outreach      │ Weekly      │ Monday 10:00 CET      │ │   │
│  │  │ Contest Check         │ Daily       │ 12:00 CET             │ │   │
│  │  │ Self-Improvement      │ Daily       │ 23:00 CET             │ │   │
│  │  │ Status Report         │ 6 hours     │ Every 6 hours         │ │   │
│  │  └─────────────────────────────────────────────────────────────┘ │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      EXTERNAL INTEGRATIONS                               │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐     │
│  │ Twitter  │ │ Reddit   │ │ LinkedIn │ │ Facebook │ │ Mastodon │     │
│  │ API      │ │ API      │ │ API      │ │ API      │ │ API      │     │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘     │
│                                                                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐     │
│  │ Amazon   │ │ Apple    │ │ Kobo     │ │ Goodreads│ │ Libraries│     │
│  │ KDP      │ │ Books    │ │          │ │          │ │ (OverDrive)│   │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘     │
│                                                                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐                  │
│  │ Gemini   │ │ Groq     │ │ NVIDIA   │ │ Z.ai     │                  │
│  │ API      │ │ API      │ │ NIM API  │ │ API      │                  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘                  │
└─────────────────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. LLM Provider Rotator (`core/llm_provider.py`)

The multi-provider LLM rotation system maximizes free tier usage by automatically switching between API providers when limits are reached.

**Features:**
- Round-robin rotation between 22+ API keys
- Automatic rate limit detection and failover
- Usage tracking per key with daily reset
- Support for Gemini, Groq, NVIDIA NIM, Z.ai, and HuggingFace

**Key Classes:**
- `APIKey`: Tracks usage, status, and limits per key
- `Provider`: Base class for LLM providers
- `LLMProviderRotator`: Main rotation manager

### 2. Memory System (`core/memory.py`)

Comprehensive memory architecture inspired by cognitive science models.

**Memory Types:**
- **Episodic**: Specific events and interactions
- **Semantic**: Facts and knowledge about books, libraries, contests
- **Procedural**: Skills and procedures for tasks
- **Strategic**: Long-term strategies and goals

**Features:**
- Persistent storage to disk
- Tag-based and semantic search
- Task result tracking
- Lesson extraction and learning

### 3. Self-Improvement Engine

Meta-cognitive system that analyzes performance and generates improvements.

**Process:**
1. Analyze recent task outcomes
2. Identify failure patterns
3. Generate improvement strategies
4. Extract lessons from experiences
5. Update strategy memos

## Skill Modules

### 1. Social Media Manager (`skills/social_media.py`)

Handles all social media marketing activities.

**Platforms:**
- Twitter/X
- Reddit
- LinkedIn
- Facebook
- Instagram
- Mastodon

**Content Generation:**
- Platform-specific post templates
- Hashtag optimization
- Multi-language support (EN, ES, FR, IT)
- Book-specific marketing content

### 2. Library Outreach (`skills/library_outreach.py`)

Automated library contact system.

**Features:**
- Database of 30+ libraries worldwide
- Multi-language email templates
- Campaign tracking
- Follow-up automation
- Response tracking

### 3. Contest Submission (`skills/contest_submission.py`)

Manuscript submission management.

**Features:**
- Contest database with deadlines
- Query letter generation
- Cover letter templates
- Submission tracking
- Deadline calendar

## Data Flow

```
1. Task Scheduler triggers task
         │
         ▼
2. Agent loads relevant memories
         │
         ▼
3. LLM generates content/decision
         │
         ▼
4. Skill module executes action
         │
         ▼
5. Result recorded in memory
         │
         ▼
6. Self-improvement analyzes outcome
         │
         ▼
7. Memory saved to disk
```

## Deployment Options

### Local Development
```bash
python main.py
```

### Docker
```bash
docker build -t literary-agent .
docker run -d literary-agent
```

### GitHub Actions (24/7 Cloud)
- Runs every 6 hours via cron schedule
- State persisted to GitHub Gist
- Logs uploaded as artifacts

## Security Considerations

1. **API Keys**: Never committed to repository
2. **Environment Variables**: Used for all secrets
3. **Rate Limiting**: Built-in protection against API abuse
4. **Dry Run Mode**: Safe testing without real actions

## Performance Metrics

The agent tracks:
- Tasks completed/failed
- Posts made per platform
- Libraries contacted
- Submissions made
- Improvements applied
- LLM API usage per provider

## Extensibility

### Adding a New Platform

1. Create platform handler in `skills/social_media.py`
2. Add credentials to `.env`
3. Update `Platform` enum
4. Implement `post_to_<platform>()` method

### Adding a New Skill Module

1. Create new file in `skills/`
2. Implement skill class with async methods
3. Add to `AutonomousLiteraryAgent.__init__()`
4. Create task schedule entry
5. Implement `run_task_<skill>()` method

## Monitoring

- Log files: `logs/` directory
- Memory state: `memory/` directory
- Status reports: `config/status_report.json`
- GitHub Actions summaries

## Troubleshooting

### Common Issues

1. **"No API keys found"**: Set environment variables or create `.env` file
2. **Rate limiting**: Agent automatically rotates to next provider
3. **Memory not persisting**: Check file permissions on `memory/` directory
4. **Tasks not running**: Verify schedule times are in the future

## Future Enhancements

1. **Web Dashboard**: Real-time monitoring interface
2. **Email Marketing**: Newsletter automation
3. **Price Monitoring**: Dynamic pricing recommendations
4. **Review Tracking**: Sentiment analysis of reviews
5. **Agent Collaboration**: Multi-agent coordination

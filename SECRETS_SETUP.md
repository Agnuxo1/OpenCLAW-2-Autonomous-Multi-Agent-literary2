# GitHub Repository Secrets Setup Guide

This document provides instructions for setting up the required secrets for the Autonomous Literary Agent.

## How to Add Secrets

1. Go to: https://github.com/Agnuxo1/OpenCLAW-2-Autonomous-Multi-Agent-literary2/settings/secrets/actions
2. Click "New repository secret"
3. Add each secret one by one

## Required Secrets List

Copy and paste each secret name and value:

### LLM Provider API Keys

| Secret Name | Description |
|-------------|-------------|
| `ZAI_API_KEY_1` | Z.ai/GLM API Key 1 |
| `ZAI_API_KEY_2` | Z.ai/GLM API Key 2 |
| `ZAI_API_KEY_3` | Z.ai/GLM API Key 3 |
| `ZAI_API_KEY_4` | Z.ai/GLM API Key 4 |
| `ZAI_API_KEY_5` | Z.ai/GLM API Key 5 |
| `ZAI_API_KEY_6` | Z.ai/GLM API Key 6 |
| `GEMINI_API_KEY_1` | Google Gemini API Key 1 |
| `GEMINI_API_KEY_2` | Google Gemini API Key 2 |
| `GEMINI_API_KEY_3` | Google Gemini API Key 3 |
| `GEMINI_API_KEY_4` | Google Gemini API Key 4 |
| `GEMINI_API_KEY_5` | Google Gemini API Key 5 |
| `GEMINI_API_KEY_6` | Google Gemini API Key 6 |
| `GROQ_API_KEY_1` | Groq API Key 1 |
| `GROQ_API_KEY_2` | Groq API Key 2 |
| `GROQ_API_KEY_3` | Groq API Key 3 |
| `GROQ_API_KEY_4` | Groq API Key 4 |
| `GROQ_API_KEY_5` | Groq API Key 5 |
| `NVIDIA_API_KEY_1` | NVIDIA NIM API Key 1 |
| `NVIDIA_API_KEY_2` | NVIDIA NIM API Key 2 |
| `HUGGINGFACE_API_KEY_1` | HuggingFace API Key 1 |
| `HUGGINGFACE_API_KEY_2` | HuggingFace API Key 2 |
| `HUGGINGFACE_API_KEY_3` | HuggingFace API Key 3 |
| `HUGGINGFACE_API_KEY_4` | HuggingFace API Key 4 |

### Search APIs

| Secret Name | Description |
|-------------|-------------|
| `BRAVE_API_KEY` | Brave Search API Key |

### GitHub

| Secret Name | Description |
|-------------|-------------|
| `GITHUB_TOKEN` | GitHub Personal Access Token |

### Social Media

| Secret Name | Description |
|-------------|-------------|
| `REDDIT_USERNAME` | Reddit Username |
| `REDDIT_PASSWORD` | Reddit Password |
| `MOLTBOOK_API_KEY` | Moltbook API Key |

### Email Configuration

| Secret Name | Description |
|-------------|-------------|
| `SMTP_HOST` | SMTP Server Host |
| `SMTP_PORT` | SMTP Server Port |
| `SMTP_USER` | SMTP Username |
| `SMTP_PASSWORD` | SMTP Password |
| `EMAIL_FROM` | From Email Address |

### Kaggle

| Secret Name | Description |
|-------------|-------------|
| `KAGGLE_USERNAME` | Kaggle Username |
| `KAGGLE_KEY` | Kaggle API Key |

### Agent Configuration

| Secret Name | Description |
|-------------|-------------|
| `AUTHOR_NAME` | Author Name |
| `AUTHOR_EMAIL` | Author Email |
| `AGENT_NAME` | Agent Name |

## Quick Setup Script

For local development, copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
# Edit .env with your API keys
```

## Security Notes

- Never commit `.env` files to the repository
- All secrets are automatically loaded from GitHub Secrets in CI/CD
- The `.gitignore` file excludes `.env` and other sensitive files

# Autonomous Literary Agent - Dockerfile
# Multi-stage build for optimized production image

# ===========================================
# Stage 1: Python Runtime
# ===========================================
FROM python:3.11-slim as python-base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# ===========================================
# Stage 2: Dependencies
# ===========================================
FROM python-base as dependencies

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# ===========================================
# Stage 3: Application
# ===========================================
FROM dependencies as application

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/memory /app/logs /app/library_data /app/submission_data /app/config

# Set permissions
RUN chmod +x main.py

# Create non-root user for security
RUN useradd -m -u 1000 literaryagent && \
    chown -R literaryagent:literaryagent /app
USER literaryagent

# Health check
HEALTHCHECK --interval=5m --timeout=30s --start-period=1m --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Expose port for health endpoint
EXPOSE 8080

# Default command
CMD ["python", "main.py"]

# ===========================================
# Stage 4: Development (optional)
# ===========================================
FROM application as development

USER root
RUN pip install pytest pytest-asyncio black flake8 mypy
USER literaryagent

CMD ["python", "main.py"]

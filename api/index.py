"""
Vercel Serverless Function Handler for Literary Agent
This provides an HTTP endpoint for the agent and health checks.
"""

import json
import asyncio
from datetime import datetime

def handler(request):
    """Handle incoming requests"""
    
    # Health check endpoint
    if request.path == "/health":
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "agent": "Autonomous Literary Agent",
                "author": "Francisco Angulo de Lafuente"
            })
        }
    
    # Status endpoint
    if request.path == "/status":
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "status": "running",
                "uptime": "active",
                "tasks_completed": 0,
                "last_run": datetime.now().isoformat()
            })
        }
    
    # Trigger agent task (for cron jobs)
    if request.path == "/run" and request.method == "POST":
        # In production, this would trigger an agent cycle
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "message": "Agent task triggered",
                "timestamp": datetime.now().isoformat()
            })
        }
    
    # Default response
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({
            "name": "Autonomous Literary Agent",
            "version": "1.0.0",
            "author": "Francisco Angulo de Lafuente",
            "endpoints": ["/health", "/status", "/run"],
            "documentation": "https://github.com/Agnuxo1/OpenCLAW-2-Autonomous-Multi-Agent-literary2"
        })
    }

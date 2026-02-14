#!/usr/bin/env python3
"""
Autonomous Literary Agent - Main Entry Point
24/7 autonomous agent for literary marketing, submissions, and promotion.

This is the world's most advanced AI literary agent, capable of:
- Social media marketing across multiple platforms
- Library outreach worldwide
- Contest and publisher submissions
- Self-improvement through reflection
- Memory and learning from experiences
"""

import os
import sys
import json
import asyncio
import signal
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field
from enum import Enum
import random

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from env_adapter import adapt_env_vars
from core.llm_provider import LLMProviderRotator, load_api_keys_from_env
from core.memory import MemorySystem, SelfImprovementEngine, MemoryType, OutcomeType, TaskResult
from skills.social_media import SocialMediaManager, BOOK_CATALOG
from skills.library_outreach import LibraryOutreachManager
from skills.contest_submission import SubmissionManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('literary_agent.log')
    ]
)
logger = logging.getLogger(__name__)


class AgentState(Enum):
    INITIALIZING = "initializing"
    RUNNING = "running"
    PAUSED = "paused"
    IMPROVING = "improving"
    SHUTDOWN = "shutdown"


@dataclass
class TaskSchedule:
    """Defines when tasks should run"""
    task_name: str
    interval_minutes: int
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    enabled: bool = True
    
    def should_run(self) -> bool:
        if not self.enabled:
            return False
        if self.next_run is None:
            return True
        return datetime.now() >= self.next_run
    
    def mark_completed(self):
        self.last_run = datetime.now()
        self.next_run = self.last_run + timedelta(minutes=self.interval_minutes)


class AutonomousLiteraryAgent:
    """
    The main autonomous literary agent class.
    Coordinates all skills and runs 24/7 with self-improvement capabilities.
    """
    
    def __init__(self, config_path: str = "./config"):
        self.config_path = config_path
        self.state = AgentState.INITIALIZING
        self.start_time = datetime.now()
        
        # Core components
        self.llm_provider: Optional[LLMProviderRotator] = None
        self.memory: Optional[MemorySystem] = None
        self.improvement_engine: Optional[SelfImprovementEngine] = None
        
        # Skill modules
        self.social_media: Optional[SocialMediaManager] = None
        self.library_outreach: Optional[LibraryOutreachManager] = None
        self.submission_manager: Optional[SubmissionManager] = None
        
        # Task scheduling
        self.schedules: Dict[str, TaskSchedule] = {
            "social_media_morning": TaskSchedule("social_media_morning", 480),  # 8 hours
            "social_media_afternoon": TaskSchedule("social_media_afternoon", 480),
            "social_media_evening": TaskSchedule("social_media_evening", 480),
            "library_outreach": TaskSchedule("library_outreach", 10080),  # Weekly
            "contest_check": TaskSchedule("contest_check", 1440),  # Daily
            "self_improvement": TaskSchedule("self_improvement", 1440),  # Daily
            "status_report": TaskSchedule("status_report", 360),  # 6 hours
            "blog_content": TaskSchedule("blog_content", 10080),  # Weekly
        }
        
        # Statistics
        self.stats = {
            "tasks_completed": 0,
            "tasks_failed": 0,
            "posts_made": 0,
            "libraries_contacted": 0,
            "submissions_made": 0,
            "improvements_applied": 0,
        }
        
        # Shutdown flag
        self._shutdown = False
        
        # Ensure directories exist
        os.makedirs(config_path, exist_ok=True)
        os.makedirs("./memory", exist_ok=True)
        os.makedirs("./logs", exist_ok=True)
    
    async def initialize(self):
        """Initialize all components"""
        logger.info("Initializing Autonomous Literary Agent...")
        
        # Load API keys
        adapt_env_vars()  # Fix: Adapt numbered keys to CSV format
        api_config = load_api_keys_from_env()
        
        if not api_config:
            logger.warning("No API keys found in environment. Agent will run in limited mode.")
        else:
            # Initialize LLM provider
            self.llm_provider = LLMProviderRotator(api_config)
            logger.info(f"LLM Provider initialized with {len(self.llm_provider.providers)} providers")
        
        # Initialize memory system
        self.memory = MemorySystem("./memory")
        logger.info(f"Memory system loaded: {self.memory.stats['total_memories']} memories")
        
        # Initialize improvement engine
        if self.llm_provider:
            self.improvement_engine = SelfImprovementEngine(self.memory, self.llm_provider)
        
        # Initialize skill modules
        self.social_media = SocialMediaManager(self.llm_provider)
        self.library_outreach = LibraryOutreachManager(self.llm_provider, "./library_data")
        self.submission_manager = SubmissionManager(self.llm_provider, "./submission_data")
        
        # Store initialization in memory
        self.memory.store(
            content="Agent initialized successfully",
            memory_type=MemoryType.EPISODIC,
            tags=["initialization", "startup"],
            importance=0.8
        )
        
        self.state = AgentState.RUNNING
        logger.info("Agent initialization complete!")
    
    async def run_task_social_media(self, time_slot: str = "morning"):
        """Run social media posting task"""
        logger.info(f"Running social media task ({time_slot})...")
        
        task_id = f"social_{time_slot}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        started = datetime.now().isoformat()
        
        try:
            # Select books for this slot
            books = random.sample(BOOK_CATALOG, min(2, len(BOOK_CATALOG)))
            
            results = []
            async with self.social_media as sm:
                for book in books:
                    # Generate and post content
                    tweet = sm.content_generator.generate_tweet(book, "EN")
                    # In production, would actually post
                    # post = await sm.post(Platform.TWITTER, tweet)
                    
                    results.append({
                        "book": book.title,
                        "content_generated": True,
                        "platform": "twitter"
                    })
                    
                    self.stats["posts_made"] += 1
            
            # Record success
            task_result = TaskResult(
                task_id=task_id,
                task_type="social_media",
                started=started,
                completed=datetime.now().isoformat(),
                outcome=OutcomeType.SUCCESS,
                details={"posts": results, "time_slot": time_slot},
                metrics={"posts_count": len(results)}
            )
            self.memory.record_task_result(task_result)
            self.stats["tasks_completed"] += 1
            
            logger.info(f"Social media task complete: {len(results)} posts generated")
            
        except Exception as e:
            logger.error(f"Social media task failed: {e}")
            
            task_result = TaskResult(
                task_id=task_id,
                task_type="social_media",
                started=started,
                completed=datetime.now().isoformat(),
                outcome=OutcomeType.FAILURE,
                details={},
                errors=[str(e)]
            )
            self.memory.record_task_result(task_result)
            self.stats["tasks_failed"] += 1
    
    async def run_task_library_outreach(self):
        """Run library outreach task"""
        logger.info("Running library outreach task...")
        
        task_id = f"library_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        started = datetime.now().isoformat()
        
        try:
            async with self.library_outreach as lo:
                # Run outreach campaign (dry run for safety)
                results = await lo.run_outreach_campaign(
                    max_libraries=5,
                    dry_run=True  # Set to False in production
                )
            
            self.stats["libraries_contacted"] += results.get("total_sent", 0)
            
            task_result = TaskResult(
                task_id=task_id,
                task_type="library_outreach",
                started=started,
                completed=datetime.now().isoformat(),
                outcome=OutcomeType.SUCCESS,
                details=results,
                metrics={"libraries_contacted": results.get("total_sent", 0)}
            )
            self.memory.record_task_result(task_result)
            self.stats["tasks_completed"] += 1
            
            logger.info(f"Library outreach complete: {results.get('total_sent', 0)} libraries")
            
        except Exception as e:
            logger.error(f"Library outreach task failed: {e}")
            
            task_result = TaskResult(
                task_id=task_id,
                task_type="library_outreach",
                started=started,
                completed=datetime.now().isoformat(),
                outcome=OutcomeType.FAILURE,
                details={},
                errors=[str(e)]
            )
            self.memory.record_task_result(task_result)
            self.stats["tasks_failed"] += 1
    
    async def run_task_contest_check(self):
        """Check for upcoming contest deadlines and prepare submissions"""
        logger.info("Running contest check task...")
        
        task_id = f"contest_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        started = datetime.now().isoformat()
        
        try:
            calendar = self.submission_manager.get_submission_calendar()
            
            upcoming = []
            for month, contests in calendar.items():
                for contest in contests:
                    upcoming.append(contest)
            
            # Store in memory
            self.memory.store(
                content=f"Found {len(upcoming)} upcoming contest deadlines",
                memory_type=MemoryType.SEMANTIC,
                metadata={"contests": upcoming[:10]},
                tags=["contests", "deadlines"],
                importance=0.7
            )
            
            task_result = TaskResult(
                task_id=task_id,
                task_type="contest_check",
                started=started,
                completed=datetime.now().isoformat(),
                outcome=OutcomeType.SUCCESS,
                details={"upcoming_contests": len(upcoming)},
            )
            self.memory.record_task_result(task_result)
            self.stats["tasks_completed"] += 1
            
            logger.info(f"Contest check complete: {len(upcoming)} upcoming deadlines")
            
        except Exception as e:
            logger.error(f"Contest check task failed: {e}")
            self.stats["tasks_failed"] += 1
    
    async def run_task_self_improvement(self):
        """Run self-improvement cycle"""
        logger.info("Running self-improvement task...")
        
        if not self.improvement_engine:
            logger.warning("Self-improvement engine not available")
            return
        
        self.state = AgentState.IMPROVING
        
        task_id = f"improve_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        started = datetime.now().isoformat()
        
        try:
            results = await self.improvement_engine.run_improvement_cycle()
            
            self.stats["improvements_applied"] += len(results.get("strategies_created", []))
            
            task_result = TaskResult(
                task_id=task_id,
                task_type="self_improvement",
                started=started,
                completed=datetime.now().isoformat(),
                outcome=OutcomeType.SUCCESS,
                details=results,
                metrics={
                    "strategies_created": len(results.get("strategies_created", [])),
                    "lessons_extracted": len(results.get("lessons_extracted", []))
                }
            )
            self.memory.record_task_result(task_result)
            self.stats["tasks_completed"] += 1
            
            logger.info(f"Self-improvement complete: {len(results.get('lessons_extracted', []))} lessons learned")
            
        except Exception as e:
            logger.error(f"Self-improvement task failed: {e}")
            self.stats["tasks_failed"] += 1
        
        self.state = AgentState.RUNNING
    
    async def run_task_status_report(self):
        """Generate and log status report"""
        logger.info("Generating status report...")
        
        uptime = datetime.now() - self.start_time
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "state": self.state.value,
            "uptime_hours": uptime.total_seconds() / 3600,
            "statistics": self.stats,
            "memory_summary": self.memory.get_summary(),
            "llm_status": self.llm_provider.get_status_report() if self.llm_provider else None,
            "next_tasks": [
                {"task": name, "next_run": schedule.next_run.isoformat() if schedule.next_run else "pending"}
                for name, schedule in self.schedules.items()
                if schedule.enabled
            ]
        }
        
        # Save report
        report_path = os.path.join(self.config_path, "status_report.json")
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"Status report saved. Uptime: {uptime}")
        logger.info(f"Stats: {json.dumps(self.stats, indent=2)}")
        
        return report
    
    async def run_main_loop(self):
        """Main agent loop - runs continuously"""
        logger.info("Starting main agent loop...")
        
        # Schedule initial tasks
        now = datetime.now()
        self.schedules["social_media_morning"].next_run = now.replace(hour=9, minute=0, second=0)
        self.schedules["social_media_afternoon"].next_run = now.replace(hour=13, minute=0, second=0)
        self.schedules["social_media_evening"].next_run = now.replace(hour=18, minute=0, second=0)
        self.schedules["library_outreach"].next_run = now + timedelta(hours=1)
        self.schedules["contest_check"].next_run = now + timedelta(minutes=30)
        self.schedules["self_improvement"].next_run = now.replace(hour=23, minute=0, second=0)
        self.schedules["status_report"].next_run = now + timedelta(minutes=5)
        
        while not self._shutdown:
            try:
                # Check each scheduled task
                for task_name, schedule in self.schedules.items():
                    if schedule.should_run():
                        logger.info(f"Running scheduled task: {task_name}")
                        
                        if task_name.startswith("social_media"):
                            time_slot = task_name.split("_")[-1]
                            await self.run_task_social_media(time_slot)
                        elif task_name == "library_outreach":
                            await self.run_task_library_outreach()
                        elif task_name == "contest_check":
                            await self.run_task_contest_check()
                        elif task_name == "self_improvement":
                            await self.run_task_self_improvement()
                        elif task_name == "status_report":
                            await self.run_task_status_report()
                        
                        schedule.mark_completed()
                        
                        # Save memory after each task
                        self.memory.save_to_disk()
                
                # Sleep before next check
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                await asyncio.sleep(60)
        
        logger.info("Main loop ended")
    
    async def shutdown(self):
        """Graceful shutdown"""
        logger.info("Initiating graceful shutdown...")
        self._shutdown = True
        self.state = AgentState.SHUTDOWN
        
        # Save final state
        self.memory.store(
            content="Agent shutdown initiated",
            memory_type=MemoryType.EPISODIC,
            tags=["shutdown"],
            importance=0.9
        )
        self.memory.save_to_disk()
        
        # Save LLM state
        if self.llm_provider:
            self.llm_provider.save_state("./memory/llm_state.json")
        
        logger.info("Shutdown complete")
    
    def handle_signal(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}")
        asyncio.create_task(self.shutdown())


async def main():
    """Main entry point"""
    agent = AutonomousLiteraryAgent()
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, agent.handle_signal)
    signal.signal(signal.SIGTERM, agent.handle_signal)
    
    try:
        # Initialize
        await agent.initialize()
        
        # Run main loop
        await agent.run_main_loop()
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        await agent.shutdown()
        raise
    
    finally:
        logger.info("Agent stopped")


if __name__ == "__main__":
    print("""
    ╔═══════════════════════════════════════════════════════════════╗
    ║     📚 AUTONOMOUS LITERARY AGENT - Francisco Angulo          ║
    ║                                                               ║
    ║     The World's Most Advanced AI Literary Agent               ║
    ║     Operating 24/7 for Author Marketing & Promotion           ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)
    
    asyncio.run(main())

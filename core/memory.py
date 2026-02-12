#!/usr/bin/env python3
"""
Autonomous Literary Agent Memory System
Persistent memory with self-improvement and learning capabilities.
"""

import os
import json
import hashlib
import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging
from collections import defaultdict
import aiohttp

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MemoryType(Enum):
    EPISODIC = "episodic"      # Specific events/interactions
    SEMANTIC = "semantic"       # Facts and knowledge
    PROCEDURAL = "procedural"   # Skills and procedures
    STRATEGIC = "strategic"     # Long-term strategies


class OutcomeType(Enum):
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILURE = "failure"
    PENDING = "pending"


@dataclass
class MemoryEntry:
    """Single memory entry"""
    id: str
    type: MemoryType
    timestamp: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    importance: float = 0.5  # 0-1 scale
    access_count: int = 0
    last_accessed: str = field(default_factory=lambda: datetime.now().isoformat())
    outcome: Optional[OutcomeType] = None
    lessons_learned: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "type": self.type.value,
            "timestamp": self.timestamp,
            "content": self.content,
            "metadata": self.metadata,
            "tags": self.tags,
            "importance": self.importance,
            "access_count": self.access_count,
            "last_accessed": self.last_accessed,
            "outcome": self.outcome.value if self.outcome else None,
            "lessons_learned": self.lessons_learned
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'MemoryEntry':
        return cls(
            id=data["id"],
            type=MemoryType(data["type"]),
            timestamp=data["timestamp"],
            content=data["content"],
            metadata=data.get("metadata", {}),
            tags=data.get("tags", []),
            importance=data.get("importance", 0.5),
            access_count=data.get("access_count", 0),
            last_accessed=data.get("last_accessed", datetime.now().isoformat()),
            outcome=OutcomeType(data["outcome"]) if data.get("outcome") else None,
            lessons_learned=data.get("lessons_learned", [])
        )


@dataclass
class StrategyMemo:
    """Strategic memory entry for long-term planning"""
    id: str
    created: str
    strategy: str
    rationale: str
    expected_outcome: str
    actual_outcome: Optional[str] = None
    effectiveness_score: Optional[float] = None
    iterations: int = 0
    improvements: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'StrategyMemo':
        return cls(**data)


@dataclass
class TaskResult:
    """Result of a completed task"""
    task_id: str
    task_type: str
    started: str
    completed: str
    outcome: OutcomeType
    details: Dict[str, Any]
    metrics: Dict[str, float] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "task_id": self.task_id,
            "task_type": self.task_type,
            "started": self.started,
            "completed": self.completed,
            "outcome": self.outcome.value,
            "details": self.details,
            "metrics": self.metrics,
            "errors": self.errors
        }


class MemorySystem:
    """
    Comprehensive memory system for the autonomous literary agent.
    Implements episodic, semantic, procedural, and strategic memory.
    """
    
    def __init__(self, storage_path: str = "./memory"):
        self.storage_path = storage_path
        self.memories: Dict[str, MemoryEntry] = {}
        self.strategies: Dict[str, StrategyMemo] = {}
        self.task_history: List[TaskResult] = []
        self.knowledge_base: Dict[str, Any] = {}
        self.skill_registry: Dict[str, Dict] = {}
        
        # Indices for fast retrieval
        self.tag_index: Dict[str, List[str]] = defaultdict(list)
        self.type_index: Dict[MemoryType, List[str]] = defaultdict(list)
        self.time_index: Dict[str, List[str]] = defaultdict(list)  # Date -> IDs
        
        # Learning parameters
        self.learning_rate = 0.1
        self.importance_decay = 0.95
        self.max_memories = 10000
        
        # Statistics
        self.stats = {
            "total_memories": 0,
            "successful_tasks": 0,
            "failed_tasks": 0,
            "strategies_improved": 0,
            "lessons_learned": 0
        }
        
        os.makedirs(storage_path, exist_ok=True)
        self._load_from_disk()
    
    def _generate_id(self, content: str) -> str:
        """Generate unique ID for memory entry"""
        timestamp = datetime.now().isoformat()
        hash_input = f"{content}{timestamp}".encode()
        return hashlib.md5(hash_input).hexdigest()[:12]
    
    def store(self, content: str, memory_type: MemoryType, 
              metadata: Dict = None, tags: List[str] = None,
              importance: float = 0.5) -> str:
        """Store a new memory entry"""
        memory_id = self._generate_id(content)
        
        entry = MemoryEntry(
            id=memory_id,
            type=memory_type,
            timestamp=datetime.now().isoformat(),
            content=content,
            metadata=metadata or {},
            tags=tags or [],
            importance=importance
        )
        
        self.memories[memory_id] = entry
        
        # Update indices
        for tag in entry.tags:
            self.tag_index[tag].append(memory_id)
        self.type_index[memory_type].append(memory_id)
        
        date_key = datetime.now().strftime("%Y-%m-%d")
        self.time_index[date_key].append(memory_id)
        
        self.stats["total_memories"] += 1
        
        # Manage memory limit
        if len(self.memories) > self.max_memories:
            self._consolidate_memories()
        
        return memory_id
    
    def retrieve(self, memory_id: str) -> Optional[MemoryEntry]:
        """Retrieve a memory by ID"""
        if memory_id in self.memories:
            entry = self.memories[memory_id]
            entry.access_count += 1
            entry.last_accessed = datetime.now().isoformat()
            return entry
        return None
    
    def search_by_tags(self, tags: List[str], limit: int = 10) -> List[MemoryEntry]:
        """Search memories by tags"""
        matching_ids = set()
        for tag in tags:
            matching_ids.update(self.tag_index.get(tag, []))
        
        results = [self.memories[mid] for mid in matching_ids if mid in self.memories]
        results.sort(key=lambda x: x.importance, reverse=True)
        return results[:limit]
    
    def search_by_type(self, memory_type: MemoryType, limit: int = 10) -> List[MemoryEntry]:
        """Search memories by type"""
        ids = self.type_index.get(memory_type, [])
        results = [self.memories[mid] for mid in ids if mid in self.memories]
        results.sort(key=lambda x: x.timestamp, reverse=True)
        return results[:limit]
    
    def search_by_date(self, date_str: str) -> List[MemoryEntry]:
        """Search memories by date (YYYY-MM-DD format)"""
        ids = self.time_index.get(date_str, [])
        return [self.memories[mid] for mid in ids if mid in self.memories]
    
    def search_semantic(self, query: str, limit: int = 10) -> List[MemoryEntry]:
        """Simple semantic search (keyword-based)"""
        query_words = set(query.lower().split())
        scored_memories = []
        
        for entry in self.memories.values():
            content_words = set(entry.content.lower().split())
            score = len(query_words & content_words)
            if score > 0:
                scored_memories.append((score, entry))
        
        scored_memories.sort(key=lambda x: x[0], reverse=True)
        return [entry for _, entry in scored_memories[:limit]]
    
    def record_task_result(self, result: TaskResult):
        """Record the result of a completed task"""
        self.task_history.append(result)
        
        if result.outcome == OutcomeType.SUCCESS:
            self.stats["successful_tasks"] += 1
        elif result.outcome == OutcomeType.FAILURE:
            self.stats["failed_tasks"] += 1
        
        # Store as episodic memory
        self.store(
            content=f"Task: {result.task_type} - Outcome: {result.outcome.value}",
            memory_type=MemoryType.EPISODIC,
            metadata=result.to_dict(),
            tags=["task", result.task_type, result.outcome.value],
            importance=0.7 if result.outcome == OutcomeType.SUCCESS else 0.8
        )
    
    def create_strategy(self, strategy: str, rationale: str, 
                        expected_outcome: str) -> str:
        """Create a new strategic memory"""
        strategy_id = self._generate_id(strategy)
        
        memo = StrategyMemo(
            id=strategy_id,
            created=datetime.now().isoformat(),
            strategy=strategy,
            rationale=rationale,
            expected_outcome=expected_outcome
        )
        
        self.strategies[strategy_id] = memo
        return strategy_id
    
    def update_strategy(self, strategy_id: str, actual_outcome: str,
                        effectiveness: float, improvement: str = None):
        """Update strategy with results"""
        if strategy_id not in self.strategies:
            return
        
        memo = self.strategies[strategy_id]
        memo.actual_outcome = actual_outcome
        memo.effectiveness_score = effectiveness
        memo.iterations += 1
        
        if improvement:
            memo.improvements.append(improvement)
            self.stats["strategies_improved"] += 1
    
    def learn_lesson(self, memory_id: str, lesson: str):
        """Add a learned lesson to a memory entry"""
        if memory_id in self.memories:
            entry = self.memories[memory_id]
            entry.lessons_learned.append(lesson)
            self.stats["lessons_learned"] += 1
            
            # Store as semantic memory
            self.store(
                content=f"Lesson: {lesson}",
                memory_type=MemoryType.SEMANTIC,
                tags=["lesson", "learning"],
                importance=0.9
            )
    
    def get_recent_lessons(self, limit: int = 10) -> List[str]:
        """Get recently learned lessons"""
        lessons = []
        for entry in self.memories.values():
            lessons.extend(entry.lessons_learned)
        return lessons[-limit:]
    
    def get_successful_patterns(self, task_type: str = None) -> List[Dict]:
        """Analyze successful tasks to find patterns"""
        successful = [
            t for t in self.task_history 
            if t.outcome == OutcomeType.SUCCESS
        ]
        
        if task_type:
            successful = [t for t in successful if t.task_type == task_type]
        
        patterns = []
        for task in successful:
            patterns.append({
                "task_type": task.task_type,
                "details": task.details,
                "metrics": task.metrics
            })
        
        return patterns
    
    def get_failure_analysis(self, task_type: str = None) -> Dict:
        """Analyze failed tasks to identify issues"""
        failed = [
            t for t in self.task_history 
            if t.outcome == OutcomeType.FAILURE
        ]
        
        if task_type:
            failed = [t for t in failed if t.task_type == task_type]
        
        error_counts = defaultdict(int)
        for task in failed:
            for error in task.errors:
                error_counts[error] += 1
        
        return {
            "total_failures": len(failed),
            "common_errors": dict(error_counts),
            "recent_failures": [
                {"task_id": t.task_id, "errors": t.errors}
                for t in failed[-5:]
            ]
        }
    
    def _consolidate_memories(self):
        """Consolidate old/low-importance memories"""
        # Sort by importance and access count
        sorted_memories = sorted(
            self.memories.items(),
            key=lambda x: (x[1].importance, x[1].access_count)
        )
        
        # Remove lowest 10%
        to_remove = int(len(sorted_memories) * 0.1)
        for memory_id, _ in sorted_memories[:to_remove]:
            self._remove_memory(memory_id)
    
    def _remove_memory(self, memory_id: str):
        """Remove a memory and update indices"""
        if memory_id not in self.memories:
            return
        
        entry = self.memories[memory_id]
        
        # Update indices
        for tag in entry.tags:
            if memory_id in self.tag_index[tag]:
                self.tag_index[tag].remove(memory_id)
        if memory_id in self.type_index[entry.type]:
            self.type_index[entry.type].remove(memory_id)
        
        date_key = datetime.fromisoformat(entry.timestamp).strftime("%Y-%m-%d")
        if memory_id in self.time_index[date_key]:
            self.time_index[date_key].remove(memory_id)
        
        del self.memories[memory_id]
    
    def _load_from_disk(self):
        """Load memories from disk"""
        try:
            # Load memories
            memories_file = os.path.join(self.storage_path, "memories.json")
            if os.path.exists(memories_file):
                with open(memories_file, 'r') as f:
                    data = json.load(f)
                    for mid, entry_data in data.get("memories", {}).items():
                        self.memories[mid] = MemoryEntry.from_dict(entry_data)
                    self.stats = data.get("stats", self.stats)
            
            # Load strategies
            strategies_file = os.path.join(self.storage_path, "strategies.json")
            if os.path.exists(strategies_file):
                with open(strategies_file, 'r') as f:
                    data = json.load(f)
                    for sid, memo_data in data.items():
                        self.strategies[sid] = StrategyMemo.from_dict(memo_data)
            
            # Load task history
            history_file = os.path.join(self.storage_path, "task_history.json")
            if os.path.exists(history_file):
                with open(history_file, 'r') as f:
                    data = json.load(f)
                    for task_data in data:
                        task_data["outcome"] = OutcomeType(task_data["outcome"])
                        self.task_history.append(TaskResult(**task_data))
            
            # Rebuild indices
            self._rebuild_indices()
            
            logger.info(f"Loaded {len(self.memories)} memories, {len(self.strategies)} strategies")
            
        except Exception as e:
            logger.error(f"Error loading memories: {e}")
    
    def _rebuild_indices(self):
        """Rebuild search indices from memories"""
        self.tag_index.clear()
        self.type_index.clear()
        self.time_index.clear()
        
        for mid, entry in self.memories.items():
            for tag in entry.tags:
                self.tag_index[tag].append(mid)
            self.type_index[entry.type].append(mid)
            date_key = datetime.fromisoformat(entry.timestamp).strftime("%Y-%m-%d")
            self.time_index[date_key].append(mid)
    
    def save_to_disk(self):
        """Save all memories to disk"""
        try:
            # Save memories
            memories_file = os.path.join(self.storage_path, "memories.json")
            with open(memories_file, 'w') as f:
                json.dump({
                    "memories": {mid: entry.to_dict() for mid, entry in self.memories.items()},
                    "stats": self.stats
                }, f, indent=2)
            
            # Save strategies
            strategies_file = os.path.join(self.storage_path, "strategies.json")
            with open(strategies_file, 'w') as f:
                json.dump({sid: memo.to_dict() for sid, memo in self.strategies.items()}, f, indent=2)
            
            # Save task history
            history_file = os.path.join(self.storage_path, "task_history.json")
            with open(history_file, 'w') as f:
                json.dump([t.to_dict() for t in self.task_history], f, indent=2)
            
            logger.info("Memories saved to disk")
            
        except Exception as e:
            logger.error(f"Error saving memories: {e}")
    
    def get_summary(self) -> Dict:
        """Get summary of memory system state"""
        return {
            "total_memories": len(self.memories),
            "total_strategies": len(self.strategies),
            "total_tasks": len(self.task_history),
            "stats": self.stats,
            "memory_types": {
                mtype.value: len(ids) 
                for mtype, ids in self.type_index.items()
            },
            "top_tags": sorted(
                [(tag, len(ids)) for tag, ids in self.tag_index.items()],
                key=lambda x: x[1],
                reverse=True
            )[:10]
        }


class SelfImprovementEngine:
    """
    Self-improvement engine that analyzes past performance
    and generates improvement strategies.
    """
    
    def __init__(self, memory: MemorySystem, llm_provider):
        self.memory = memory
        self.llm_provider = llm_provider
        self.improvement_history: List[Dict] = []
    
    async def analyze_performance(self) -> Dict:
        """Analyze overall performance and identify areas for improvement"""
        summary = self.memory.get_summary()
        failure_analysis = self.memory.get_failure_analysis()
        successful_patterns = self.memory.get_successful_patterns()
        
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "performance_metrics": {
                "success_rate": summary["stats"]["successful_tasks"] / max(1, summary["stats"]["successful_tasks"] + summary["stats"]["failed_tasks"]),
                "total_tasks": summary["stats"]["successful_tasks"] + summary["stats"]["failed_tasks"],
                "lessons_learned": summary["stats"]["lessons_learned"]
            },
            "failure_analysis": failure_analysis,
            "successful_patterns_count": len(successful_patterns),
            "improvement_areas": []
        }
        
        # Identify improvement areas
        if failure_analysis["total_failures"] > 5:
            analysis["improvement_areas"].append({
                "area": "error_reduction",
                "priority": "high",
                "details": failure_analysis["common_errors"]
            })
        
        if summary["stats"]["lessons_learned"] < 10:
            analysis["improvement_areas"].append({
                "area": "learning",
                "priority": "medium",
                "details": "Need to extract more lessons from experiences"
            })
        
        return analysis
    
    async def generate_improvement_strategy(self, area: str, details: Dict) -> str:
        """Generate an improvement strategy for a specific area"""
        prompt = f"""As an AI literary agent, I need to improve in the following area:

Area: {area}
Details: {json.dumps(details, indent=2)}

Recent lessons learned:
{chr(10).join(self.memory.get_recent_lessons(5))}

Generate a specific, actionable improvement strategy that I can implement.
Focus on concrete steps and measurable outcomes.
"""
        
        result = await self.llm_provider.generate(prompt)
        
        if result["success"]:
            strategy_id = self.memory.create_strategy(
                strategy=result["text"],
                rationale=f"Improvement for {area}",
                expected_outcome=f"Reduced errors in {area}"
            )
            return strategy_id
        
        return None
    
    async def reflect_on_task(self, task_result: TaskResult) -> List[str]:
        """Reflect on a completed task and extract lessons"""
        prompt = f"""Reflect on this completed task and extract lessons learned:

Task Type: {task_result.task_type}
Outcome: {task_result.outcome.value}
Details: {json.dumps(task_result.details, indent=2)}
Errors: {task_result.errors}

What lessons can be learned from this task?
What could be done differently next time?
Provide 2-3 specific, actionable lessons.
"""
        
        result = await self.llm_provider.generate(prompt)
        
        lessons = []
        if result["success"]:
            # Parse lessons from response
            lines = result["text"].strip().split('\n')
            for line in lines:
                line = line.strip()
                if line and (line.startswith('-') or line.startswith('•') or line.startswith('*')):
                    lesson = line.lstrip('-•* ').strip()
                    if lesson:
                        lessons.append(lesson)
        
        return lessons
    
    async def run_improvement_cycle(self) -> Dict:
        """Run a complete self-improvement cycle"""
        logger.info("Starting self-improvement cycle...")
        
        # 1. Analyze performance
        analysis = await self.analyze_performance()
        
        # 2. Generate strategies for improvement areas
        strategies_created = []
        for area in analysis["improvement_areas"]:
            strategy_id = await self.generate_improvement_strategy(
                area["area"], 
                area["details"]
            )
            if strategy_id:
                strategies_created.append(strategy_id)
        
        # 3. Reflect on recent failed tasks
        lessons_extracted = []
        recent_failures = [
            t for t in self.memory.task_history[-10:]
            if t.outcome == OutcomeType.FAILURE
        ]
        
        for task in recent_failures[-3:]:  # Limit to 3 most recent
            lessons = await self.reflect_on_task(task)
            for lesson in lessons:
                self.memory.learn_lesson(task.task_id, lesson)
                lessons_extracted.append(lesson)
        
        result = {
            "timestamp": datetime.now().isoformat(),
            "analysis": analysis,
            "strategies_created": strategies_created,
            "lessons_extracted": lessons_extracted
        }
        
        self.improvement_history.append(result)
        self.memory.save_to_disk()
        
        logger.info(f"Improvement cycle complete. Created {len(strategies_created)} strategies, extracted {len(lessons_extracted)} lessons")
        
        return result


# Example usage
async def main():
    """Example usage of the memory system"""
    memory = MemorySystem("./test_memory")
    
    # Store some memories
    mid1 = memory.store(
        "Successfully posted to Twitter about ApocalypsAI novel",
        MemoryType.EPISODIC,
        metadata={"platform": "twitter", "book": "ApocalypsAI"},
        tags=["social_media", "success"],
        importance=0.7
    )
    
    mid2 = memory.store(
        "Library outreach email template works best with personalization",
        MemoryType.SEMANTIC,
        tags=["library", "email", "best_practice"],
        importance=0.8
    )
    
    # Record a task result
    task = TaskResult(
        task_id="task_001",
        task_type="social_post",
        started=datetime.now().isoformat(),
        completed=datetime.now().isoformat(),
        outcome=OutcomeType.SUCCESS,
        details={"platform": "twitter", "engagement": 45}
    )
    memory.record_task_result(task)
    
    # Search memories
    results = memory.search_by_tags(["social_media"])
    print(f"Found {len(results)} memories about social media")
    
    # Get summary
    print("\nMemory Summary:")
    print(json.dumps(memory.get_summary(), indent=2))
    
    # Save to disk
    memory.save_to_disk()


if __name__ == "__main__":
    asyncio.run(main())

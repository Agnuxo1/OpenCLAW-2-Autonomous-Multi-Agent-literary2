import asyncio
from core.memory import MemorySystem, MemoryType, TaskResult, OutcomeType
import os
import shutil

async def test_memory_system():
    # Setup test directory
    test_path = "./test_memory_system"
    if os.path.exists(test_path):
        shutil.rmtree(test_path)
    
    memory = MemorySystem(test_path)
    
    # 1. Store memories
    print("Storing memories...")
    mid1 = memory.store(
        "ApocalypsAI is a novel about the day after AGI.",
        MemoryType.SEMANTIC,
        tags=["novel", "agi"]
    )
    
    mid2 = memory.store(
        "Social media posts on Tuesday evenings get 20% more engagement.",
        MemoryType.EPISODIC,
        tags=["social_media", "engagement"]
    )
    
    # 2. Semantic Search
    print("\nTesting semantic search...")
    results = memory.search_semantic("Tell me about the novel")
    print(f"Query: 'Tell me about the novel'")
    for r in results:
        print(f" - Found: {r.content} (Tags: {r.tags})")
    
    if any("novel" in r.tags for r in results):
        print("✅ Semantic search for 'novel' successful.")
    else:
        print("❌ Semantic search for 'novel' failed.")

    # 3. Retrieve by tag
    print("\nTesting tag search...")
    results = memory.search_by_tags(["engagement"])
    if results and "engagement" in results[0].tags:
        print(f"✅ Tag search successful: {results[0].content}")
    else:
        print("❌ Tag search failed.")

    # 4. Persistence test
    print("\nTesting persistence...")
    memory.save_to_disk()
    
    memory2 = MemorySystem(test_path)
    if mid1 in memory2.memories:
        print("✅ Persistence successful.")
    else:
        print("❌ Persistence failed.")

if __name__ == "__main__":
    asyncio.run(test_memory_system())

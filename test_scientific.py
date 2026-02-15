import asyncio
from core.scientific_crew import OpenCLAW_ScientificCrew

def test_scientific_crew():
    print("🚀 Starting Scientific Crew Verification...")
    manager = OpenCLAW_ScientificCrew()
    test_topic = "Autonomous Artificial Intelligence in Science"
    
    print(f"Running research for: {test_topic}")
    result = manager.conduct_research(test_topic)
    
    print("\n✅ Research Cycle Complete!")
    print(f"\nFinal Proposal Snippet:\n{str(result)[:500]}...")

if __name__ == "__main__":
    test_scientific_crew()

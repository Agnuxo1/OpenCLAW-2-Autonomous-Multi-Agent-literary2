import os
import sys
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
# CrewAI requires an OPENAI_API_KEY for internal validation even if using custom LLM
os.environ["OPENAI_API_KEY"] = "sk-dummy-key-for-internal-validation"

# Add root to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from core.crew_manager import OpenCLAW_CrewManager
    print("✅ CrewManager imported successfully.")
except ImportError as e:
    print(f"❌ Failed to import CrewManager: {e}")
    sys.exit(1)

def main():
    print("🚀 Starting CrewAI Verification...")
    
    manager = OpenCLAW_CrewManager()
    
    # Simple book data for testing
    test_book = {
        "title": "ApocalypsAI: The Day After AGI",
        "genre": "Science Fiction"
    }
    
    # Run a test cycle (non-destructive)
    # Note: In a real test we might want to mock the social media call if it's too expensive/risky.
    # But since we are in verification, let's see if it executes the logic up until the tool call.
    
    print(f"Running daily promotion for: {test_book['title']}")
    try:
        # We will use a shortened task description to keep it fast for verification
        result = manager.run_daily_promotion(test_book)
        print("\n🏆 Verification Result:")
        print(result)
    except Exception as e:
        print(f"❌ Execution failed: {e}")

if __name__ == "__main__":
    main()

import os
import logging
import uuid
from typing import List, Dict, Any
from crewai import Agent, Task, Crew, Process, LLM
from core.langchain_wrapper import UnifiedLangChainLLM
from core.tools import post_to_social_media, search_libraries, get_upcoming_contests, search_memory
from core.analytics import PerformanceAnalytics

logger = logging.getLogger(__name__)

class OpenCLAW_CrewManager:
    """
    Manages the CrewAI orchestration for the Autonomous Literary Agent.
    Now enhanced with Memory, Reflection, and Analytics capabilities.
    """
    
    def __init__(self):
        # Initialize the unified rotator wrapped in a LangChain LLM
        self.llm = UnifiedLangChainLLM()
        self.analytics = PerformanceAnalytics()
        
        # Define Agents
        self.scout = Agent(
            role='Literary Scout',
            goal='Identify high-impact opportunities for book promotion and outreach.',
            backstory='Expert in literary market trends with access to library databases and contest calendars. Always checks past results to optimize search.',
            tools=[get_upcoming_contests, search_libraries, search_memory],
            llm=self.llm,
            function_calling_llm=self.llm,
            model="unified-openclaw",
            verbose=True,
            allow_delegation=True
        )
        
        self.editor = Agent(
            role='Literary Editor',
            goal='Refine marketing copy and ensure high literary quality and brand voice.',
            backstory='Senior editor with a keen eye for hooks, blurbs, and engaging prose. Uses memory to maintain consistency.',
            tools=[search_memory],
            llm=self.llm,
            function_calling_llm=self.llm,
            model="unified-openclaw",
            verbose=True,
            allow_delegation=False
        )

        self.reviewer = Agent(
            role='Literary Critic',
            goal='Ensure all marketing content meets the highest standards and is culturally resonant.',
            backstory='A high-standard critic who provides constructive feedback to improve hooks and blurbs.',
            llm=self.llm,
            function_calling_llm=self.llm,
            model="unified-openclaw",
            verbose=True,
            allow_delegation=True
        )
        
        self.marketer = Agent(
            role='Social Media Marketer',
            goal='Execute viral social media campaigns and engage with the community.',
            backstory='Digital marketing specialist who knows how to optimize posts. Learns from past engagement metrics via memory.',
            tools=[post_to_social_media, search_memory],
            llm=self.llm,
            function_calling_llm=self.llm,
            model="unified-openclaw",
            verbose=True,
            allow_delegation=False
        )
        
        self.director = Agent(
            role='Agency Director',
            goal='Coordinate all agents to maximize author exposure and book sales.',
            backstory='Managing Director of the Literary Agency. Ensures that the memory is utilized for strategic decisions.',
            tools=[search_memory],
            llm=self.llm,
            function_calling_llm=self.llm,
            model="unified-openclaw",
            verbose=True,
            allow_delegation=True
        )

    def run_daily_promotion(self, book_data: Dict[str, Any]):
        """Runs a standard daily promotion cycle for a specific book."""
        session_id = str(uuid.uuid4())
        
        # Define Tasks
        research_task = Task(
            description=f"Find the best library outreach opportunity or contest for the book: {book_data['title']}.",
            expected_output="A report identifying 1-2 specific opportunities with contact details or deadlines.",
            agent=self.scout
        )
        
        copywritting_task = Task(
            description=f"Generate 3 highly engaging social media hooks for {book_data['title']} based on its genre: {book_data['genre']}.",
            expected_output="Three hooks (short, medium, long) in both English and Spanish.",
            agent=self.editor
        )

        reflection_task = Task(
            description="Critically review the generated hooks. Provide specific suggestions for improvement or approve them if they are exceptional.",
            expected_output="A critique with improvements or an approval confirmation.",
            agent=self.reviewer,
            context=[copywritting_task]
        )
        
        posting_task = Task(
            description="Select the best hook (incorporating any improvements from the critic) and post it to at least two social media platforms (Twitter and Reddit).",
            expected_output="Confirmation of successful posts with platform IDs.",
            agent=self.marketer,
            context=[copywritting_task, reflection_task]
        )
        
        # Define Crew
        crew = Crew(
            agents=[self.director, self.scout, self.editor, self.reviewer, self.marketer],
            tasks=[research_task, copywritting_task, reflection_task, posting_task],
            process=Process.sequential,
            verbose=True
        )
        
        logger.info(f"Starting Crew execution for session {session_id} and book: {book_data['title']}")
        result = crew.kickoff()
        
        # Record results in Analytics
        self.analytics.record_session(session_id, result)
        
        return result

if __name__ == "__main__":
    # Example test run
    manager = OpenCLAW_CrewManager()
    test_book = {
        "title": "ApocalypsAI: The Day After AGI",
        "genre": "Science Fiction"
    }
    result = manager.run_daily_promotion(test_book)
    print(f"\nFinal Result:\n{result}")

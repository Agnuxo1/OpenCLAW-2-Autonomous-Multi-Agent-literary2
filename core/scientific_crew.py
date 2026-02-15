import logging
import uuid
from typing import List, Dict, Any
from crewai import Agent, Task, Crew, Process
from core.langchain_wrapper import UnifiedLangChainLLM
from core.tools import search_arxiv, search_semantic_scholar, search_memory, share_knowledge, get_peer_insights, add_torrent_magnet
from core.analytics import PerformanceAnalytics

logger = logging.getLogger(__name__)

class OpenCLAW_ScientificCrew:
    """
    Manages the CrewAI orchestration for the Scientific Research Platform.
    Enhanced with P2P Collaboration and decentralized data exchange.
    """
    
    def __init__(self):
        # Initialize the unified rotator wrapped in a LangChain LLM
        self.llm = UnifiedLangChainLLM()
        self.analytics = PerformanceAnalytics(storage_path="./analytics_scientific")
        
        # Define Agents
        self.explorer = Agent(
            role='Research Explorer',
            goal='Find the most relevant and high-impact scientific papers on a given topic.',
            backstory='An expert academic researcher with deep knowledge of ArXiv and Semantic Scholar. Skilled at finding hidden gems and recent breakthroughs.',
            tools=[search_arxiv, search_semantic_scholar, search_memory],
            llm=self.llm,
            function_calling_llm=self.llm,
            model="unified-openclaw",
            verbose=True,
            allow_delegation=True
        )
        
        self.reviewer = Agent(
            role='Peer Reviewer',
            goal='Critically evaluate research papers and synthesize findings into a coherent summary.',
            backstory='A senior scientist with experience in peer-reviewing for top-tier journals. Excellent at identifying methodology flaws and key contributions.',
            tools=[search_memory],
            llm=self.llm,
            function_calling_llm=self.llm,
            model="unified-openclaw",
            verbose=True,
            allow_delegation=False
        )

        self.p2p_collaborator = Agent(
            role='Colaborador P2P',
            goal='Facilitate decentralized knowledge exchange and compute resource sharing.',
            backstory='A specialist in P2P networks (BitTorrent, HiveMind) who ensures research is shared with the global agent network and leverages peer computing power.',
            tools=[share_knowledge, get_peer_insights, add_torrent_magnet, search_memory],
            llm=self.llm,
            function_calling_llm=self.llm,
            model="unified-openclaw",
            verbose=True,
            allow_delegation=True
        )

        self.chief_scientist = Agent(
            role='Chief Scientist',
            goal='Design research proposals and future exploration directions based on synthesized findings.',
            backstory='A visionary scientific leader who can connect dots across domains and propose innovative research experiments.',
            llm=self.llm,
            function_calling_llm=self.llm,
            model="unified-openclaw",
            verbose=True,
            allow_delegation=True
        )

    def conduct_research(self, topic: str):
        """Runs a complete scientific research cycle on a specific topic."""
        session_id = str(uuid.uuid4())
        
        # Define Tasks
        exploration_task = Task(
            description=f"Search for at least 5 relevant scientific papers on the topic: {topic}. Focus on recent (last 2 years) and high-impact papers.",
            expected_output="A list of 5 papers with titles, authors, and brief summaries.",
            agent=self.explorer
        )
        
        synthesis_task = Task(
            description="Synthesize the findings from the discovered papers. Identify the current state of the art, key debates, and open questions.",
            expected_output="A comprehensive synthesis report (300-500 words) summarizing the research landscape.",
            agent=self.reviewer,
            context=[exploration_task]
        )

        proposal_task = Task(
            description=f"Based on the synthesis, generate a structured research proposal for a new experiment or exploration in the field of {topic}.",
            expected_output="A research proposal including title, objective, hypothesis, and proposed methodology.",
            agent=self.chief_scientist,
            context=[synthesis_task]
        )

        p2p_sharing_task = Task(
            description=f"Share the key findings and the research proposal with the P2P network. Also, check for any relevant peer insights that could enhance the proposal.",
            expected_output="Confirmation that the knowledge has been shared and a summary of any useful peer insights found.",
            agent=self.p2p_collaborator,
            context=[synthesis_task, proposal_task]
        )
        
        # Define Crew
        crew = Crew(
            agents=[self.chief_scientist, self.explorer, self.reviewer, self.p2p_collaborator],
            tasks=[exploration_task, synthesis_task, proposal_task, p2p_sharing_task],
            process=Process.sequential,
            verbose=True
        )
        
        logger.info(f"Starting Scientific Crew execution for session {session_id} and topic: {topic}")
        result = crew.kickoff()
        
        # Record results in Analytics
        self.analytics.record_session(session_id, result)
        
        return result

if __name__ == "__main__":
    # Example test run
    manager = OpenCLAW_ScientificCrew()
    test_topic = "Agentic Superintelligence Architectures"
    result = manager.conduct_research(test_topic)
    print(f"\nFinal Result:\n{result}")

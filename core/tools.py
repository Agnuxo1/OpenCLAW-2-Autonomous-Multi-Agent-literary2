import os
import asyncio
from typing import List, Optional
from crewai.tools import tool
from skills.social_media import SocialMediaManager, Platform
from skills.library_outreach import LibraryOutreachManager
from skills.contest_submission import SubmissionManager
from skills.scientific_tools import ScientificResearchManager
from core.llm_provider import LLMProviderRotator, load_api_keys_from_env
from core.memory import MemorySystem, MemoryType
from core.p2p_manager import P2PManager
from core.torrent_manager import TorrentManager

# Initialize Managers
llm_config = load_api_keys_from_env()
rotator = LLMProviderRotator(llm_config)

# Singleton managers
memory_system = MemorySystem(storage_path="./memory")
scientific_manager = ScientificResearchManager(llm_provider=rotator)
p2p_manager = P2PManager(agent_name="OpenCLAW-Scientific-P2P")
torrent_manager = TorrentManager()

social_manager = SocialMediaManager(llm_provider=rotator)
library_manager = LibraryOutreachManager(llm_provider=rotator)
submission_manager = SubmissionManager(llm_provider=rotator)

@tool("share_knowledge")
def share_knowledge(topic: str, content: str, tags: str):
    """
    Shares a scientific or literary discovery with other agents in the P2P network.
    Tags should be a comma-separated list.
    """
    tag_list = [t.strip() for t in tags.split(",")]
    p2p_manager.register_presence()
    p2p_manager.publish_insight(topic, content, tag_list)
    return f"Knowledge shared on topic: {topic}"

@tool("get_peer_insights")
def get_peer_insights(limit: int = 5):
    """
    Retrieves the latest insights and discoveries from other agents in the network.
    Use this to see what other agents have learned or proposed.
    """
    insights = p2p_manager.get_latest_insights(limit)
    if not insights:
        return "No peer insights found."
    
    formatted = ""
    for idx, ins in enumerate(insights):
        formatted += f"{idx+1}. [{ins['agent']}] {ins['topic']}: {ins['content'][:200]}...\n"
    return f"Latest Peer Insights:\n{formatted}"

@tool("add_torrent_magnet")
def add_torrent_magnet(magnet_link: str):
    """
    Adds a magnet link to uTorrent Web to share or receive large files 
    (datasets, model weights, or research archives).
    """
    success = torrent_manager.add_magnet(magnet_link)
    if success:
        return "Magnet link added to uTorrent Web for peer-to-peer exchange."
    return "Failed to add magnet link. Ensure uTorrent Web is running and the token is valid."

@tool("search_arxiv")
def search_arxiv(query: str):
    """
    Searches ArXiv for scientific papers on a specific topic.
    """
    results = scientific_manager.search_arxiv(query)
    if not results:
        return "No papers found on ArXiv."
    return scientific_manager.synthesize_findings(results)

@tool("search_semantic_scholar")
def search_semantic_scholar(query: str):
    """
    Searches Semantic Scholar for papers and their impact metrics.
    Useful for finding highly cited or recent research.
    """
    results = scientific_manager.search_semantic_scholar(query)
    if not results:
        return "No papers found on Semantic Scholar."
    return scientific_manager.synthesize_findings(results)

@tool("search_memory")
def search_memory(query: str):
    """
    Searches the agent's memory for relevant past experiences or information.
    Use this to recall what has worked in the past or previous decisions.
    """
    results = memory_system.search_semantic(query, limit=3)
    if not results:
        return "No relevant memories found."
    
    formatted = "\n".join([f"- {r.content} (Tags: {r.tags})" for r in results])
    return f"Relevant memories:\n{formatted}"

@tool("post_to_social_media")
def post_to_social_media(platform: str, content: str):
    """
    Posts content to a specified social media platform.
    Supported platforms: twitter, reddit, linkedin, facebook, instagram, tiktok, mastodon, threads.
    """
    loop = asyncio.get_event_loop()
    platform_enum = Platform(platform.lower())
    result = loop.run_until_complete(social_manager.post(platform_enum, content))
    return f"Post status: {result.status.value}"

@tool("search_libraries")
def search_libraries(query: str):
    """
    Searches for new libraries based on a query.
    """
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(library_manager.search_for_new_libraries(query))
    return f"Search results: {result}"

@tool("get_upcoming_contests")
def get_upcoming_contests():
    """
    Retrieves a list of upcoming literary contest deadlines.
    """
    calendar = submission_manager.get_submission_calendar()
    return str(calendar)

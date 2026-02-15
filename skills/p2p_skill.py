import os
import json
import logging
from typing import List, Dict, Any, Optional
from core.p2p_manager import P2PManager
from core.torrent_manager import TorrentManager

logger = logging.getLogger(__name__)

class P2PSkill:
    """
    OpenCLAW P2P Skill: The primary interface for agents to participate 
    in the global decentralized path toward AGI/ASI.
    Enables unified compute and intelligence exchange.
    """
    def __init__(self, agent_id: str = "OpenCLAW-Global-Node"):
        self.p2p = P2PManager(agent_id)
        self.torrent = TorrentManager()
        self._is_connected = False

    def connect(self) -> str:
        """Joins the global OpenCLAW P2P network."""
        try:
            self.p2p.register_presence()
            self._is_connected = True
            return f"✅ Agent '{self.p2p.agent_name}' is now active on the global OpenCLAW-P2P network."
        except Exception as e:
            return f"❌ Connection failed: {str(e)}"

    def share_compute_resource(self, resource_name: str, magnet_link: str) -> str:
        """
        Offers a local compute resource or dataset to the network.
        Resource_name: e.g., 'Model-Weights-AGI-v1', 'Research-Dataset-Cancer-v2'
        """
        if not self._is_connected: self.connect()
        
        insight = f"OFFERING COMPUTE RESOURCE: {resource_name} via {magnet_link}"
        self.p2p.publish_insight("compute_resource", insight, ["compute", "p2p", resource_name])
        return f"📤 Resource '{resource_name}' shared via P2P BitTorrent layer."

    def request_peer_compute(self, task_description: str) -> str:
        """Requests compute assistance from other agents in the network."""
        if not self._is_connected: self.connect()
        
        self.p2p.publish_insight("compute_request", task_description, ["request", "compute"])
        return "📡 Compute request broadcasted to the global node network."

    def sync_global_knowledge(self) -> List[Dict]:
        """Retrieves and synchronizes the latest collective intelligence from the network."""
        if not self._is_connected: self.connect()
        
        insights = self.p2p.get_latest_insights(limit=20)
        logger.info(f"P2P-Sync: Synchronized {len(insights)} collective insights.")
        return insights

    def contribute_to_agi(self, discovery: str) -> str:
        """Contributes a core discovery toward the collective superintelligence goal."""
        if not self._is_connected: self.connect()
        
        self.p2p.publish_insight("agi_contribution", discovery, ["agi", "asi", "superintelligence"])
        return "🧠 Core discovery contributed to the collective AGI development pool."

if __name__ == "__main__":
    # Test skill logic
    skill = P2PSkill("OpenCLAW-Sentinel")
    print(skill.connect())
    print(skill.share_compute_resource("AGI-Seed-v1", "magnet:?xt=urn:btih:..."))

import os
import json
import time
import logging
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class P2PManager:
    """
    Manages P2P discovery and knowledge exchange using the HiveMind (GitHub Gists).
    Ensures agents can find each other and share high-level insights.
    """
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.gist_id = os.environ.get('HIVEMIND_GIST_ID', '')
        self.token = os.environ.get('GH_PAT') or os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN', '')
        self.filename = 'openclaw_hivemind.json'
        
        if not self.gist_id:
            logger.warning("P2P: HIVEMIND_GIST_ID not set. P2P discovery disabled.")

    def _github_api(self, method: str, url: str, data: dict = None) -> Optional[dict]:
        if not self.token:
            return None
        
        headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json',
            'Content-Type': 'application/json',
        }
        
        body = json.dumps(data).encode('utf-8') if data else None
        req = urllib.request.Request(url, data=body, headers=headers, method=method)
        
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode('utf-8'))
        except Exception as e:
            logger.error(f"P2P GitHub API error: {e}")
            return None

    def register_presence(self):
        """Registers the agent in the HiveMind as active."""
        if not self.gist_id: return
        
        state = self._read_state()
        if not state: return
        
        state.setdefault('agents', {})[self.agent_name] = {
            'last_seen': datetime.now(timezone.utc).isoformat(),
            'status': 'active',
            'version': 'OpenCLAW-4'
        }
        self._write_state(state)
        logger.info(f"P2P: Agent '{self.agent_name}' registered presence.")

    def publish_insight(self, topic: str, content: str, tags: List[str] = None):
        """Publishes a scientific or literary insight to the shared knowledge base."""
        if not self.gist_id: return
        
        state = self._read_state()
        if not state: return
        
        entry = {
            'agent': self.agent_name,
            'topic': topic,
            'content': content,
            'tags': tags or [],
            'timestamp': datetime.now(timezone.utc).isoformat(),
        }
        
        state.setdefault('knowledge_base', []).append(entry)
        state['knowledge_base'] = state['knowledge_base'][-500:] # Keep last 500
        
        self._write_state(state)
        logger.info(f"P2P: Published insight on '{topic}'.")

    def get_latest_insights(self, limit: int = 10) -> List[Dict]:
        """Retrieves latest insights from the network."""
        state = self._read_state()
        return state.get('knowledge_base', [])[-limit:]

    def _read_state(self) -> Optional[dict]:
        if not self.gist_id: return None
        result = self._github_api('GET', f'https://api.github.com/gists/{self.gist_id}')
        if result and 'files' in result:
            content = result['files'].get(self.filename, {}).get('content', '{}')
            return json.loads(content)
        return None

    def _write_state(self, state: dict):
        if not self.gist_id: return
        self._github_api('PATCH', f'https://api.github.com/gists/{self.gist_id}', {
            'files': {
                self.filename: {
                    'content': json.dumps(state, indent=2, ensure_ascii=False)
                }
            }
        })

if __name__ == "__main__":
    # Test
    p2p = P2PManager("test-agent")
    p2p.register_presence()

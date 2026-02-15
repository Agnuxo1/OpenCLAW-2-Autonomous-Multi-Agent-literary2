import requests
import logging
import os
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class TorrentManager:
    """
    Manages data exchange via uTorrent Web.
    Uses BitTorrent protocol to share large datasets (superintelligence seeds) between agents.
    """
    def __init__(self, api_token: str = "localapi6ad51616bfda7857", base_url: str = "http://127.0.0.1:10000/gui/"):
        self.api_token = api_token
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {self.api_token}"
        }

    def _make_request(self, action: str, params: Dict = None) -> Optional[Dict]:
        """Base method for interacting with uTorrent Web API."""
        if params is None:
            params = {}
        params['action'] = action
        params['token'] = self.api_token # Some versions use it in params too
        
        try:
            response = requests.get(self.base_url, params=params, headers=self.headers, timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Torrent: API error {response.status_code}: {response.text}")
                return None
        except Exception as e:
            logger.error(f"Torrent: Connection failed: {e}")
            return None

    def add_magnet(self, magnet_link: str) -> bool:
        """Adds a magnet link to the download queue."""
        result = self._make_request("add-url", {"s": magnet_link})
        if result:
            logger.info(f"Torrent: Magnet link added successfully.")
            return True
        return False

    def list_torrents(self) -> List[Dict]:
        """Lists active torrents and their status."""
        result = self._make_request("list")
        if result and 'torrents' in result:
            return result['torrents']
        return []

    def get_download_status(self, info_hash: str) -> Optional[Dict]:
        """Gets status for a specific torrent by info hash."""
        torrents = self.list_torrents()
        for t in torrents:
            if t[0].lower() == info_hash.lower():
                return {
                    "name": t[2],
                    "status": t[1],
                    "progress": t[4] / 10, # Per mille to percentage
                    "download_speed": t[9],
                    "upload_speed": t[10]
                }
        return None

if __name__ == "__main__":
    # Test (requires local uTorrent Web running)
    tm = TorrentManager()
    # tm.add_magnet("magnet:?xt=urn:btih:...")
    print("Torrent Manager initialized.")

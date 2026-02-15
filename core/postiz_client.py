
import os
import aiohttp
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class PostizClient:
    """
    Client for interacting with the Postiz Social Media Scheduling API.
    """
    
    def __init__(self, api_key: str = None, base_url: str = "http://localhost:5000/api"):
        self.api_key = api_key or os.getenv("POSTIZ_API_KEY")
        self.base_url = base_url or os.getenv("POSTIZ_URL", "http://localhost:5000/api")
        self.session: Optional[aiohttp.ClientSession] = None
        
        if not self.api_key:
            logger.warning("Postiz API Key not found. Social posting will fail.")

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(headers={
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        })
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def ensure_session(self):
        if not self.session:
            self.session = aiohttp.ClientSession(headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            })

    async def create_post(self, content: str, platforms: List[str], media_urls: List[str] = None, schedule_time: str = None) -> Dict:
        """
        Create a new post in Postiz.
        
        Args:
            content: The text content of the post.
            platforms: List of platform IDs (e.g., ['twitter', 'linkedin']).
            media_urls: List of image/video URLs.
            schedule_time: ISO 8601 string for scheduled time. If None, posts immediately.
        """
        await self.ensure_session()
        
        payload = {
            "content": content,
            "providers": platforms,
            "media": media_urls or [],
        }
        
        if schedule_time:
            payload["scheduledAt"] = schedule_time
        else:
            payload["postNow"] = True

        endpoint = f"{self.base_url}/posts"
        
        try:
            async with self.session.post(endpoint, json=payload) as response:
                if response.status in [200, 201]:
                    data = await response.json()
                    logger.info(f"Post created successfully in Postiz: {data.get('id')}")
                    return {"success": True, "data": data}
                else:
                    error_text = await response.text()
                    logger.error(f"Failed to create post in Postiz: {response.status} - {error_text}")
                    return {"success": False, "error": error_text, "status": response.status}
        except Exception as e:
            logger.error(f"Exception creating post in Postiz: {e}")
            return {"success": False, "error": str(e)}

    async def get_platforms(self) -> List[Dict]:
        """Get connected social platforms."""
        await self.ensure_session()
        endpoint = f"{self.base_url}/integrations"
        
        try:
            async with self.session.get(endpoint) as response:
                if response.status == 200:
                    return await response.json()
                return []
        except Exception as e:
            logger.error(f"Error fetching platforms: {e}")
            return []

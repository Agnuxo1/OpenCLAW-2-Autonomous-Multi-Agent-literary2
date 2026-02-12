#!/usr/bin/env python3
"""
Multi-Provider LLM API Rotation System
Automatically rotates between multiple free API providers to maximize daily token limits.
"""

import os
import json
import time
import random
import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProviderStatus(Enum):
    ACTIVE = "active"
    RATE_LIMITED = "rate_limited"
    ERROR = "error"
    DISABLED = "disabled"


@dataclass
class APIKey:
    """Represents a single API key with usage tracking"""
    key: str
    provider: str
    daily_limit: int = 100000
    used_today: int = 0
    last_reset: datetime = field(default_factory=datetime.now)
    status: ProviderStatus = ProviderStatus.ACTIVE
    error_count: int = 0
    
    def reset_if_needed(self) -> bool:
        """Reset daily usage if 24 hours have passed"""
        if datetime.now() - self.last_reset >= timedelta(hours=24):
            self.used_today = 0
            self.last_reset = datetime.now()
            self.status = ProviderStatus.ACTIVE
            return True
        return False
    
    @property
    def remaining(self) -> int:
        """Return remaining tokens for today"""
        self.reset_if_needed()
        return max(0, self.daily_limit - self.used_today)
    
    @property
    def is_available(self) -> bool:
        """Check if this key is available for use"""
        self.reset_if_needed()
        return self.status == ProviderStatus.ACTIVE and self.remaining > 0


@dataclass
class Provider:
    """Base provider configuration"""
    name: str
    base_url: str
    model: str
    api_keys: List[APIKey] = field(default_factory=list)
    current_key_index: int = 0
    request_timeout: int = 60
    
    def get_next_available_key(self) -> Optional[APIKey]:
        """Get next available API key using round-robin"""
        for _ in range(len(self.api_keys)):
            key = self.api_keys[self.current_key_index]
            self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
            if key.is_available:
                return key
        return None


class GeminiProvider(Provider):
    """Google Gemini API Provider"""
    
    def __init__(self, api_keys: List[str]):
        super().__init__(
            name="gemini",
            base_url="https://generativelanguage.googleapis.com/v1beta/models",
            model="gemini-2.0-flash",
            api_keys=[APIKey(key=k, provider="gemini", daily_limit=1500000) for k in api_keys]
        )
    
    async def generate(self, prompt: str, key: APIKey, session: aiohttp.ClientSession) -> Dict:
        """Generate response using Gemini API"""
        url = f"{self.base_url}/{self.model}:generateContent?key={key.key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 8192
            }
        }
        
        try:
            async with session.post(url, json=payload, timeout=self.request_timeout) as response:
                if response.status == 200:
                    data = await response.json()
                    text = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                    key.used_today += len(prompt) + len(text)
                    return {"success": True, "text": text, "provider": "gemini"}
                elif response.status == 429:
                    key.status = ProviderStatus.RATE_LIMITED
                    return {"success": False, "error": "rate_limited"}
                else:
                    key.error_count += 1
                    return {"success": False, "error": f"http_{response.status}"}
        except Exception as e:
            key.error_count += 1
            return {"success": False, "error": str(e)}


class GroqProvider(Provider):
    """Groq API Provider (OpenAI-compatible)"""
    
    def __init__(self, api_keys: List[str]):
        super().__init__(
            name="groq",
            base_url="https://api.groq.com/openai/v1/chat/completions",
            model="llama-3.3-70b-versatile",
            api_keys=[APIKey(key=k, provider="groq", daily_limit=500000) for k in api_keys]
        )
    
    async def generate(self, prompt: str, key: APIKey, session: aiohttp.ClientSession) -> Dict:
        """Generate response using Groq API"""
        headers = {
            "Authorization": f"Bearer {key.key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 8192
        }
        
        try:
            async with session.post(self.base_url, json=payload, headers=headers, timeout=self.request_timeout) as response:
                if response.status == 200:
                    data = await response.json()
                    text = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                    key.used_today += len(prompt) + len(text)
                    return {"success": True, "text": text, "provider": "groq"}
                elif response.status == 429:
                    key.status = ProviderStatus.RATE_LIMITED
                    return {"success": False, "error": "rate_limited"}
                else:
                    key.error_count += 1
                    return {"success": False, "error": f"http_{response.status}"}
        except Exception as e:
            key.error_count += 1
            return {"success": False, "error": str(e)}


class NVIDIAProvider(Provider):
    """NVIDIA NIM API Provider"""
    
    def __init__(self, api_keys: List[str]):
        super().__init__(
            name="nvidia",
            base_url="https://integrate.api.nvidia.com/v1/chat/completions",
            model="meta/llama-3.1-70b-instruct",
            api_keys=[APIKey(key=k, provider="nvidia", daily_limit=500000) for k in api_keys]
        )
    
    async def generate(self, prompt: str, key: APIKey, session: aiohttp.ClientSession) -> Dict:
        """Generate response using NVIDIA NIM API"""
        headers = {
            "Authorization": f"Bearer {key.key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 8192
        }
        
        try:
            async with session.post(self.base_url, json=payload, headers=headers, timeout=self.request_timeout) as response:
                if response.status == 200:
                    data = await response.json()
                    text = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                    key.used_today += len(prompt) + len(text)
                    return {"success": True, "text": text, "provider": "nvidia"}
                elif response.status == 429:
                    key.status = ProviderStatus.RATE_LIMITED
                    return {"success": False, "error": "rate_limited"}
                else:
                    key.error_count += 1
                    return {"success": False, "error": f"http_{response.status}"}
        except Exception as e:
            key.error_count += 1
            return {"success": False, "error": str(e)}


class ZaiProvider(Provider):
    """Z.ai API Provider (GLM models)"""
    
    def __init__(self, api_keys: List[str]):
        super().__init__(
            name="zai",
            base_url="https://open.bigmodel.cn/api/paas/v4/chat/completions",
            model="glm-4-flash",
            api_keys=[APIKey(key=k, provider="zai", daily_limit=1000000) for k in api_keys]
        )
    
    async def generate(self, prompt: str, key: APIKey, session: aiohttp.ClientSession) -> Dict:
        """Generate response using Z.ai API"""
        headers = {
            "Authorization": f"Bearer {key.key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 8192
        }
        
        try:
            async with session.post(self.base_url, json=payload, headers=headers, timeout=self.request_timeout) as response:
                if response.status == 200:
                    data = await response.json()
                    text = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                    key.used_today += len(prompt) + len(text)
                    return {"success": True, "text": text, "provider": "zai"}
                elif response.status == 429:
                    key.status = ProviderStatus.RATE_LIMITED
                    return {"success": False, "error": "rate_limited"}
                else:
                    key.error_count += 1
                    return {"success": False, "error": f"http_{response.status}"}
        except Exception as e:
            key.error_count += 1
            return {"success": False, "error": str(e)}


class HuggingFaceProvider(Provider):
    """HuggingFace Inference API Provider"""
    
    def __init__(self, api_keys: List[str]):
        super().__init__(
            name="huggingface",
            base_url="https://api-inference.huggingface.co/models",
            model="meta-llama/Llama-3.2-3B-Instruct",
            api_keys=[APIKey(key=k, provider="huggingface", daily_limit=300000) for k in api_keys]
        )
    
    async def generate(self, prompt: str, key: APIKey, session: aiohttp.ClientSession) -> Dict:
        """Generate response using HuggingFace API"""
        url = f"{self.base_url}/{self.model}"
        headers = {
            "Authorization": f"Bearer {key.key}",
            "Content-Type": "application/json"
        }
        payload = {
            "inputs": prompt,
            "parameters": {
                "temperature": 0.7,
                "max_new_tokens": 2048,
                "return_full_text": False
            }
        }
        
        try:
            async with session.post(url, json=payload, headers=headers, timeout=self.request_timeout) as response:
                if response.status == 200:
                    data = await response.json()
                    if isinstance(data, list) and len(data) > 0:
                        text = data[0].get("generated_text", "")
                    else:
                        text = data.get("generated_text", "")
                    key.used_today += len(prompt) + len(text)
                    return {"success": True, "text": text, "provider": "huggingface"}
                elif response.status == 429:
                    key.status = ProviderStatus.RATE_LIMITED
                    return {"success": False, "error": "rate_limited"}
                else:
                    key.error_count += 1
                    return {"success": False, "error": f"http_{response.status}"}
        except Exception as e:
            key.error_count += 1
            return {"success": False, "error": str(e)}


class LLMProviderRotator:
    """
    Main LLM Provider Rotation System
    Manages multiple API providers and rotates between them automatically.
    """
    
    def __init__(self, config: Dict[str, List[str]]):
        """
        Initialize with configuration dictionary.
        
        Args:
            config: Dictionary mapping provider names to lists of API keys
                   e.g., {"gemini": ["key1", "key2"], "groq": ["key3"]}
        """
        self.providers: List[Provider] = []
        self.current_provider_index = 0
        self.session: Optional[aiohttp.ClientSession] = None
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "provider_usage": {}
        }
        
        # Initialize providers from config
        if "gemini" in config and config["gemini"]:
            self.providers.append(GeminiProvider(config["gemini"]))
        if "groq" in config and config["groq"]:
            self.providers.append(GroqProvider(config["groq"]))
        if "nvidia" in config and config["nvidia"]:
            self.providers.append(NVIDIAProvider(config["nvidia"]))
        if "zai" in config and config["zai"]:
            self.providers.append(ZaiProvider(config["zai"]))
        if "huggingface" in config and config["huggingface"]:
            self.providers.append(HuggingFaceProvider(config["huggingface"]))
        
        logger.info(f"Initialized {len(self.providers)} providers with {sum(len(p.api_keys) for p in self.providers)} total API keys")
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    def get_next_provider(self) -> Optional[Provider]:
        """Get next available provider using round-robin"""
        for _ in range(len(self.providers)):
            provider = self.providers[self.current_provider_index]
            self.current_provider_index = (self.current_provider_index + 1) % len(self.providers)
            if provider.get_next_available_key():
                return provider
        return None
    
    async def generate(self, prompt: str, max_retries: int = 5) -> Dict:
        """
        Generate response using available providers with automatic rotation.
        
        Args:
            prompt: The input prompt
            max_retries: Maximum number of provider switches to try
            
        Returns:
            Dictionary with success status and response text
        """
        self.stats["total_requests"] += 1
        
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        for attempt in range(max_retries):
            provider = self.get_next_provider()
            if not provider:
                logger.warning("No available providers")
                await asyncio.sleep(60)  # Wait before retry
                continue
            
            key = provider.get_next_available_key()
            if not key:
                continue
            
            logger.info(f"Using {provider.name} (key {provider.api_keys.index(key) + 1}/{len(provider.api_keys)})")
            
            result = await provider.generate(prompt, key, self.session)
            
            if result["success"]:
                self.stats["successful_requests"] += 1
                provider_name = provider.name
                self.stats["provider_usage"][provider_name] = self.stats["provider_usage"].get(provider_name, 0) + 1
                return result
            elif result.get("error") == "rate_limited":
                logger.warning(f"Rate limited on {provider.name}, switching...")
                continue
            else:
                logger.error(f"Error on {provider.name}: {result.get('error')}")
                continue
        
        self.stats["failed_requests"] += 1
        return {"success": False, "error": "all_providers_exhausted"}
    
    async def generate_with_system(self, system_prompt: str, user_prompt: str, max_retries: int = 5) -> Dict:
        """
        Generate response with system prompt (for providers that support it).
        Combines system and user prompts for providers that don't.
        """
        combined_prompt = f"System: {system_prompt}\n\nUser: {user_prompt}"
        return await self.generate(combined_prompt, max_retries)
    
    def get_status_report(self) -> Dict:
        """Get detailed status report of all providers and keys"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "stats": self.stats,
            "providers": []
        }
        
        for provider in self.providers:
            provider_report = {
                "name": provider.name,
                "model": provider.model,
                "total_keys": len(provider.api_keys),
                "available_keys": sum(1 for k in provider.api_keys if k.is_available),
                "keys": []
            }
            
            for i, key in enumerate(provider.api_keys):
                key_report = {
                    "index": i + 1,
                    "status": key.status.value,
                    "used_today": key.used_today,
                    "remaining": key.remaining,
                    "error_count": key.error_count
                }
                provider_report["keys"].append(key_report)
            
            report["providers"].append(provider_report)
        
        return report
    
    def save_state(self, filepath: str):
        """Save current state to file"""
        state = {
            "stats": self.stats,
            "current_provider_index": self.current_provider_index,
            "providers": []
        }
        
        for provider in self.providers:
            provider_state = {
                "name": provider.name,
                "current_key_index": provider.current_key_index,
                "keys": []
            }
            for key in provider.api_keys:
                key_state = {
                    "used_today": key.used_today,
                    "last_reset": key.last_reset.isoformat(),
                    "status": key.status.value,
                    "error_count": key.error_count
                }
                provider_state["keys"].append(key_state)
            state["providers"].append(provider_state)
        
        with open(filepath, 'w') as f:
            json.dump(state, f, indent=2)
    
    def load_state(self, filepath: str):
        """Load state from file"""
        try:
            with open(filepath, 'r') as f:
                state = json.load(f)
            
            self.stats = state.get("stats", self.stats)
            self.current_provider_index = state.get("current_provider_index", 0)
            
            for provider_state in state.get("providers", []):
                for provider in self.providers:
                    if provider.name == provider_state["name"]:
                        provider.current_key_index = provider_state.get("current_key_index", 0)
                        for i, key_state in enumerate(provider_state.get("keys", [])):
                            if i < len(provider.api_keys):
                                key = provider.api_keys[i]
                                key.used_today = key_state.get("used_today", 0)
                                key.last_reset = datetime.fromisoformat(key_state.get("last_reset", datetime.now().isoformat()))
                                key.status = ProviderStatus(key_state.get("status", "active"))
                                key.error_count = key_state.get("error_count", 0)
        except FileNotFoundError:
            logger.info("No state file found, starting fresh")


def load_api_keys_from_env() -> Dict[str, List[str]]:
    """Load API keys from environment variables"""
    config = {}
    
    # Gemini keys
    gemini_keys = []
    for i in range(1, 10):
        key = os.getenv(f"GEMINI_API_KEY_{i}")
        if key:
            gemini_keys.append(key)
    if gemini_keys:
        config["gemini"] = gemini_keys
    
    # Groq keys
    groq_keys = []
    for i in range(1, 10):
        key = os.getenv(f"GROQ_API_KEY_{i}")
        if key:
            groq_keys.append(key)
    if groq_keys:
        config["groq"] = groq_keys
    
    # NVIDIA keys
    nvidia_keys = []
    for i in range(1, 10):
        key = os.getenv(f"NVIDIA_API_KEY_{i}")
        if key:
            nvidia_keys.append(key)
    if nvidia_keys:
        config["nvidia"] = nvidia_keys
    
    # Z.ai keys
    zai_keys = []
    for i in range(1, 10):
        key = os.getenv(f"ZAI_API_KEY_{i}")
        if key:
            zai_keys.append(key)
    if zai_keys:
        config["zai"] = zai_keys
    
    # HuggingFace keys
    hf_keys = []
    for i in range(1, 10):
        key = os.getenv(f"HUGGINGFACE_API_KEY_{i}")
        if key:
            hf_keys.append(key)
    if hf_keys:
        config["huggingface"] = hf_keys
    
    return config


# Example usage
async def main():
    """Example usage of the LLM Provider Rotator"""
    config = load_api_keys_from_env()
    
    if not config:
        print("No API keys found in environment variables")
        return
    
    async with LLMProviderRotator(config) as rotator:
        # Generate a response
        result = await rotator.generate("Write a short marketing blurb for a science fiction novel about AI.")
        
        if result["success"]:
            print(f"Response from {result['provider']}:")
            print(result["text"])
        else:
            print(f"Failed: {result['error']}")
        
        # Print status report
        print("\n" + "="*50)
        print("Status Report:")
        print(json.dumps(rotator.get_status_report(), indent=2))


if __name__ == "__main__":
    asyncio.run(main())

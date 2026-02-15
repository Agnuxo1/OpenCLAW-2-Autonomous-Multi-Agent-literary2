from typing import Any, List, Optional, Dict, Union
from crewai.llms.base_llm import BaseLLM
from unified_llm import UnifiedLLM

# Shared singleton instance
_shared_rotator: Optional[UnifiedLLM] = None

def get_rotator() -> UnifiedLLM:
    global _shared_rotator
    if _shared_rotator is None:
        _shared_rotator = UnifiedLLM()
    return _shared_rotator

class UnifiedLangChainLLM(BaseLLM):
    """
    A CrewAI-compatible BaseLLM wrapper for OpenCLAW UnifiedLLM.
    Inheriting from BaseLLM ensures seamless integration and bypasses fallback logic.
    """
    
    def __init__(self, **kwargs):
        # Initialize with a dummy model name to satisfy BaseLLM requirement
        super().__init__(model="unified-openclaw", **kwargs)

    def call(
        self,
        messages: Union[str, List[Dict[str, Any]]],
        **kwargs: Any,
    ) -> str:
        """
        Processes the LLM call using the UnifiedLLM rotator.
        """
        system_prompt = "You are a helpful AI assistant."
        user_prompt = ""
        
        if isinstance(messages, str):
            user_prompt = messages
        else:
            for msg in messages:
                role = msg.get("role")
                content = msg.get("content")
                if role == "system":
                    system_prompt = content
                elif role == "user":
                    user_prompt += f"{content}\n"
                elif role == "assistant":
                    user_prompt += f"Assistant: {content}\n"
        
        rotator = get_rotator()
        response = rotator.generate(user_prompt.strip(), system=system_prompt)
        
        if response is None:
            return "Error: All LLM providers failed."
            
        return response

    async def acall(
        self,
        messages: Union[str, List[Dict[str, Any]]],
        **kwargs: Any,
    ) -> str:
        """
        Asynchronous call wrapper.
        """
        return self.call(messages, **kwargs)

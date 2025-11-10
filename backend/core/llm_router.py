"""
LLM Router for multi-provider support with fallback
"""

import litellm
from typing import List, Dict, Any, Optional, AsyncIterator
import logging
from enum import Enum

from core.config import settings

logger = logging.getLogger(__name__)

# Configure LiteLLM
litellm.telemetry = False  # Disable telemetry
litellm.set_verbose = settings.DEBUG


class AgentType(str, Enum):
    """Agent types for model routing"""
    # Priority 1
    IMPLEMENTATION = "implementation"
    REVIEW = "review"
    ARCHITECT = "architect"
    QA = "qa"
    DEBUG = "debug"
    # Priority 2
    DOCUMENTATION = "documentation"
    REFACTORING = "refactoring"
    SECURITY = "security"
    DEVOPS = "devops"


class LLMRouter:
    """Routes LLM requests to appropriate models with fallback"""
    
    def __init__(self):
        self.model_map = {
            # Priority 1
            AgentType.IMPLEMENTATION: settings.MODEL_IMPLEMENTATION,
            AgentType.REVIEW: settings.MODEL_REVIEW,
            AgentType.ARCHITECT: settings.MODEL_ARCHITECT,
            AgentType.QA: settings.MODEL_QA,
            AgentType.DEBUG: settings.MODEL_DEBUG,
            # Priority 2
            AgentType.DOCUMENTATION: settings.MODEL_DOCUMENTATION,
            AgentType.REFACTORING: settings.MODEL_REFACTORING,
            AgentType.SECURITY: settings.MODEL_SECURITY,
            AgentType.DEVOPS: settings.MODEL_DEVOPS,
        }
        
        # Setup DeepSeek API key
        if settings.DEEPSEEK_API_KEY:
            litellm.api_key = settings.DEEPSEEK_API_KEY
            litellm.api_base = settings.DEEPSEEK_BASE_URL
        
        # Setup Llamafile for local sensitive data
        # Modern litellm handles custom base URLs directly in completion calls
        self.llamafile_base_url = settings.LLAMAFILE_BASE_URL if settings.LLAMAFILE_ENABLED else None
        
    async def complete(
        self,
        messages: List[Dict[str, str]],
        agent_type: AgentType,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        **kwargs
    ) -> Any:
        """
        Generate completion with fallback
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            agent_type: Type of agent making the request
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            stream: Whether to stream response
            **kwargs: Additional arguments for litellm
            
        Returns:
            Completion response
        """
        model = self.model_map.get(agent_type, settings.MODEL_FALLBACK)
        max_tokens = max_tokens or settings.MAX_OUTPUT_TOKENS
        
        try:
            logger.info(f"🤖 {agent_type.value} using model: {model}")
            
            # Use custom base URL for Llamafile
            completion_kwargs = kwargs.copy()
            if "llamafile" in model.lower() and self.llamafile_base_url:
                completion_kwargs["api_base"] = self.llamafile_base_url
            
            response = await litellm.acompletion(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream,
                **completion_kwargs
            )
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Model {model} failed: {e}")
            
            # Try fallback model
            if model != settings.MODEL_FALLBACK:
                logger.warning(f"Retrying with fallback model: {settings.MODEL_FALLBACK}")
                try:
                    # Use custom base URL for fallback if it's Llamafile
                    fallback_kwargs = kwargs.copy()
                    if "llamafile" in settings.MODEL_FALLBACK.lower() and self.llamafile_base_url:
                        fallback_kwargs["api_base"] = self.llamafile_base_url
                    
                    response = await litellm.acompletion(
                        model=settings.MODEL_FALLBACK,
                        messages=messages,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        stream=stream,
                        **fallback_kwargs
                    )
                    return response
                except Exception as fallback_error:
                    logger.error(f"❌ Fallback model also failed: {fallback_error}")
            
            raise
    
    async def stream_complete(
        self,
        messages: List[Dict[str, str]],
        agent_type: AgentType,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """
        Stream completion tokens
        
        Args:
            messages: List of message dicts
            agent_type: Type of agent
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional arguments
            
        Yields:
            Content chunks
        """
        response = await self.complete(
            messages=messages,
            agent_type=agent_type,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
            **kwargs
        )
        
        async for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    def get_model(self, agent_type: AgentType) -> str:
        """Get model name for agent type"""
        return self.model_map.get(agent_type, settings.MODEL_FALLBACK)
    
    def estimate_cost(self, input_tokens: int, output_tokens: int, model: str) -> float:
        """
        Estimate cost for a completion
        
        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            model: Model name
            
        Returns:
            Estimated cost in USD
        """
        try:
            cost = litellm.completion_cost(
                completion_response={
                    "usage": {
                        "prompt_tokens": input_tokens,
                        "completion_tokens": output_tokens
                    },
                    "model": model
                }
            )
            return cost
        except:
            return 0.0


# Global router instance
llm_router = LLMRouter()


async def get_completion(
    messages: List[Dict[str, str]],
    agent_type: AgentType = AgentType.IMPLEMENTATION,
    **kwargs
) -> str:
    """
    Convenience function for getting completion
    
    Args:
        messages: List of messages
        agent_type: Type of agent
        **kwargs: Additional arguments
        
    Returns:
        Generated text
    """
    response = await llm_router.complete(
        messages=messages,
        agent_type=agent_type,
        **kwargs
    )
    
    return response.choices[0].message.content

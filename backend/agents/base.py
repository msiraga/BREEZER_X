"""
Base agent class and interfaces
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import logging

from core.llm_router import llm_router, AgentType

logger = logging.getLogger(__name__)


class AgentContext(BaseModel):
    """Context provided to agents"""
    workspace_path: str
    current_file: Optional[str] = None
    selected_code: Optional[str] = None
    open_files: List[str] = []
    recent_changes: List[Dict[str, Any]] = []
    user_query: str
    additional_context: Dict[str, Any] = {}


class AgentResponse(BaseModel):
    """Agent response"""
    success: bool
    content: str
    metadata: Dict[str, Any] = {}
    actions: List[Dict[str, Any]] = []  # Suggested actions
    confidence: float = 1.0


class BaseAgent(ABC):
    """Base class for all agents"""
    
    def __init__(self, agent_type: AgentType):
        self.agent_type = agent_type
        self.logger = logging.getLogger(f"agent.{agent_type.value}")
    
    @abstractmethod
    async def process(self, context: AgentContext) -> AgentResponse:
        """
        Process request and generate response
        
        Args:
            context: Agent context with user query and code context
            
        Returns:
            Agent response
        """
        pass
    
    async def get_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """
        Get LLM completion for this agent
        
        Args:
            messages: Chat messages
            temperature: Sampling temperature
            **kwargs: Additional arguments
            
        Returns:
            Generated text
        """
        response = await llm_router.complete(
            messages=messages,
            agent_type=self.agent_type,
            temperature=temperature,
            **kwargs
        )
        
        return response.choices[0].message.content
    
    def build_system_prompt(self) -> str:
        """Build system prompt for this agent"""
        return f"You are a {self.agent_type.value} agent."
    
    def format_context(self, context: AgentContext) -> str:
        """Format context for LLM"""
        parts = [f"User Query: {context.user_query}"]
        
        if context.current_file:
            parts.append(f"\nCurrent File: {context.current_file}")
        
        if context.selected_code:
            parts.append(f"\nSelected Code:\n```\n{context.selected_code}\n```")
        
        if context.open_files:
            parts.append(f"\nOpen Files: {', '.join(context.open_files)}")
        
        return "\n".join(parts)
    
    async def log_interaction(
        self,
        context: AgentContext,
        response: AgentResponse
    ):
        """Log agent interaction for learning"""
        self.logger.info(
            f"Processed query: {context.user_query[:100]}... "
            f"Success: {response.success}, "
            f"Confidence: {response.confidence}"
        )

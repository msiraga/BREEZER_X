"""
Agent Orchestrator - Routes and coordinates multiple agents
"""

from typing import Dict, List, Optional, Any
from enum import Enum
import logging

from agents.base import AgentContext, AgentResponse
from agents.implementation import ImplementationAgent
from agents.review import ReviewAgent
from agents.debug import DebugAgent
from agents.documentation import DocumentationAgent
from agents.refactoring import RefactoringAgent
from agents.security import SecurityAgent
from agents.devops import DevOpsAgent


logger = logging.getLogger(__name__)


class RequestType(str, Enum):
    """Types of user requests"""
    IMPLEMENT = "implement"
    REVIEW = "review"
    DEBUG = "debug"
    REFACTOR = "refactor"
    EXPLAIN = "explain"
    TEST = "test"
    UNKNOWN = "unknown"


class AgentOrchestrator:
    """Coordinates multiple agents to handle complex tasks"""
    
    def __init__(self):
        self.agents = {
            # Priority 1
            "implementation": ImplementationAgent(),
            "review": ReviewAgent(),
            "debug": DebugAgent(),
            # Priority 2  
            "documentation": DocumentationAgent(),
            "refactoring": RefactoringAgent(),
            "security": SecurityAgent(),
            "devops": DevOpsAgent(),
        }
    
    async def process_request(
        self,
        context: AgentContext
    ) -> AgentResponse:
        """
        Process user request with appropriate agent(s)
        
        Args:
            context: Request context
            
        Returns:
            Agent response
        """
        try:
            # Classify request type
            request_type = self._classify_request(context.user_query)
            logger.info(f"Classified request as: {request_type.value}")
            
            # Route to appropriate agent
            if request_type == RequestType.IMPLEMENT:
                return await self.agents["implementation"].process(context)
            
            elif request_type == RequestType.REVIEW:
                return await self.agents["review"].process(context)
            
            elif request_type == RequestType.DEBUG:
                return await self.agents["debug"].process(context)
            
            elif request_type == RequestType.REFACTOR:
                # Use implementation agent for refactoring
                return await self.agents["implementation"].process(context)
            
            elif request_type == RequestType.EXPLAIN:
                # Use review agent to explain code
                return await self.agents["review"].process(context)
            
            else:
                # Default to implementation agent
                return await self.agents["implementation"].process(context)
                
        except Exception as e:
            logger.error(f"Orchestration failed: {e}", exc_info=True)
            return AgentResponse(
                success=False,
                content=f"Request processing failed: {str(e)}",
                confidence=0.0
            )
    
    def _classify_request(self, query: str) -> RequestType:
        """
        Classify user request type
        
        Args:
            query: User query
            
        Returns:
            Request type
        """
        query_lower = query.lower()
        
        # Implementation keywords
        if any(kw in query_lower for kw in [
            'create', 'implement', 'build', 'add', 'write',
            'generate', 'make', 'develop'
        ]):
            return RequestType.IMPLEMENT
        
        # Review keywords
        if any(kw in query_lower for kw in [
            'review', 'check', 'analyze', 'improve',
            'suggest', 'feedback', 'quality'
        ]):
            return RequestType.REVIEW
        
        # Debug keywords
        if any(kw in query_lower for kw in [
            'debug', 'fix', 'error', 'bug', 'problem',
            'issue', 'not working', 'broken', 'fails'
        ]):
            return RequestType.DEBUG
        
        # Refactor keywords
        if any(kw in query_lower for kw in [
            'refactor', 'clean', 'simplify', 'optimize',
            'restructure', 'reorganize'
        ]):
            return RequestType.REFACTOR
        
        # Explain keywords
        if any(kw in query_lower for kw in [
            'explain', 'what does', 'how does', 'why',
            'understand', 'clarify'
        ]):
            return RequestType.EXPLAIN
        
        return RequestType.UNKNOWN
    
    async def process_multi_agent(
        self,
        context: AgentContext,
        agent_sequence: List[str]
    ) -> List[AgentResponse]:
        """
        Process request with multiple agents in sequence
        
        Args:
            context: Request context
            agent_sequence: List of agent names to use
            
        Returns:
            List of agent responses
        """
        responses = []
        
        for agent_name in agent_sequence:
            if agent_name in self.agents:
                response = await self.agents[agent_name].process(context)
                responses.append(response)
                
                # Update context with previous response
                context.additional_context[f"{agent_name}_response"] = response.content
        
        return responses

    async def continue_with_tool(
        self,
        agent_name: str,
        conversation_state: Dict[str, Any],
        tool_results: List[Dict[str, Any]]
    ) -> AgentResponse:
        if agent_name not in self.agents:
            raise ValueError(f"Unknown agent: {agent_name}")

        agent = self.agents[agent_name]
        try:
            return await agent.continue_with_tool(conversation_state, tool_results)
        except NotImplementedError as exc:
            raise ValueError(f"Agent '{agent_name}' does not support tool continuation") from exc


# Global orchestrator instance
orchestrator = AgentOrchestrator()

"""
Agent API routes
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uuid
import asyncio

from agents.orchestrator import orchestrator
from agents.base import AgentContext, AgentResponse
from core.tool_state import tool_state_manager

router = APIRouter()


class AgentRequest(BaseModel):
    """Agent request model"""
    query: str
    workspace_path: str
    current_file: Optional[str] = None
    selected_code: Optional[str] = None
    open_files: List[str] = []
    additional_context: Dict[str, Any] = {}
    stream: bool = False


class AgentResponseModel(BaseModel):
    """Agent response model"""
    request_id: str
    success: bool
    content: str
    metadata: Dict[str, Any]
    actions: List[Dict[str, Any]]
    confidence: float
    requires_tool: bool = False
    tool_calls: List[Dict[str, Any]] = []


@router.post("/query", response_model=AgentResponseModel)
async def process_query(request: AgentRequest):
    """
    Process agent query
    
    Args:
        request: Agent request
        
    Returns:
        Agent response
    """
    try:
        # Generate request ID
        request_id = str(uuid.uuid4())
        
        # Build context
        context = AgentContext(
            workspace_path=request.workspace_path,
            current_file=request.current_file,
            selected_code=request.selected_code,
            open_files=request.open_files,
            user_query=request.query,
            additional_context=request.additional_context
        )
        
        # Process with orchestrator
        response = await orchestrator.process_request(context)
        
        if response.requires_tool and response.conversation_state:
            await tool_state_manager.set_state(
                request_id,
                {
                    "agent": response.conversation_state.get("agent"),
                    "conversation_state": response.conversation_state
                }
            )
        else:
            await tool_state_manager.clear_state(request_id)

        return AgentResponseModel(
            request_id=request_id,
            success=response.success,
            content=response.content,
            metadata=response.metadata,
            actions=response.actions,
            confidence=response.confidence,
            requires_tool=response.requires_tool,
            tool_calls=response.tool_calls
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query/stream")
async def process_query_stream(request: AgentRequest):
    """
    Process query with streaming response
    
    Args:
        request: Agent request
        
    Returns:
        Streaming response
    """
    async def generate():
        try:
            context = AgentContext(
                workspace_path=request.workspace_path,
                current_file=request.current_file,
                selected_code=request.selected_code,
                open_files=request.open_files,
                user_query=request.query,
                additional_context=request.additional_context
            )
            
            # For MVP, just send the response in chunks
            # TODO: Implement actual streaming from LLM
            response = await orchestrator.process_request(context)
            
            # Stream content in chunks
            chunk_size = 50
            content = response.content
            for i in range(0, len(content), chunk_size):
                chunk = content[i:i+chunk_size]
                yield f"data: {chunk}\n\n"
                await asyncio.sleep(0.01)  # Small delay for smoother streaming
            
            yield "data: [DONE]\n\n"
            
        except Exception as e:
            yield f"data: [ERROR] {str(e)}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")


@router.post("/multi-agent")
async def process_multi_agent(
    request: AgentRequest,
    agent_sequence: List[str]
):
    """
    Process request with multiple agents in sequence
    
    Args:
        request: Agent request
        agent_sequence: List of agent names (e.g., ["implementation", "review"])
        
    Returns:
        List of agent responses
    """
    try:
        context = AgentContext(
            workspace_path=request.workspace_path,
            current_file=request.current_file,
            selected_code=request.selected_code,
            open_files=request.open_files,
            user_query=request.query,
            additional_context=request.additional_context
        )
        
        responses = await orchestrator.process_multi_agent(context, agent_sequence)
        
        return {
            "request_id": str(uuid.uuid4()),
            "agents_used": agent_sequence,
            "responses": [
                {
                    "agent": agent_sequence[i],
                    "success": r.success,
                    "content": r.content,
                    "metadata": r.metadata,
                    "confidence": r.confidence
                }
                for i, r in enumerate(responses)
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class ToolResultItem(BaseModel):
    call_id: str
    name: str
    output: str


class ToolResultRequest(BaseModel):
    request_id: str
    tool_results: List[ToolResultItem]


@router.post("/tool-result", response_model=AgentResponseModel)
async def submit_tool_result(request: ToolResultRequest):
    state = await tool_state_manager.get_state(request.request_id)
    if not state:
        raise HTTPException(status_code=404, detail="No pending tool call for request")

    agent_name = state.get("agent")
    conversation_state = state.get("conversation_state")
    if not agent_name or not conversation_state:
        await tool_state_manager.clear_state(request.request_id)
        raise HTTPException(status_code=500, detail="Incomplete conversation state")

    try:
        response = await orchestrator.continue_with_tool(
            agent_name,
            conversation_state,
            [item.dict() for item in request.tool_results]
        )
    except Exception as exc:  # pylint: disable=broad-except
        await tool_state_manager.clear_state(request.request_id)
        raise HTTPException(status_code=500, detail=str(exc))

    if response.requires_tool and response.conversation_state:
        await tool_state_manager.set_state(
            request.request_id,
            {
                "agent": response.conversation_state.get("agent"),
                "conversation_state": response.conversation_state
            }
        )
    else:
        await tool_state_manager.clear_state(request.request_id)

    return AgentResponseModel(
        request_id=request.request_id,
        success=response.success,
        content=response.content,
        metadata=response.metadata,
        actions=response.actions,
        confidence=response.confidence,
        requires_tool=response.requires_tool,
        tool_calls=response.tool_calls
    )


@router.get("/agents")
async def list_agents():
    """
    List available agents
    
    Returns:
        List of agent information
    """
    return {
        "agents": [
            {
                "name": "implementation",
                "description": "Generates and edits code",
                "capabilities": ["code_generation", "refactoring", "feature_implementation"]
            },
            {
                "name": "review",
                "description": "Reviews code for quality and issues",
                "capabilities": ["code_review", "best_practices", "bug_detection"]
            },
            {
                "name": "debug",
                "description": "Debugs and troubleshoots code",
                "capabilities": ["error_analysis", "debugging", "root_cause_analysis"]
            }
        ]
    }

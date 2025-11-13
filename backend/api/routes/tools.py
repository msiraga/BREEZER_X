"""Tool execution API routes."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any

from services.tool_executor import ToolExecutionService, ToolExecutionError

router = APIRouter()


class ToolExecutionRequest(BaseModel):
    workspace_path: str
    tool: str
    arguments: Dict[str, Any] = {}


class ToolExecutionResponse(BaseModel):
    success: bool
    result: Dict[str, Any]


@router.post("/execute", response_model=ToolExecutionResponse)
async def execute_tool(request: ToolExecutionRequest) -> ToolExecutionResponse:
    try:
        executor = ToolExecutionService(request.workspace_path)
        result = executor.execute(request.tool, request.arguments)
    except ToolExecutionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return ToolExecutionResponse(success=True, result=result)

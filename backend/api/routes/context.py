"""
Code context and indexing endpoints
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from services.vector_store import (
    index_code_snippet,
    search_code,
    delete_workspace_code
)

router = APIRouter()


class IndexRequest(BaseModel):
    content: str
    file_path: str
    language: str
    workspace_id: str
    metadata: dict = {}


class SearchRequest(BaseModel):
    query: str
    workspace_id: Optional[str] = None
    language: Optional[str] = None
    limit: int = 10


@router.post("/index")
async def index_code(request: IndexRequest):
    """Index code snippet for semantic search"""
    try:
        point_id = await index_code_snippet(
            content=request.content,
            file_path=request.file_path,
            language=request.language,
            workspace_id=request.workspace_id,
            metadata=request.metadata
        )
        
        return {
            "success": True,
            "point_id": point_id,
            "message": "Code indexed successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search")
async def search_context(request: SearchRequest):
    """Search for relevant code"""
    try:
        results = await search_code(
            query=request.query,
            workspace_id=request.workspace_id,
            language=request.language,
            limit=request.limit
        )
        
        return {
            "success": True,
            "results": results,
            "count": len(results)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/workspace/{workspace_id}")
async def delete_workspace(workspace_id: str):
    """Delete all indexed code for workspace"""
    try:
        await delete_workspace_code(workspace_id)
        
        return {
            "success": True,
            "message": f"Workspace {workspace_id} deleted"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

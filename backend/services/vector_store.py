"""
Vector store service for code search using Qdrant
"""

from qdrant_client import AsyncQdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue
)
from typing import List, Dict, Any, Optional
import hashlib
import logging

from core.config import settings
from core.embeddings import embed_text, embed_texts, get_embedding_dimension

logger = logging.getLogger(__name__)

# Collection names
COLLECTION_CODE = "code_snippets"
COLLECTION_DOCS = "documentation"

# Global client
_qdrant_client: Optional[AsyncQdrantClient] = None


async def init_vector_store():
    """Initialize Qdrant vector store"""
    global _qdrant_client
    
    try:
        _qdrant_client = AsyncQdrantClient(
            url=settings.qdrant_url,
            api_key=settings.QDRANT_API_KEY if settings.QDRANT_API_KEY else None
        )
        
        # Check if collections exist
        collections = await _qdrant_client.get_collections()
        collection_names = [col.name for col in collections.collections]
        
        embedding_dim = get_embedding_dimension()
        
        # Create code snippets collection if not exists
        if COLLECTION_CODE not in collection_names:
            await _qdrant_client.create_collection(
                collection_name=COLLECTION_CODE,
                vectors_config=VectorParams(
                    size=embedding_dim,
                    distance=Distance.COSINE
                )
            )
            logger.info(f"✅ Created collection: {COLLECTION_CODE}")
        
        # Create documentation collection if not exists
        if COLLECTION_DOCS not in collection_names:
            await _qdrant_client.create_collection(
                collection_name=COLLECTION_DOCS,
                vectors_config=VectorParams(
                    size=embedding_dim,
                    distance=Distance.COSINE
                )
            )
            logger.info(f"✅ Created collection: {COLLECTION_DOCS}")
        
        logger.info("✅ Vector store initialized")
        
    except Exception as e:
        logger.error(f"❌ Vector store initialization failed: {e}")
        raise


def get_client() -> AsyncQdrantClient:
    """Get Qdrant client instance"""
    if not _qdrant_client:
        raise RuntimeError("Vector store not initialized")
    return _qdrant_client


async def index_code_snippet(
    content: str,
    file_path: str,
    language: str,
    workspace_id: str,
    metadata: Optional[Dict[str, Any]] = None
) -> str:
    """
    Index a code snippet
    
    Args:
        content: Code content
        file_path: Path to file
        language: Programming language
        workspace_id: Workspace identifier
        metadata: Additional metadata
        
    Returns:
        Point ID
    """
    client = get_client()
    
    # Generate ID from content hash
    point_id = hashlib.sha256(
        f"{workspace_id}:{file_path}:{content}".encode()
    ).hexdigest()[:16]
    
    # Generate embedding
    embedding = await embed_text(content)
    
    # Prepare payload
    payload = {
        "content": content,
        "file_path": file_path,
        "language": language,
        "workspace_id": workspace_id,
        **(metadata or {})
    }
    
    # Upsert point
    await client.upsert(
        collection_name=COLLECTION_CODE,
        points=[
            PointStruct(
                id=point_id,
                vector=embedding,
                payload=payload
            )
        ]
    )
    
    return point_id


async def search_code(
    query: str,
    workspace_id: Optional[str] = None,
    language: Optional[str] = None,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Search for code snippets
    
    Args:
        query: Search query
        workspace_id: Filter by workspace
        language: Filter by language
        limit: Maximum results
        
    Returns:
        List of matching code snippets with scores
    """
    client = get_client()
    
    # Generate query embedding
    query_vector = await embed_text(query)
    
    # Build filter
    conditions = []
    if workspace_id:
        conditions.append(
            FieldCondition(
                key="workspace_id",
                match=MatchValue(value=workspace_id)
            )
        )
    if language:
        conditions.append(
            FieldCondition(
                key="language",
                match=MatchValue(value=language)
            )
        )
    
    query_filter = Filter(must=conditions) if conditions else None
    
    # Search
    results = await client.search(
        collection_name=COLLECTION_CODE,
        query_vector=query_vector,
        query_filter=query_filter,
        limit=limit
    )
    
    return [
        {
            "score": hit.score,
            "content": hit.payload["content"],
            "file_path": hit.payload["file_path"],
            "language": hit.payload["language"],
            **{k: v for k, v in hit.payload.items() 
               if k not in ["content", "file_path", "language"]}
        }
        for hit in results
    ]


async def delete_workspace_code(workspace_id: str):
    """Delete all code snippets for a workspace"""
    client = get_client()
    
    await client.delete(
        collection_name=COLLECTION_CODE,
        points_selector=Filter(
            must=[
                FieldCondition(
                    key="workspace_id",
                    match=MatchValue(value=workspace_id)
                )
            ]
        )
    )
    
    logger.info(f"Deleted code snippets for workspace: {workspace_id}")


async def get_collection_stats() -> Dict[str, Any]:
    """Get vector store statistics"""
    client = get_client()
    
    code_info = await client.get_collection(COLLECTION_CODE)
    docs_info = await client.get_collection(COLLECTION_DOCS)
    
    return {
        "code_snippets": {
            "count": code_info.points_count,
            "status": code_info.status
        },
        "documentation": {
            "count": docs_info.points_count,
            "status": docs_info.status
        }
    }

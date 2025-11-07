"""
Embeddings initialization with GPU support
"""

import torch
from sentence_transformers import SentenceTransformer
from typing import List, Optional
import logging

from core.config import settings

logger = logging.getLogger(__name__)

# Global embeddings model
_embeddings_model: Optional[SentenceTransformer] = None


async def init_embeddings():
    """Initialize embeddings model"""
    global _embeddings_model
    
    if settings.EMBEDDINGS_PROVIDER != "local":
        logger.info("Using cloud embeddings provider")
        return
    
    try:
        # Check GPU availability
        device = settings.EMBEDDINGS_DEVICE
        if device == "cuda" and not torch.cuda.is_available():
            logger.warning("CUDA requested but not available, falling back to CPU")
            device = "cpu"
        
        if device == "cuda":
            logger.info(f"🎮 Loading embeddings on GPU: {torch.cuda.get_device_name(0)}")
        else:
            logger.info("💻 Loading embeddings on CPU")
        
        # Load model
        _embeddings_model = SentenceTransformer(
            settings.EMBEDDINGS_MODEL,
            device=device
        )
        
        # Warmup
        _ = _embeddings_model.encode(["warmup"], show_progress_bar=False)
        
        logger.info(f"✅ Embeddings model loaded: {settings.EMBEDDINGS_MODEL}")
        
    except Exception as e:
        logger.error(f"❌ Failed to load embeddings model: {e}")
        logger.warning("Falling back to cloud embeddings")
        settings.EMBEDDINGS_PROVIDER = "openai"


def get_embeddings_model() -> Optional[SentenceTransformer]:
    """Get embeddings model instance"""
    return _embeddings_model


async def embed_texts(texts: List[str]) -> List[List[float]]:
    """
    Generate embeddings for texts
    
    Args:
        texts: List of text strings
        
    Returns:
        List of embedding vectors
    """
    if settings.EMBEDDINGS_PROVIDER == "local" and _embeddings_model:
        # Use local GPU model
        embeddings = _embeddings_model.encode(
            texts,
            batch_size=32,
            show_progress_bar=False,
            convert_to_numpy=True
        )
        return embeddings.tolist()
    
    elif settings.EMBEDDINGS_PROVIDER == "openai":
        # Use OpenAI embeddings API
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        
        response = await client.embeddings.create(
            model=settings.OPENAI_EMBEDDING_MODEL,
            input=texts
        )
        
        return [item.embedding for item in response.data]
    
    else:
        raise ValueError(f"Unknown embeddings provider: {settings.EMBEDDINGS_PROVIDER}")


async def embed_text(text: str) -> List[float]:
    """
    Generate embedding for single text
    
    Args:
        text: Text string
        
    Returns:
        Embedding vector
    """
    embeddings = await embed_texts([text])
    return embeddings[0]


def get_embedding_dimension() -> int:
    """Get embedding dimension"""
    if settings.EMBEDDINGS_PROVIDER == "local":
        if _embeddings_model:
            return _embeddings_model.get_sentence_embedding_dimension()
        return 768  # Default dimension
    elif settings.EMBEDDINGS_PROVIDER == "openai":
        if "small" in settings.OPENAI_EMBEDDING_MODEL:
            return 1536
        return 3072  # large model
    return 768

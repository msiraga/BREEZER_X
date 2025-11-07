"""
Database initialization and connection management
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, JSON, Text, Boolean
from datetime import datetime
import logging

from core.config import settings

logger = logging.getLogger(__name__)

# Create async engine
engine = create_async_engine(
    settings.database_url,
    echo=settings.DEBUG,
    pool_size=10,
    max_overflow=20
)

# Create session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Base class for models
Base = declarative_base()


class Task(Base):
    """Task model for tracking agent tasks"""
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String(36), unique=True, index=True)
    user_id = Column(String(100), index=True)
    description = Column(Text)
    status = Column(String(20), default="pending")  # pending, in_progress, completed, failed
    assigned_agent = Column(String(50))
    context = Column(JSON)
    result = Column(JSON)
    error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)


class AgentMemory(Base):
    """Agent memory for learning from past interactions"""
    __tablename__ = "agent_memory"
    
    id = Column(Integer, primary_key=True, index=True)
    memory_id = Column(String(36), unique=True, index=True)
    agent_type = Column(String(50), index=True)
    pattern = Column(Text)
    context_hash = Column(String(64), index=True)
    outcome = Column(String(20))  # success, failure
    feedback = Column(Text, nullable=True)
    usage_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used = Column(DateTime, default=datetime.utcnow)


class CodeContext(Base):
    """Store code context and relationships"""
    __tablename__ = "code_context"
    
    id = Column(Integer, primary_key=True, index=True)
    context_id = Column(String(36), unique=True, index=True)
    workspace_path = Column(String(500), index=True)
    file_path = Column(String(500), index=True)
    content_hash = Column(String(64))
    symbols = Column(JSON)  # functions, classes, imports
    dependencies = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


async def init_db():
    """Initialize database tables"""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("✅ Database tables created/verified")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise


async def get_db():
    """Dependency for getting database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

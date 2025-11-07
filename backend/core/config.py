"""
Configuration management using Pydantic Settings
"""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_WORKERS: int = 4
    DEBUG: bool = False
    
    # Security
    SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION: int = 86400
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "vscode-webview://*",
        "http://localhost:*",
        "http://127.0.0.1:*"
    ]
    
    # LLM API Keys
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"
    OPENAI_API_KEY: str = ""
    OPENAI_ORG_ID: str = ""
    ANTHROPIC_API_KEY: str = ""
    
    # Local LLM (Llamafile - Mistral 7B)
    LLAMAFILE_ENABLED: bool = True
    LLAMAFILE_BASE_URL: str = "http://localhost:8080"
    LLAMAFILE_MODEL: str = "mistral-7b-instruct"
    USE_LOCAL_FOR_SENSITIVE: bool = True
    
    # Database
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "breezer"
    POSTGRES_USER: str = "breezer"
    POSTGRES_PASSWORD: str = "breezer123"
    
    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ""
    
    # Qdrant
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_API_KEY: str = ""
    
    # Model Configuration (DeepSeek with reasoning)
    MODEL_IMPLEMENTATION: str = "deepseek/deepseek-chat"
    MODEL_REVIEW: str = "deepseek/deepseek-chat"
    MODEL_ARCHITECT: str = "deepseek/deepseek-reasoner"
    MODEL_QA: str = "deepseek/deepseek-chat"
    MODEL_DEBUG: str = "deepseek/deepseek-reasoner"
    MODEL_DOCUMENTATION: str = "deepseek/deepseek-chat"
    MODEL_REFACTORING: str = "deepseek/deepseek-chat"
    MODEL_SECURITY: str = "deepseek/deepseek-chat"
    MODEL_DEVOPS: str = "deepseek/deepseek-chat"
    MODEL_FALLBACK: str = "llamafile/mistral-7b-instruct"
    
    # Embeddings
    EMBEDDINGS_PROVIDER: str = "local"  # or 'openai'
    EMBEDDINGS_MODEL: str = "sentence-transformers/all-mpnet-base-v2"
    EMBEDDINGS_DEVICE: str = "cuda"  # or 'cpu'
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    
    # Sandbox (Strategy B - Heavy Isolation)
    SANDBOX_ENABLED: bool = True
    SANDBOX_STRATEGY: str = "docker-in-docker"
    SANDBOX_TIMEOUT: int = 300
    SANDBOX_MEMORY_LIMIT: str = "2g"
    SANDBOX_CPU_LIMIT: int = 2
    SANDBOX_NETWORK_ISOLATED: bool = True
    SANDBOX_READ_ONLY_ROOT: bool = True
    
    # Context
    MAX_CONTEXT_TOKENS: int = 128000
    MAX_OUTPUT_TOKENS: int = 4096
    
    # Caching
    CACHE_ENABLED: bool = True
    CACHE_TTL: int = 3600
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 60
    
    # Telemetry (DISABLED - Company-wide sensitive data)
    TELEMETRY_ENABLED: bool = False
    ANALYTICS_ENABLED: bool = False
    CRASH_REPORTING: bool = False
    USAGE_STATS: bool = False
    DATA_RESIDENCY: str = "on-premise"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/breezer.log"
    
    @property
    def database_url(self) -> str:
        """Construct PostgreSQL URL"""
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    @property
    def redis_url(self) -> str:
        """Construct Redis URL"""
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}"
    
    @property
    def qdrant_url(self) -> str:
        """Construct Qdrant URL"""
        return f"http://{self.QDRANT_HOST}:{self.QDRANT_PORT}"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()

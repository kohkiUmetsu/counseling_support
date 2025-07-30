from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # AWS S3
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION: str = "ap-northeast-1"
    S3_BUCKET_NAME: str
    
    # Database
    DATABASE_URL: str
    VECTOR_DATABASE_URL: Optional[str] = None
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    
    # Debug
    DEBUG: bool = False
    
    # File Upload
    MAX_UPLOAD_SIZE: int = 500 * 1024 * 1024  # 500MB
    ALLOWED_AUDIO_FORMATS: list[str] = [
        "audio/webm",
        "audio/mp3",
        "audio/mpeg",
        "audio/wav",
        "audio/x-wav",
        "audio/mp4",
        "audio/x-m4a",
    ]
    
    # OpenAI
    OPENAI_API_KEY: Optional[str] = None
    
    # Vector Search Settings
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    EMBEDDING_DIMENSIONS: int = 1536
    MAX_CHUNK_TOKENS: int = 512
    SIMILARITY_THRESHOLD: float = 0.7
    
    # Clustering Settings
    MIN_CLUSTER_SIZE: int = 5
    MAX_CLUSTERS: int = 15
    
    # Redis (for caching)
    REDIS_URL: str = "redis://localhost:6379"
    
    class Config:
        env_file = ".env"
        extra = "ignore"  # 未定義フィールドを無視

settings = Settings()
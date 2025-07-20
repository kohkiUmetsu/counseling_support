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
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    
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
    
    class Config:
        env_file = ".env"

settings = Settings()
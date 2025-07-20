from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://counseling_user:counseling_password@localhost:5432/counseling_db"
    vector_database_url: str = "postgresql://vector_user:vector_password@localhost:5433/counseling_vector_db"
    
    # Application
    app_name: str = "Counseling Support API"
    debug: bool = True
    environment: str = "development"
    
    # API
    api_v1_str: str = "/api/v1"
    
    # CORS
    allowed_origins: list = ["http://localhost:3000"]
    
    # AWS
    aws_region: str = "ap-northeast-1"
    s3_bucket_name: str = "counseling-support-audio-files"
    
    # OpenAI
    openai_api_key: Optional[str] = None
    
    # Security
    secret_key: str = "development-secret-key-change-in-production"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import List
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Environment
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    DEBUG: bool = Field(default=True, env="DEBUG")
    
    # API Configuration
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "Voice Clone Platform"
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30  # 30 days
    
    # CORS - Handled manually to avoid pydantic parsing issues
    
    # Database
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    
    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    
    # Firebase Configuration
    FIREBASE_PROJECT_ID: str = Field(..., env="FIREBASE_PROJECT_ID")
    FIREBASE_PRIVATE_KEY_ID: str = Field(..., env="FIREBASE_PRIVATE_KEY_ID")
    FIREBASE_PRIVATE_KEY: str = Field(..., env="FIREBASE_PRIVATE_KEY")
    FIREBASE_CLIENT_EMAIL: str = Field(..., env="FIREBASE_CLIENT_EMAIL")
    FIREBASE_CLIENT_ID: str = Field(..., env="FIREBASE_CLIENT_ID")
    FIREBASE_AUTH_URI: str = Field(
        default="https://accounts.google.com/o/oauth2/auth",
        env="FIREBASE_AUTH_URI"
    )
    FIREBASE_TOKEN_URI: str = Field(
        default="https://oauth2.googleapis.com/token",
        env="FIREBASE_TOKEN_URI"
    )
    
    # AWS S3 Configuration
    AWS_ACCESS_KEY_ID: str = Field(..., env="AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: str = Field(..., env="AWS_SECRET_ACCESS_KEY")
    AWS_REGION: str = Field(default="us-west-2", env="AWS_REGION")
    AWS_S3_BUCKET: str = Field(..., env="AWS_S3_BUCKET")
    
    # TTS Configuration
    TTS_MODEL_PATH: str = Field(default="./models", env="TTS_MODEL_PATH")
    TTS_OUTPUT_PATH: str = Field(default="./audio", env="TTS_OUTPUT_PATH")
    MAX_AUDIO_DURATION: int = Field(default=300, env="MAX_AUDIO_DURATION")  # 5 minutes
    SUPPORTED_AUDIO_FORMATS: List[str] = ["wav", "mp3", "flac", "ogg"]
    
    # Voice Processing
    SAMPLE_RATE: int = 22050
    HOP_LENGTH: int = 256
    WIN_LENGTH: int = 1024
    N_FFT: int = 1024
    N_MELS: int = 80
    
    # Watermarking
    WATERMARK_STRENGTH: float = 0.1
    WATERMARK_KEY: str = Field(..., env="WATERMARK_KEY")
    
    # Celery Configuration
    CELERY_BROKER_URL: str = Field(default="redis://localhost:6379/0", env="CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND: str = Field(default="redis://localhost:6379/0", env="CELERY_RESULT_BACKEND")
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FILE: str = Field(default="voice_clone.log", env="LOG_FILE")
    
    # Security
    BCRYPT_ROUNDS: int = 12
    JWT_ALGORITHM: str = "HS256"
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = Field(default=100, env="RATE_LIMIT_PER_MINUTE")
    
    # File Upload
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB
    UPLOAD_PATH: str = Field(default="./uploads", env="UPLOAD_PATH")
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Handle ALLOWED_ORIGINS completely manually (as object attribute, not pydantic field)
        origins_env = os.getenv('ALLOWED_ORIGINS')
        if origins_env:
            object.__setattr__(self, 'ALLOWED_ORIGINS', [origin.strip() for origin in origins_env.split(',') if origin.strip()])
        else:
            object.__setattr__(self, 'ALLOWED_ORIGINS', [
                "http://localhost:3000",
                "http://127.0.0.1:3000",
                "http://localhost:3001",
                "http://127.0.0.1:3001",
                "http://localhost:8000"
            ])


# Create settings instance
settings = Settings()

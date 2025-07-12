"""
JARVIS 4.0 Configuration Management
Environment-based settings with validation
"""
from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Application
    APP_NAME: str = "JARVIS 4.0"
    VERSION: str = "4.0.0"
    DEBUG: bool = False
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Security
    SECRET_KEY: str = "jarvis-4.0-super-secret-key-change-in-production"
    JWT_SECRET_KEY: str = "jarvis-4.0-jwt-secret-key"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    # Database
    DATABASE_URL: str = "sqlite:///./jarvis.db"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # AI Models
    OLLAMA_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama2"
    WHISPER_MODEL: str = "base"
    
    # Vision
    YOLO_MODEL: str = "yolov8n.pt"
    
    # Voice
    TTS_ENGINE: str = "pyttsx3"  # or "elevenlabs" for advanced
    
    # File Upload
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    UPLOAD_DIR: str = "./uploads"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/jarvis.log"
    
    # Features
    ENABLE_VOICE: bool = True
    ENABLE_VISION: bool = True
    ENABLE_PLUGINS: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Global settings instance
settings = Settings()

# Create directories if they don't exist
os.makedirs(os.path.dirname(settings.LOG_FILE), exist_ok=True)
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
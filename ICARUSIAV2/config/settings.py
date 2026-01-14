"""
ICARUSIAV2 settings (pydantic-settings)
"""

from __future__ import annotations

from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    # App
    APP_NAME: str = "ICARUSIAV2"
    DEBUG: bool = False
    VERSION: str = "2.0.0"

    # API / CORS
    API_V1_PREFIX: str = "/api/v1"
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
    ]

    # OpenAI
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"

    # Cognitive tuning
    MAX_REASONING_DEPTH: int = 5
    PARALLEL_DECODING_WORKERS: int = 4
    THREAD_ROT_THRESHOLD: float = 0.7
    MEMORY_RETENTION_DAYS: int = 30

    # Sales
    MAX_CONVERSATION_TURNS: int = 50
    OBJECTION_HANDLING_ENABLED: bool = True
    SALES_SCRIPT_AUTO_ADAPT: bool = True

    # Twilio
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_PHONE_NUMBER: Optional[str] = None

    # WhatsApp Business API
    WHATSAPP_API_TOKEN: Optional[str] = None
    WHATSAPP_PHONE_NUMBER_ID: Optional[str] = None
    WHATSAPP_VERIFY_TOKEN: Optional[str] = None

    # Google Cloud
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None
    GOOGLE_TTS_VOICE: str = "es-ES-Neural2-D"

    # Enterprise
    CRM_SYNC_INTERVAL: int = 300
    ANALYTICS_UPDATE_INTERVAL: int = 60
    FEEDBACK_LEARNING_ENABLED: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

"""
Configuration settings for ICARUSIAV2
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
import os
from pathlib import Path


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "ICARUSIAV2"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    VERSION: str = "2.0.0"
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "https://lustinia.web.app"
    ]
    
    # OpenAI
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-large"
    
    # Firebase
    FIREBASE_PROJECT_ID: str = os.getenv("FIREBASE_PROJECT_ID", "lustinia")
    FIREBASE_CREDENTIALS_PATH: Optional[str] = os.getenv("FIREBASE_CREDENTIALS_PATH")
    
    # Database
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT", "5432"))
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "icarus")
    
    # Redis
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    
    # Vector Database
    CHROMA_PERSIST_DIR: str = os.getenv("CHROMA_PERSIST_DIR", "./data/chroma")
    
    # Twilio
    TWILIO_ACCOUNT_SID: Optional[str] = os.getenv("TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN: Optional[str] = os.getenv("TWILIO_AUTH_TOKEN")
    TWILIO_PHONE_NUMBER: Optional[str] = os.getenv("TWILIO_PHONE_NUMBER")
    
    # WhatsApp Business API
    WHATSAPP_API_TOKEN: Optional[str] = os.getenv("WHATSAPP_API_TOKEN")
    WHATSAPP_PHONE_NUMBER_ID: Optional[str] = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
    WHATSAPP_VERIFY_TOKEN: Optional[str] = os.getenv("WHATSAPP_VERIFY_TOKEN")
    
    # Google Cloud TTS/STT
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    GOOGLE_TTS_VOICE: str = os.getenv("GOOGLE_TTS_VOICE", "es-ES-Neural2-D")
    
    # Cognitive Settings
    MAX_REASONING_DEPTH: int = 5
    PARALLEL_DECODING_WORKERS: int = 4
    THREAD_ROT_THRESHOLD: float = 0.7
    MEMORY_RETENTION_DAYS: int = 30
    
    # Sales Settings
    MAX_CONVERSATION_TURNS: int = 50
    OBJECTION_HANDLING_ENABLED: bool = True
    SALES_SCRIPT_AUTO_ADAPT: bool = True
    
    # Enterprise Settings
    CRM_SYNC_INTERVAL: int = 300  # seconds
    ANALYTICS_UPDATE_INTERVAL: int = 60  # seconds
    FEEDBACK_LEARNING_ENABLED: bool = True
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

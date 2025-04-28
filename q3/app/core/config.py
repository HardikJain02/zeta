import os
from pydantic import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Zeta Banking API"
    
    # Database settings
    DATABASE_URI: str = os.getenv("DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/banking")
    DB_POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "20"))
    DB_MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", "10"))
    DB_POOL_TIMEOUT: int = int(os.getenv("DB_POOL_TIMEOUT", "30"))
    DB_POOL_RECYCLE: int = int(os.getenv("DB_POOL_RECYCLE", "1800"))
    
    # Performance settings
    WORKERS_COUNT: int = int(os.getenv("WORKERS_COUNT", "4"))
    
    # API rate limiting
    RATE_LIMIT_ENABLED: bool = bool(os.getenv("RATE_LIMIT_ENABLED", "True"))
    RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    RATE_LIMIT_PERIOD_SECONDS: int = int(os.getenv("RATE_LIMIT_PERIOD_SECONDS", "60"))
    
    # Retry settings
    MAX_TRANSACTION_RETRIES: int = int(os.getenv("MAX_TRANSACTION_RETRIES", "3"))
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings() 
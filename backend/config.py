from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./sahakaar_seva.db"  # fallback for local dev
    SECRET_KEY: str = "dev-secret-key-change-in-production-32chars-min-length"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    
    DEFAULT_WORKER_PERCENTAGE: float = 88.0
    DEFAULT_COOPERATIVE_PERCENTAGE: float = 6.0
    DEFAULT_PLATFORM_PERCENTAGE: float = 6.0
    
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:8000,http://localhost:5173"
    
    ENV: str = "development"
    
    class Config:
        env_file = "../.env"
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()

def get_cors_origins() -> List[str]:
    return [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]

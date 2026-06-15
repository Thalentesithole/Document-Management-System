import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Secure AI-Powered DMS"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development" # 'development' or 'production'
    
    # Database Settings
    DATABASE_URL: str
    
    # Supabase Integrations
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    SUPABASE_JWT_SECRET: str = ""
    
    # JWT Config
    SECRET_KEY: str = "supersecretkey" # Override with JWT_SECRET_KEY in prod
    JWT_SECRET_KEY: Optional[str] = None
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440 # 24 hours
    
    # Redis / Celery
    REDIS_URL: str
    
    # Google Gemini API
    GEMINI_API_KEY: str
    
    # Email (Resend)
    EMAIL_PROVIDER: str = "resend"
    RESEND_API_KEY: Optional[str] = None
    SMTP_FROM_EMAIL: str = "noreply@example.com"
    
    # Monitoring
    SENTRY_DSN: Optional[str] = None
    
    # URLs
    FRONTEND_URL: str = "http://localhost:5173"
    BACKEND_URL: str = "http://localhost:8000"
    
    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True, extra="ignore")

    @model_validator(mode='after')
    def validate_production_settings(self) -> 'Settings':
        if self.ENVIRONMENT == "production":
            required_prod = [
                ("DATABASE_URL", self.DATABASE_URL),
                ("REDIS_URL", self.REDIS_URL),
                ("GEMINI_API_KEY", self.GEMINI_API_KEY),
                ("JWT_SECRET_KEY", self.JWT_SECRET_KEY),
                ("RESEND_API_KEY", self.RESEND_API_KEY),
            ]
            missing = [name for name, val in required_prod if not val or val == ""]
            if missing:
                raise ValueError(f"Missing required environment variables for production: {', '.join(missing)}")
            
            # Use JWT_SECRET_KEY as SECRET_KEY in prod
            if self.JWT_SECRET_KEY:
                self.SECRET_KEY = self.JWT_SECRET_KEY
        return self

settings = Settings()

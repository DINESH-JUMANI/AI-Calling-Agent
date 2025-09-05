import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # OpenAI
    openai_api_key: str
    
    # Twilio
    twilio_account_sid: str
    twilio_auth_token: str
    
    # ElevenLabs
    elevenlabs_api_key: str
    
    # Database
    database_url: str
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # App
    secret_key: str
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000
    
    # N8N
    n8n_base_url: Optional[str] = None
    
    class Config:
        env_file = ".env"
        
settings = Settings()
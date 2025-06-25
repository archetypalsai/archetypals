from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    # API Settings
    APP_NAME: str = "Constitutional AI Validator"
    DEBUG: bool = False
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    
    # AnythingLLM Settings
    ANYTHINGLLM_API_URL: str
    ANYTHINGLLM_API_KEY: str
    ANYTHINGLLM_WORKSPACE_ID: str
    
    # CrewAI Settings
    CREWAI_MAX_ITERATIONS: int = 3
    CREWAI_TIMEOUT: int = 30
    
    # Safety Settings
    MAX_REJECTIONS: int = 2
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
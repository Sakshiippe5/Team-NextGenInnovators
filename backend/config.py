from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    GROQ_API_KEY: str = "your_groq_api_key_here"
    MODEL_NAME: str = "llama-3.3-70b-versatile" # Default Groq model
    APP_NAME: str = "PsychProfileAgent"
    DEBUG: bool = False

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()

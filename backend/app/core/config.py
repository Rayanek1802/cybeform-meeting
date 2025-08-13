"""
Configuration settings for CybeMeeting backend
"""
import os
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings"""
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    MODEL_NAME: str = os.getenv("MODEL_NAME", "gpt-4o")
    WHISPER_API: str = os.getenv("WHISPER_API", "on")
    
    # Hugging Face Configuration
    HUGGINGFACE_TOKEN: str = os.getenv("HUGGINGFACE_TOKEN", "")
    
    # Application Configuration
    DATA_PATH: str = "./data"
    MAX_AUDIO_SIZE_MB: int = 500
    ALLOWED_AUDIO_FORMATS: str = "mp3,wav,m4a,webm,opus"
    
    # Authentication Configuration
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    
    # Development
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    
    @property
    def allowed_formats_list(self) -> List[str]:
        """Get allowed audio formats as list"""
        return [fmt.strip().lower() for fmt in self.ALLOWED_AUDIO_FORMATS.split(",")]
    
    @property
    def max_audio_size_bytes(self) -> int:
        """Get max audio size in bytes"""
        return self.MAX_AUDIO_SIZE_MB * 1024 * 1024
    
    @property
    def is_openai_available(self) -> bool:
        """Check if OpenAI API is configured"""
        return bool(self.OPENAI_API_KEY)
    
    @property
    def is_huggingface_available(self) -> bool:
        """Check if Hugging Face is configured"""
        return bool(self.HUGGINGFACE_TOKEN)
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()

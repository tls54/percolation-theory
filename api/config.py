"""API configuration."""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """API settings loaded from environment variables."""
    
    # API settings
    api_title: str = "Percolation Theory API"
    api_version: str = "0.1.0"
    api_description: str = "High-performance percolation simulation API"
    
    # CORS settings
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:5173"]  # React dev servers
    
    # Simulation defaults
    default_N: int = 50
    default_num_trials: int = 100
    max_N: int = 500  # Safety limit
    max_trials: int = 1000
    
    # Performance
    use_cpp: bool = True  # Use C++ if available
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
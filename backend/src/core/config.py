"""
Core Configuration
Application settings and configuration management
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application settings"""

    # Database settings
    DB_HOST: str = os.getenv('DB_HOST', 'localhost')
    DB_PORT: int = int(os.getenv('DB_PORT', 5432))
    DB_NAME: str = os.getenv('DB_NAME', 'construction_db')
    DB_USER: str = os.getenv('DB_USER', 'admin')
    DB_PASSWORD: str = os.getenv('DB_PASSWORD', 'admin123')

    # Ollama settings
    OLLAMA_BASE_URL: str = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
    OLLAMA_MODEL: str = os.getenv('OLLAMA_MODEL', 'gemma:2b')

    # API settings
    API_V1_PREFIX: str = '/api/v1'
    PROJECT_NAME: str = 'Construction AI Risk Monitor'
    VERSION: str = '1.0.0'

    # CORS settings
    CORS_ORIGINS: list = ['http://localhost:5173', 'http://localhost:3000']


settings = Settings()

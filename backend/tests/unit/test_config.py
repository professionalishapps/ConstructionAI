"""
Test configuration settings
"""
import pytest
from src.core.config import settings


def test_settings_exist():
    """Test that settings object exists"""
    assert settings is not None


def test_database_settings():
    """Test database settings"""
    assert hasattr(settings, 'DB_HOST')
    assert hasattr(settings, 'DB_PORT')
    assert hasattr(settings, 'DB_NAME')
    assert hasattr(settings, 'DB_USER')
    assert hasattr(settings, 'DB_PASSWORD')
    assert isinstance(settings.DB_PORT, int)


def test_api_settings():
    """Test API settings"""
    assert settings.API_V1_PREFIX == '/api/v1'
    assert settings.PROJECT_NAME == 'Construction AI Risk Monitor'
    assert settings.VERSION == '1.0.0'


def test_cors_settings():
    """Test CORS settings"""
    assert isinstance(settings.CORS_ORIGINS, list)
    assert 'http://localhost:5173' in settings.CORS_ORIGINS


def test_ollama_settings():
    """Test Ollama settings"""
    assert hasattr(settings, 'OLLAMA_BASE_URL')
    assert hasattr(settings, 'OLLAMA_MODEL')
    assert 'localhost' in settings.OLLAMA_BASE_URL or settings.OLLAMA_BASE_URL.startswith('http')

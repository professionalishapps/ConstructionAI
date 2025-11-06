"""
Test that all modules can be imported correctly
"""
import pytest


def test_api_router_import():
    """Test that API router can be imported"""
    from src.api.v1.router import api_router
    assert api_router is not None


def test_config_import():
    """Test that config can be imported"""
    from src.core.config import settings
    assert settings is not None
    assert settings.PROJECT_NAME == 'Construction AI Risk Monitor'
    assert settings.API_V1_PREFIX == '/api/v1'


def test_database_models_import():
    """Test that database models can be imported"""
    from src.database.models import Project, DailyMetrics, AgentResult
    assert Project is not None
    assert DailyMetrics is not None
    assert AgentResult is not None


def test_database_base_import():
    """Test that database base can be imported"""
    from src.database.base import Base
    assert Base is not None


def test_dependencies_import():
    """Test that API dependencies can be imported"""
    from src.api.dependencies import get_db_connection
    assert get_db_connection is not None


def test_services_import():
    """Test that services can be imported"""
    from src.services.llm_service import OllamaClient
    assert OllamaClient is not None


@pytest.mark.parametrize("agent_module", [
    "src.agents.analysis.schedule_variance",
    "src.agents.analysis.cost_variance",
    "src.agents.analysis.subcontractor_score",
    "src.agents.predictive.weather_impact",
])
def test_agent_imports(agent_module):
    """Test that agents can be imported"""
    import importlib
    module = importlib.import_module(agent_module)
    assert module is not None

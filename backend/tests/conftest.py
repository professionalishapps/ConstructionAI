"""
Pytest configuration and fixtures
"""
import sys
from pathlib import Path

# Add src to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

import pytest


@pytest.fixture
def sample_project_data():
    """Sample project data for testing"""
    return {
        'project_id': 'PRJ-TEST-001',
        'name': 'Test Construction Project',
        'type': 'Commercial',
        'contract_value': 5000000,
        'start_date': '2025-01-01',
        'planned_completion': '2025-12-31',
        'current_completion_pct': 25.5
    }


@pytest.fixture
def sample_metrics_data():
    """Sample metrics data for testing"""
    return {
        'spi': 0.95,
        'cpi': 1.02,
        'actual_pct_complete': 25.5,
        'cost_variance': -50000,
        'schedule_variance_days': -5,
        'weather_risk_score': 3
    }

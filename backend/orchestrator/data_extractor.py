"""Data Extractor for Agent Orchestrator

Extracts project data from database and prepares it in the format
expected by the master orchestrator.
"""
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from datetime import datetime, timedelta


def extract_project_data_for_agents(
    db: Session,
    project_id: str
) -> Dict[str, Any]:
    """Extract complete project data from database for agent analysis.
    
    Args:
        db: Database session
        project_id: Project identifier
        
    Returns:
        Dict in format expected by AgentOrchestrator.run_all_agents()
    """
    # This is a template - adjust based on your actual database models
    
    # TODO: Import your actual database models
    # from backend.database.models import Project, Subcontractor, Material, etc.
    
    # For now, returning structure with placeholder data
    # Replace with actual database queries
    
    project_data = {
        'project': _extract_project_info(db, project_id),
        'schedule': _extract_schedule_data(db, project_id),
        'budget': _extract_budget_data(db, project_id),
        'subcontractor': _extract_subcontractor_data(db, project_id),
        'supply_chain': _extract_supply_chain_data(db, project_id),
        'change_orders': _extract_change_orders(db, project_id),
        'productivity': _extract_productivity_data(db, project_id),
        'quality': _extract_quality_data(db, project_id),
        'progress': _extract_progress_data(db, project_id),
        'cash_flow': _extract_cash_flow_data(db, project_id)
    }
    
    return project_data


def _extract_project_info(db: Session, project_id: str) -> Dict[str, Any]:
    """Extract basic project information."""
    # TODO: Replace with actual database query
    # project = db.query(Project).filter(Project.id == project_id).first()
    
    # Placeholder - replace with real data
    return {
        'id': project_id,
        'name': 'Sample Project',
        'location': {
            'lat': 37.7749,   # San Francisco
            'lon': -122.4194
        }
    }


def _extract_schedule_data(db: Session, project_id: str) -> Dict[str, Any]:
    """Extract schedule and progress data."""
    # TODO: Query your Project or Schedule table
    # project = db.query(Project).filter(Project.id == project_id).first()
    
    return {
        'baseline_pct_complete': 45.0,    # From baseline schedule
        'actual_pct_complete': 42.5,       # From progress tracking
        'total_days': 350,                 # Total duration
        'start_date': '2025-01-15',
        'baseline_end_date': '2025-12-31'
    }


def _extract_budget_data(db: Session, project_id: str) -> Dict[str, Any]:
    """Extract budget and cost data."""
    # TODO: Query cost tracking tables
    # cost_data = db.query(CostTracking).filter(...).first()
    
    return {
        'total': 15000000,          # Contract value
        'spent_to_date': 6800000,   # Actual costs
        'committed': 2000000         # Committed but not spent
    }


def _extract_subcontractor_data(db: Session, project_id: str) -> Dict[str, Any]:
    """Extract subcontractor performance data."""
    # TODO: Query Subcontractor and SubcontractorActivity tables
    # subcontractors = db.query(Subcontractor).filter(
    #     Subcontractor.project_id == project_id
    # ).all()
    
    # For now, aggregate data across all subcontractors
    # In production, you might track per-subcontractor or aggregate
    
    return {
        'planned_days': 30,
        'actual_days': 34,
        'critical_path': True,
        'defects': 2,
        'rework_hours': 8.5,
        'inspections_passed': 4,
        'inspections_total': 5,
        'incidents': 0,
        'near_misses': 1,
        'safety_observations': 3
    }


def _extract_supply_chain_data(db: Session, project_id: str) -> Dict[str, Any]:
    """Extract materials and supplier data."""
    # TODO: Query Material and Supplier tables
    # materials = db.query(Material).filter(
    #     Material.project_id == project_id
    # ).all()
    
    return {
        'materials': [
            {
                'name': 'Rebar Steel',
                'lead_time_days': 21,
                'stock_level': 15,       # Percentage
                'critical': True
            },
            {
                'name': 'Concrete',
                'lead_time_days': 3,
                'stock_level': 80,
                'critical': True
            }
        ],
        'supplier_performance': {
            'on_time_deliveries': 18,
            'total_deliveries': 20,
            'lead_time_extensions': 2
        }
    }


def _extract_change_orders(db: Session, project_id: str) -> List[Dict[str, Any]]:
    """Extract change order history."""
    # TODO: Query ChangeOrder table
    # change_orders = db.query(ChangeOrder).filter(
    #     ChangeOrder.project_id == project_id
    # ).all()
    
    return [
        {
            'category': 'Design Change',
            'amount': 50000,
            'initiated_by': 'Owner',
            'date': '2025-02-15',
            'status': 'Approved'
        },
        {
            'category': 'Owner Request',
            'amount': 75000,
            'initiated_by': 'Owner',
            'date': '2025-05-20',
            'status': 'Approved'
        }
    ]


def _extract_productivity_data(db: Session, project_id: str) -> Dict[str, Any]:
    """Extract productivity metrics and history."""
    # TODO: Query ProductivityTracking or DailyReports table
    # recent_data = db.query(ProductivityTracking).filter(
    #     ProductivityTracking.project_id == project_id
    # ).order_by(ProductivityTracking.date.desc()).limit(7).all()
    
    return {
        'units_completed': 450,
        'labor_hours': 180,
        'unit_type': 'sq ft',
        'benchmark_rate': 3.0,
        'historical_rates': [
            {'date': '2025-01-01', 'rate': 3.2},
            {'date': '2025-01-08', 'rate': 3.0},
            {'date': '2025-01-15', 'rate': 2.8},
            {'date': '2025-01-22', 'rate': 2.7},
            {'date': '2025-01-29', 'rate': 2.5}
        ]
    }


def _extract_quality_data(db: Session, project_id: str) -> Dict[str, Any]:
    """Extract quality and defect data."""
    # TODO: Query QualityInspection and Defect tables
    # defects = db.query(Defect).filter(
    #     Defect.project_id == project_id,
    #     Defect.status == 'Open'
    # ).all()
    
    return {
        'open_defects': 4,
        'recent_failures': 2,
        'inspection_pass_rate': 80,      # Percentage
        'historical_rework_rate': 15,     # Percentage
        'defect_density': 0.5,            # Defects per 1000 sq ft
        'defects': [
            {
                'severity': 'Major',
                'category': 'Concrete',
                'cost_estimate': 5000,
                'date_reported': '2025-10-15'
            },
            {
                'severity': 'Minor',
                'category': 'Finish',
                'cost_estimate': 800,
                'date_reported': '2025-10-20'
            }
        ]
    }


def _extract_progress_data(db: Session, project_id: str) -> Dict[str, Any]:
    """Extract progress photos and verification data."""
    # TODO: Query ProgressPhoto table
    # photo_count = db.query(ProgressPhoto).filter(
    #     ProgressPhoto.project_id == project_id
    # ).count()
    
    return {
        'photo_count': 8,
        'activity_type': 'framing',  # Current primary activity
        'last_photo_date': '2025-11-01'
    }


def _extract_cash_flow_data(db: Session, project_id: str) -> Dict[str, Any]:
    """Extract cash flow and payment data."""
    # TODO: Query CashFlow and Invoice tables
    # recent_costs = db.query(DailyCost).filter(
    #     DailyCost.project_id == project_id
    # ).order_by(DailyCost.date.desc()).limit(30).all()
    
    return {
        'current_balance': 500000,
        'recent_daily_costs': [45000, 50000, 40000, 48000, 52000],
        'expected_payments': [
            {'date': '2025-11-15', 'amount': 300000},
            {'date': '2025-12-01', 'amount': 250000}
        ],
        'projection_days': 90
    }


def validate_project_data(project_data: Dict[str, Any]) -> List[str]:
    """Validate that project data has all required fields.
    
    Args:
        project_data: Project data dictionary
        
    Returns:
        List of validation errors (empty if valid)
    """
    errors = []
    
    # Check required top-level keys
    required_keys = [
        'project', 'schedule', 'budget', 'subcontractor',
        'supply_chain', 'change_orders', 'productivity',
        'quality', 'progress', 'cash_flow'
    ]
    
    for key in required_keys:
        if key not in project_data:
            errors.append(f"Missing required key: {key}")
    
    # Validate schedule data
    if 'schedule' in project_data:
        schedule = project_data['schedule']
        if schedule.get('actual_pct_complete', 0) < 0 or schedule.get('actual_pct_complete', 0) > 100:
            errors.append("schedule.actual_pct_complete must be between 0 and 100")
        if schedule.get('baseline_pct_complete', 0) < 0 or schedule.get('baseline_pct_complete', 0) > 100:
            errors.append("schedule.baseline_pct_complete must be between 0 and 100")
        if schedule.get('total_days', 0) <= 0:
            errors.append("schedule.total_days must be positive")
    
    # Validate budget data
    if 'budget' in project_data:
        budget = project_data['budget']
        if budget.get('total', 0) <= 0:
            errors.append("budget.total must be positive")
        if budget.get('spent_to_date', 0) < 0:
            errors.append("budget.spent_to_date cannot be negative")
    
    # Validate location for weather API
    if 'project' in project_data:
        location = project_data['project'].get('location', {})
        lat = location.get('lat')
        lon = location.get('lon')
        if lat is None or lon is None:
            errors.append("project.location.lat and .lon are required for weather agent")
        elif not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
            errors.append("Invalid lat/lon coordinates")
    
    return errors


# Example usage
if __name__ == "__main__":
    print("Data Extractor Module")
    print("=" * 60)
    print("\nThis module provides functions to extract project data from")
    print("the database in the format expected by the agent orchestrator.")
    print("\nTo use:")
    print("  1. Update the _extract_* functions with your actual DB queries")
    print("  2. Import your database models at the top")
    print("  3. Call extract_project_data_for_agents(db, project_id)")
    print("\nExample:")
    print("""
    from backend.orchestrator.data_extractor import extract_project_data_for_agents
    from backend.orchestrator.master_orchestrator import AgentOrchestrator
    
    # In your API endpoint or scheduler
    project_data = extract_project_data_for_agents(db, "PRJ-123")
    
    # Validate data
    errors = validate_project_data(project_data)
    if errors:
        print("Validation errors:", errors)
        return
    
    # Run agents with real data
    orchestrator = AgentOrchestrator()
    results = await orchestrator.run_all_agents(project_data)
    """)


"""Comprehensive Synthetic Data Generator for Construction AI Demo

Generates realistic construction project data including:
- Projects (Green, Yellow, Red scenarios)
- Daily metrics (150+ days)
- Cost transactions (1000+ items)
- Subcontractors (12 subs with performance data)
- Change orders (20-30)
- Quality inspections (300+)
- Material deliveries (150+)
- Cash flow data
- Productivity metrics
"""
from datetime import date, datetime, timedelta
from decimal import Decimal
import random
import json
from typing import Dict, List

# Ensure we can import database models
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import (
    Project, DailyMetrics, Subcontractor, ChangeOrder, 
    Inspection, AgentResult
)


def generate_demo_projects(session) -> Dict[str, str]:
    """Generate three demo projects: Green, Yellow, and Red.
    
    Returns:
        Dict mapping scenario name to project_id
    """
    projects = {}
    
    # GREEN PROJECT - On track
    green_proj = Project(
        project_id="PRJ-2025-GREEN",
        name="Green Hills Medical Center",
        type="Healthcare Construction",
        location_lat=Decimal('37.3861'),
        location_lon=Decimal('-122.0839'),  # Palo Alto
        contract_value=Decimal('18000000.00'),
        start_date=date(2025, 2, 1),
        planned_completion=date(2025, 12, 15),
        current_completion_pct=Decimal('48.5')
    )
    session.add(green_proj)
    projects['green'] = "PRJ-2025-GREEN"
    
    # YELLOW PROJECT - Moderate issues
    yellow_proj = Project(
        project_id="PRJ-2025-YELLOW",
        name="Downtown Office Complex",
        type="Commercial Construction",
        location_lat=Decimal('37.7749'),
        location_lon=Decimal('-122.4194'),  # San Francisco
        contract_value=Decimal('15000000.00'),
        start_date=date(2025, 1, 15),
        planned_completion=date(2025, 12, 31),
        current_completion_pct=Decimal('42.5')
    )
    session.add(yellow_proj)
    projects['yellow'] = "PRJ-2025-YELLOW"
    
    # RED PROJECT - Major overrun (for demo)
    red_proj = Project(
        project_id="PRJ-2025-RED",
        name="Sunset Residential Complex",
        type="Residential Construction",
        location_lat=Decimal('37.7619'),
        location_lon=Decimal('-122.4850'),  # SF Sunset District
        contract_value=Decimal('12000000.00'),
        start_date=date(2024, 11, 1),
        planned_completion=date(2025, 10, 31),
        current_completion_pct=Decimal('35.0')
    )
    session.add(red_proj)
    projects['red'] = "PRJ-2025-RED"
    
    session.commit()
    print(f"Created {len(projects)} demo projects")
    
    return projects


def generate_daily_metrics(session, project_id: str, scenario: str, days: int = 150):
    """Generate realistic daily metrics for a project.
    
    Args:
        session: Database session
        project_id: Project identifier
        scenario: 'green', 'yellow', or 'red'
        days: Number of days of history to generate
    """
    today = date.today()
    
    # Scenario-specific parameters
    if scenario == 'green':
        base_spi = 1.05
        spi_volatility = 0.03
        base_cpi = 1.02
        cpi_volatility = 0.02
        schedule_var_range = (-3, 5)
        weather_risk_range = (10, 40)
    elif scenario == 'yellow':
        base_spi = 0.944
        spi_volatility = 0.05
        base_cpi = 0.936
        cpi_volatility = 0.04
        schedule_var_range = (-15, -5)
        weather_risk_range = (30, 60)
    else:  # red
        base_spi = 0.82
        spi_volatility = 0.08
        base_cpi = 0.80
        cpi_volatility = 0.06
        schedule_var_range = (-35, -20)
        weather_risk_range = (50, 80)
    
    for i in range(days):
        metric_date = today - timedelta(days=days - i)
        
        # Progress increases over time
        baseline_pct = min(100, 5 + (i / days) * 95)
        
        # Add noise and trend
        spi = base_spi + random.uniform(-spi_volatility, spi_volatility)
        actual_pct = baseline_pct * spi
        
        cpi = base_cpi + random.uniform(-cpi_volatility, cpi_volatility)
        
        # Cost variance worsens over time for red project
        if scenario == 'red':
            cost_var = -50000 - (i * 300)
        elif scenario == 'yellow':
            cost_var = -5000 - (i * 50)
        else:
            cost_var = random.randint(-2000, 3000)
        
        schedule_var = random.randint(*schedule_var_range)
        weather_risk = random.randint(*weather_risk_range)
        
        dm = DailyMetrics(
            project_id=project_id,
            date=metric_date,
            spi=Decimal(str(round(spi, 3))),
            cpi=Decimal(str(round(cpi, 3))),
            actual_pct_complete=Decimal(str(round(actual_pct, 2))),
            cost_variance=Decimal(str(cost_var)),
            schedule_variance_days=schedule_var,
            weather_risk_score=weather_risk
        )
        session.add(dm)
    
    session.commit()
    print(f"Generated {days} daily metrics for {project_id}")


def generate_subcontractors(session, project_id: str, scenario: str):
    """Generate subcontractor data.
    
    Args:
        session: Database session
        project_id: Project identifier
        scenario: Project scenario
    """
    subcontractor_types = [
        ("ABC Concrete Works", "Concrete"),
        ("Elite Steel Fabricators", "Structural Steel"),
        ("Premier Electrical", "Electrical"),
        ("ProPlumb Systems", "Plumbing"),
        ("Perfect HVAC", "HVAC"),
        ("TopFrame Carpentry", "Carpentry"),
        ("Skyline Roofing", "Roofing"),
        ("Precision Drywall", "Drywall"),
        ("Master Painters", "Painting"),
        ("GreenScape", "Landscaping"),
        ("SafeGuard Fire Protection", "Fire Protection"),
        ("TechSite Excavation", "Site Work")
    ]
    
    for name, trade in subcontractor_types:
        if scenario == 'red':
            perf_score = random.randint(55, 85)
            on_time_pct = random.uniform(65, 85)
            quality_score = random.randint(60, 80)
            safety_incidents = random.randint(1, 3)
        elif scenario == 'yellow':
            perf_score = random.randint(70, 90)
            on_time_pct = random.uniform(75, 92)
            quality_score = random.randint(75, 90)
            safety_incidents = random.randint(0, 2)
        else:  # green
            perf_score = random.randint(85, 98)
            on_time_pct = random.uniform(88, 99)
            quality_score = random.randint(88, 98)
            safety_incidents = 0 if random.random() > 0.3 else 1
        
        sub = Subcontractor(
            project_id=project_id,
            name=name,
            trade=trade,
            performance_score=perf_score,
            on_time_pct=Decimal(str(round(on_time_pct, 2))),
            quality_score=quality_score,
            safety_incidents=safety_incidents
        )
        session.add(sub)
    
    session.commit()
    print(f"Generated {len(subcontractor_types)} subcontractors for {project_id}")


def generate_change_orders(session, project_id: str, scenario: str):
    """Generate change order data.
    
    Args:
        session: Database session
        project_id: Project identifier
        scenario: Project scenario
    """
    categories = [
        "Design Change", "Site Conditions", "Owner Request", 
        "Code Compliance", "Material Substitution", "Weather Impact"
    ]
    
    reasons = {
        "Design Change": ["Design coordination issue", "MEP conflict", "Structural revision required"],
        "Site Conditions": ["Unforeseen underground utilities", "Soil conditions differ", "Rock excavation needed"],
        "Owner Request": ["Additional features requested", "Scope expansion", "Finish upgrade"],
        "Code Compliance": ["Building code update", "ADA requirements", "Fire code change"],
        "Material Substitution": ["Original material unavailable", "Supply chain issue", "Cost reduction"],
        "Weather Impact": ["Weather damage repair", "Additional drainage needed", "Storm protection"]
    }
    
    initiators = ["Owner", "Architect", "Contractor", "Engineer"]
    
    # More change orders for worse scenarios
    if scenario == 'red':
        co_count = random.randint(28, 35)
    elif scenario == 'yellow':
        co_count = random.randint(18, 25)
    else:
        co_count = random.randint(8, 15)
    
    start_date = datetime.now() - timedelta(days=150)
    
    for i in range(co_count):
        category = random.choice(categories)
        reason = random.choice(reasons[category])
        initiator = random.choice(initiators)
        
        # Amount varies by scenario
        if scenario == 'red':
            amount = random.uniform(15000, 85000)
        elif scenario == 'yellow':
            amount = random.uniform(8000, 45000)
        else:
            amount = random.uniform(2000, 25000)
        
        co_date = start_date + timedelta(days=random.randint(0, 150))
        
        co = ChangeOrder(
            project_id=project_id,
            co_number=f"CO-{i+1:03d}",
            date=co_date.date(),
            amount=Decimal(str(round(amount, 2))),
            category=category,
            reason=reason,
            status="Approved" if random.random() > 0.2 else "Pending"
        )
        session.add(co)
    
    session.commit()
    print(f"Generated {co_count} change orders for {project_id}")


def generate_inspections(session, project_id: str, scenario: str, count: int = 100):
    """Generate quality inspection data.
    
    Args:
        session: Database session
        project_id: Project identifier
        scenario: Project scenario
        count: Number of inspections
    """
    areas = [
        "Foundation", "Structural Frame", "Exterior Walls", "Roofing",
        "MEP Rough-in", "Drywall", "Interior Finishes", "Exterior Finishes",
        "Site Work", "Parking", "Landscaping", "Fire Protection"
    ]
    
    inspectors = ["John Smith", "Maria Garcia", "David Chen", "Sarah Johnson", "Mike Brown"]
    severities = ["Minor", "Moderate", "Major"]
    
    start_date = datetime.now() - timedelta(days=120)
    
    for i in range(count):
        area = random.choice(areas)
        inspector = random.choice(inspectors)
        inspect_date = start_date + timedelta(days=random.randint(0, 120))
        
        # Scenario affects defect rates
        if scenario == 'red':
            defects = random.randint(2, 8)
            severity = random.choices(severities, weights=[0.3, 0.4, 0.3])[0]
        elif scenario == 'yellow':
            defects = random.randint(0, 4)
            severity = random.choices(severities, weights=[0.5, 0.4, 0.1])[0]
        else:
            defects = random.randint(0, 2)
            severity = random.choices(severities, weights=[0.7, 0.2, 0.1])[0]
        
        notes = f"Inspected {area}. " + (
            f"Found {defects} defects requiring correction." if defects > 0 
            else "No significant issues found."
        )
        
        inspection = Inspection(
            project_id=project_id,
            date=inspect_date.date(),
            area=area,
            inspector=inspector,
            defects_found=defects,
            severity=severity if defects > 0 else "None",
            notes=notes
        )
        session.add(inspection)
    
    session.commit()
    print(f"Generated {count} inspections for {project_id}")


def generate_agent_results_sample(session, project_id: str, scenario: str):
    """Generate sample agent results for the project.
    
    Args:
        session: Database session
        project_id: Project identifier
        scenario: Project scenario
    """
    from datetime import datetime
    
    # Risk scores by scenario
    if scenario == 'green':
        risk_scores = {
            'schedule_variance': 15, 'cost_variance': 18, 'subcontractor': 20,
            'weather': 25, 'supply_chain': 22, 'change_orders': 18,
            'productivity': 20, 'quality': 15, 'cash_flow': 25,
            'delay_cause': 20, 'completion_forecast': 22, 'cost_forecast': 20
        }
    elif scenario == 'yellow':
        risk_scores = {
            'schedule_variance': 52, 'cost_variance': 58, 'subcontractor': 45,
            'weather': 52, 'supply_chain': 38, 'change_orders': 42,
            'productivity': 55, 'quality': 35, 'cash_flow': 40,
            'delay_cause': 48, 'completion_forecast': 52, 'cost_forecast': 58
        }
    else:  # red
        risk_scores = {
            'schedule_variance': 78, 'cost_variance': 82, 'subcontractor': 68,
            'weather': 65, 'supply_chain': 70, 'change_orders': 75,
            'productivity': 72, 'quality': 65, 'cash_flow': 78,
            'delay_cause': 75, 'completion_forecast': 80, 'cost_forecast': 85
        }
    
    session_id = f"sess-demo-{scenario}-001"
    
    for agent_name, risk_score in risk_scores.items():
        result = AgentResult(
            project_id=project_id,
            session_id=session_id,
            agent_name=agent_name,
            status="completed",
            output=json.dumps({
                'risk_score': risk_score,
                'status': 'LOW' if risk_score < 30 else 'MEDIUM' if risk_score < 60 else 'HIGH',
                'timestamp': datetime.now().isoformat()
            }),
            execution_time_ms=random.randint(150, 500),
            completed_at=datetime.now()
        )
        session.add(result)
    
    session.commit()
    print(f"Generated sample agent results for {project_id}")


def generate_all_demo_data(session):
    """Generate comprehensive demo data for all scenarios.
    
    Args:
        session: Database session
    """
    print("\n" + "="*60)
    print("GENERATING COMPREHENSIVE DEMO DATA")
    print("="*60 + "\n")
    
    # Generate projects
    projects = generate_demo_projects(session)
    
    # Generate data for each project
    for scenario, project_id in projects.items():
        print(f"\n--- Generating data for {scenario.upper()} project ({project_id}) ---")
        
        days = 150 if scenario == 'red' else 120 if scenario == 'yellow' else 100
        generate_daily_metrics(session, project_id, scenario, days)
        generate_subcontractors(session, project_id, scenario)
        generate_change_orders(session, project_id, scenario)
        
        inspection_count = 120 if scenario == 'red' else 80 if scenario == 'yellow' else 60
        generate_inspections(session, project_id, scenario, inspection_count)
        
        generate_agent_results_sample(session, project_id, scenario)
    
    print("\n" + "="*60)
    print("DEMO DATA GENERATION COMPLETE")
    print("="*60)
    print(f"\nGenerated data for {len(projects)} projects:")
    print(f"  - GREEN: {projects['green']} (on track)")
    print(f"  - YELLOW: {projects['yellow']} (moderate issues)")
    print(f"  - RED: {projects['red']} (25% overrun - demo ready)")
    print("\nReady for demo! Load RED project to show crisis scenario.")
    print("="*60 + "\n")


if __name__ == "__main__":
    from database.db_setup import init_db
    
    print("Initializing database connection...")
    engine, SessionLocal = init_db()
    session = SessionLocal()
    
    try:
        generate_all_demo_data(session)
    except Exception as e:
        print(f"\nError: {e}")
        session.rollback()
        raise
    finally:
        session.close()
        print("Database session closed.")


"""Synthetic data generator for demo project.
This script creates a sample project and populates daily_metrics with a short time series.
"""
from datetime import date, timedelta
from decimal import Decimal
import random

from database.db_setup import init_db
from database.models import Project, DailyMetrics


def generate_sample_project(session):
    project_id = "PRJ-2025-001"
    existing = session.query(Project).filter_by(project_id=project_id).first()
    if existing:
        print("Sample project already exists")
        return existing.project_id

    proj = Project(
        project_id=project_id,
        name="Downtown Office Complex",
        type="Commercial Construction",
        location_lat=Decimal('37.7749'),
        location_lon=Decimal('-122.4194'),
        contract_value=Decimal('15000000.00'),
        start_date=date(2025,1,15),
        planned_completion=date(2025,12,31),
        current_completion_pct=Decimal('42.5')
    )
    session.add(proj)
    session.commit()
    print("Inserted sample project", project_id)
    return project_id


def generate_daily_metrics(session, project_id, days=30):
    today = date.today()
    # Generate historical metrics for `days` days prior to today
    for i in range(days):
        d = today - timedelta(days=days - i)
        baseline_pct = 40.0 + i * 0.2  # simple rising baseline
        actual_pct = baseline_pct - random.uniform(0.0, 2.0)  # slight lag
        spi = round((actual_pct / baseline_pct) if baseline_pct > 0 else 1.0, 3)
        cpi = round(1.0 - random.uniform(-0.05, 0.1), 3)
        dm = DailyMetrics(
            project_id=project_id,
            date=d,
            spi=Decimal(str(spi)),
            cpi=Decimal(str(cpi)),
            actual_pct_complete=Decimal(str(round(actual_pct,2))),
            cost_variance=Decimal(str(random.randint(-5000,5000))),
            schedule_variance_days=random.randint(-5,5),
            weather_risk_score=random.randint(0,50)
        )
        session.add(dm)
    session.commit()
    print(f"Inserted {days} daily metric rows for {project_id}")


if __name__ == "__main__":
    print("Initializing DB connection...")
    engine, SessionLocal = init_db()
    session = SessionLocal()
    try:
        pid = generate_sample_project(session)
        generate_daily_metrics(session, pid, days=60)
    finally:
        session.close()
        print("Data generation complete")

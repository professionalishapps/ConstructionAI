"""Agent Scheduler

Runs agents on a schedule and persists results.
"""
import asyncio
import logging
import os
import signal
import sys
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ..database.models import Project, DailyMetrics
from .agent_runner import run_all_agents

# Database connection from environment
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = int(os.getenv('DB_PORT', 5432))
DB_NAME = os.getenv('DB_NAME', 'construction_db')
DB_USER = os.getenv('DB_USER', 'admin')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'admin123')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AgentScheduler:
    def __init__(self):
        """Initialize the scheduler."""
        self.running = False
        self.engine = create_engine(
            f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        )
        self.Session = sessionmaker(bind=self.engine)
        
    async def get_active_projects(self) -> List[Dict]:
        """Get list of active projects to analyze."""
        db = self.Session()
        try:
            projects = db.query(Project).all()
            return [{
                'project_id': p.project_id,
                'name': p.name,
                'contract_value': float(p.contract_value) if p.contract_value else 0,
                'current_completion_pct': float(p.current_completion_pct) if p.current_completion_pct else 0
            } for p in projects]
        finally:
            db.close()
            
    async def get_project_metrics(self, project_id: str) -> Optional[Dict]:
        """Get latest metrics for a project."""
        db = self.Session()
        try:
            metrics = db.query(DailyMetrics).filter(
                DailyMetrics.project_id == project_id
            ).order_by(
                DailyMetrics.date.desc()
            ).first()
            
            if not metrics:
                return None
                
            return {
                'date': metrics.date.isoformat(),
                'spi': float(metrics.spi) if metrics.spi else 1.0,
                'cpi': float(metrics.cpi) if metrics.cpi else 1.0,
                'actual_pct_complete': float(metrics.actual_pct_complete) if metrics.actual_pct_complete else 0,
                'cost_variance': float(metrics.cost_variance) if metrics.cost_variance else 0,
                'schedule_variance_days': metrics.schedule_variance_days or 0,
                'weather_risk_score': metrics.weather_risk_score or 0
            }
        finally:
            db.close()
            
    async def analyze_project(self, project: Dict):
        """Run analysis for a single project."""
        logger.info(f"Analyzing project {project['project_id']}")
        
        try:
            # Get latest metrics
            metrics = await self.get_project_metrics(project['project_id'])
            if not metrics:
                logger.warning(f"No metrics found for project {project['project_id']}")
                return
                
            # Prepare input data
            input_data = {
                # Cost variance inputs
                "budget": project['contract_value'],
                "cpi": metrics['cpi'],
                "pct_complete": project['current_completion_pct'],
                "cost_variance": metrics['cost_variance'],
                "spent_to_date": project['contract_value'] * (project['current_completion_pct']/100.0),
                
                # Weather impact inputs
                "weather_data": {
                    "risk_score": metrics['weather_risk_score']
                },
                "activity_type": "site_work",  # TODO: Get from schedule
                "duration_days": 30,
                
                # Subcontractor inputs
                "planned_days": 30,
                "actual_days": 30 + metrics['schedule_variance_days'],
                "critical_path": True,
                "defects": 0,
                "rework_hours": 0,
                "inspections_passed": 0,
                "inspections_total": 0,
                "incidents": 0,
                "near_misses": 0,
                "safety_observations": 0
            }
            
            # Run agents
            db = self.Session()
            try:
                results = await run_all_agents(
                    db=db,
                    project_id=project['project_id'],
                    input_data=input_data
                )
                logger.info(f"Analysis complete for {project['project_id']}")
                logger.debug(f"Results: {results}")
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error analyzing project {project['project_id']}: {e}")
            
    async def run_analysis(self):
        """Run analysis for all active projects."""
        try:
            # Get active projects
            projects = await self.get_active_projects()
            logger.info(f"Found {len(projects)} active projects")
            
            # Analyze each project
            tasks = [self.analyze_project(p) for p in projects]
            await asyncio.gather(*tasks)
            
        except Exception as e:
            logger.error(f"Error in analysis run: {e}")
            
    async def run(self, interval_seconds: int = 3600):
        """Run the scheduler loop."""
        self.running = True
        logger.info("Starting agent scheduler")
        
        def handle_signal(signum, frame):
            logger.info("Received shutdown signal")
            self.running = False
            
        signal.signal(signal.SIGINT, handle_signal)
        signal.signal(signal.SIGTERM, handle_signal)
        
        while self.running:
            await self.run_analysis()
            logger.info(f"Sleeping for {interval_seconds} seconds")
            await asyncio.sleep(interval_seconds)
            
        logger.info("Scheduler stopped")

if __name__ == "__main__":
    # Run scheduler with 1 hour interval
    scheduler = AgentScheduler()
    asyncio.run(scheduler.run(3600))
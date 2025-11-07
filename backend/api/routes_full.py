"""Full API Routes with 14-Agent Orchestrator Integration"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
import asyncio
from datetime import datetime, date

from database.db_setup import get_db
from database.models import Project, DailyMetrics, Subcontractor, ChangeOrder, Inspection
from orchestrator.master_orchestrator import run_full_analysis

router = APIRouter(prefix="/api/v1")


# ============================================================================
# PROJECT ENDPOINTS
# ============================================================================

@router.get("/projects")
async def list_projects(db: Session = Depends(get_db)):
    """List all projects."""
    projects = db.query(Project).all()
    return {
        "projects": [
            {
                "project_id": p.project_id,
                "name": p.name,
                "type": p.type,
                "contract_value": float(p.contract_value),
                "current_completion_pct": float(p.current_completion_pct),
                "start_date": p.start_date.isoformat(),
                "planned_completion": p.planned_completion.isoformat()
            }
            for p in projects
        ]
    }


@router.get("/projects/{project_id}")
async def get_project(project_id: str, db: Session = Depends(get_db)):
    """Get detailed project information."""
    project = db.query(Project).filter(Project.project_id == project_id).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Get latest metrics
    latest_metric = db.query(DailyMetrics)\
        .filter(DailyMetrics.project_id == project_id)\
        .order_by(DailyMetrics.date.desc())\
        .first()
    
    # Get subcontractors
    subcontractors = db.query(Subcontractor)\
        .filter(Subcontractor.project_id == project_id)\
        .all()
    
    # Get change orders
    change_orders = db.query(ChangeOrder)\
        .filter(ChangeOrder.project_id == project_id)\
        .all()
    
    return {
        "project": {
            "id": project.project_id,
            "name": project.name,
            "type": project.type,
            "location": {
                "lat": float(project.location_lat),
                "lon": float(project.location_lon)
            },
            "contract_value": float(project.contract_value),
            "start_date": project.start_date.isoformat(),
            "planned_completion": project.planned_completion.isoformat(),
            "current_completion_pct": float(project.current_completion_pct)
        },
        "latest_metric": {
            "spi": float(latest_metric.spi) if latest_metric else 1.0,
            "cpi": float(latest_metric.cpi) if latest_metric else 1.0,
            "actual_pct_complete": float(latest_metric.actual_pct_complete) if latest_metric else 0,
            "cost_variance": float(latest_metric.cost_variance) if latest_metric else 0,
            "schedule_variance_days": latest_metric.schedule_variance_days if latest_metric else 0,
            "weather_risk_score": latest_metric.weather_risk_score if latest_metric else 0,
            "date": latest_metric.date.isoformat() if latest_metric else None
        },
        "subcontractors": [
            {
                "name": s.name,
                "trade": s.trade,
                "performance_score": s.performance_score,
                "on_time_pct": float(s.on_time_pct),
                "quality_score": s.quality_score,
                "safety_incidents": s.safety_incidents
            }
            for s in subcontractors
        ],
        "change_orders_summary": {
            "count": len(change_orders),
            "total_value": sum(float(co.amount) for co in change_orders)
        }
    }


@router.get("/projects/current")
async def get_current_project(db: Session = Depends(get_db)):
    """Get the current/default project for demo."""
    # Try to get RED project first (for demo), fallback to any project
    project = db.query(Project).filter(Project.project_id == "PRJ-2025-RED").first()
    
    if not project:
        project = db.query(Project).first()
    
    if not project:
        return {
            "project": None,
            "message": "No projects found. Please generate demo data."
        }
    
    return await get_project(project.project_id, db)


# ============================================================================
# AGENT ANALYSIS ENDPOINTS
# ============================================================================

@router.post("/projects/{project_id}/analyze")
async def run_project_analysis(project_id: str, db: Session = Depends(get_db)):
    """Run complete 14-agent analysis on a project.
    
    This is the main endpoint that executes all agents and returns comprehensive results.
    """
    # Get project data
    project = db.query(Project).filter(Project.project_id == project_id).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Get latest metrics
    latest_metric = db.query(DailyMetrics)\
        .filter(DailyMetrics.project_id == project_id)\
        .order_by(DailyMetrics.date.desc())\
        .first()
    
    # Calculate days elapsed
    days_elapsed = (date.today() - project.start_date).days
    total_days = (project.planned_completion - project.start_date).days
    days_remaining = (project.planned_completion - date.today()).days
    
    # Calculate baseline completion
    baseline_pct = (days_elapsed / total_days * 100) if total_days > 0 else 0
    
    # Prepare data for orchestrator
    project_data = {
        "project": {
            "id": project.project_id,
            "name": project.name,
            "type": project.type,
            "location": {
                "lat": float(project.location_lat),
                "lon": float(project.location_lon)
            },
            "contract_value": float(project.contract_value),
            "start_date": project.start_date.isoformat(),
            "planned_completion": project.planned_completion.isoformat()
        },
        "schedule": {
            "baseline_pct_complete": baseline_pct,
            "actual_pct_complete": float(project.current_completion_pct),
            "total_days": total_days,
            "days_elapsed": days_elapsed,
            "days_remaining": days_remaining
        },
        "budget": {
            "total": float(project.contract_value),
            "spent_to_date": float(project.contract_value) * (float(project.current_completion_pct) / 100) * 1.1,  # Estimated
            "committed": float(project.contract_value) * 0.15,  # Estimated
            "contingency": float(project.contract_value) * 0.05
        },
        "latest_metrics": {
            "spi": float(latest_metric.spi) if latest_metric else 1.0,
            "cpi": float(latest_metric.cpi) if latest_metric else 1.0,
            "cost_variance": float(latest_metric.cost_variance) if latest_metric else 0,
            "schedule_variance_days": latest_metric.schedule_variance_days if latest_metric else 0
        }
    }
    
    # Run the full 14-agent analysis
    try:
        results = await run_full_analysis(project_data)
        
        return {
            "success": True,
            "project_id": project_id,
            "project_name": project.name,
            "analysis_results": results,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )


@router.get("/projects/{project_id}/status")
async def get_project_status(project_id: str, db: Session = Depends(get_db)):
    """Get quick project status (cached agent results)."""
    project = db.query(Project).filter(Project.project_id == project_id).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    latest_metric = db.query(DailyMetrics)\
        .filter(DailyMetrics.project_id == project_id)\
        .order_by(DailyMetrics.date.desc())\
        .first()
    
    # Calculate overall health
    spi = float(latest_metric.spi) if latest_metric else 1.0
    cpi = float(latest_metric.cpi) if latest_metric else 1.0
    
    avg_performance = (spi + cpi) / 2
    
    if avg_performance >= 0.95:
        health = "GREEN"
    elif avg_performance >= 0.85:
        health = "YELLOW"
    else:
        health = "RED"
    
    return {
        "project_id": project_id,
        "name": project.name,
        "overall_health": health,
        "spi": spi,
        "cpi": cpi,
        "completion_pct": float(project.current_completion_pct),
        "cost_variance": float(latest_metric.cost_variance) if latest_metric else 0,
        "schedule_variance_days": latest_metric.schedule_variance_days if latest_metric else 0
    }


# ============================================================================
# METRICS ENDPOINTS
# ============================================================================

@router.get("/projects/{project_id}/metrics")
async def get_project_metrics(
    project_id: str,
    days: int = 30,
    db: Session = Depends(get_db)
):
    """Get historical metrics for a project."""
    metrics = db.query(DailyMetrics)\
        .filter(DailyMetrics.project_id == project_id)\
        .order_by(DailyMetrics.date.desc())\
        .limit(days)\
        .all()
    
    return {
        "project_id": project_id,
        "metrics": [
            {
                "date": m.date.isoformat(),
                "spi": float(m.spi),
                "cpi": float(m.cpi),
                "actual_pct_complete": float(m.actual_pct_complete),
                "cost_variance": float(m.cost_variance),
                "schedule_variance_days": m.schedule_variance_days,
                "weather_risk_score": m.weather_risk_score
            }
            for m in reversed(metrics)  # Return in chronological order
        ]
    }


@router.get("/projects/{project_id}/change-orders")
async def get_change_orders(project_id: str, db: Session = Depends(get_db)):
    """Get change orders for a project."""
    change_orders = db.query(ChangeOrder)\
        .filter(ChangeOrder.project_id == project_id)\
        .order_by(ChangeOrder.date.desc())\
        .all()
    
    return {
        "project_id": project_id,
        "change_orders": [
            {
                "co_number": co.co_number,
                "date": co.date.isoformat(),
                "amount": float(co.amount),
                "category": co.category,
                "reason": co.reason,
                "status": co.status
            }
            for co in change_orders
        ],
        "summary": {
            "total_count": len(change_orders),
            "total_value": sum(float(co.amount) for co in change_orders),
            "pending_count": sum(1 for co in change_orders if co.status == "Pending")
        }
    }


@router.get("/projects/{project_id}/inspections")
async def get_inspections(
    project_id: str,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get quality inspections for a project."""
    inspections = db.query(Inspection)\
        .filter(Inspection.project_id == project_id)\
        .order_by(Inspection.date.desc())\
        .limit(limit)\
        .all()
    
    return {
        "project_id": project_id,
        "inspections": [
            {
                "date": i.date.isoformat(),
                "area": i.area,
                "inspector": i.inspector,
                "defects_found": i.defects_found,
                "severity": i.severity,
                "notes": i.notes
            }
            for i in inspections
        ],
        "summary": {
            "total_inspections": len(inspections),
            "total_defects": sum(i.defects_found for i in inspections),
            "avg_defects_per_inspection": sum(i.defects_found for i in inspections) / len(inspections) if inspections else 0
        }
    }


# ============================================================================
# HEALTH CHECK
# ============================================================================

@router.get("/health")
async def health_check():
    """API health check."""
    return {
        "status": "healthy",
        "service": "Construction AI - 14 Agent System",
        "timestamp": datetime.now().isoformat(),
        "agents_available": 14
    }


@router.get("/system-status")
async def system_status():
    """Get system status including agent availability."""
    
    # Check if Ollama is available
    ollama_available = False
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        ollama_available = response.status_code == 200
    except:
        pass
    
    return {
        "status": "operational",
        "agents": {
            "total": 14,
            "independent": 10,
            "dependent": 3,
            "orchestrator": 1
        },
        "integrations": {
            "ollama": {
                "available": ollama_available,
                "endpoint": "http://localhost:11434"
            },
            "open_meteo": {
                "available": True,
                "endpoint": "https://api.open-meteo.com"
            }
        },
        "database": {
            "connected": True
        },
        "timestamp": datetime.now().isoformat()
    }


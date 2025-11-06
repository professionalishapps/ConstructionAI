"""Agent Runner Module

Handles agent execution, data preparation, and result persistence.
"""
import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

from sqlalchemy.orm import Session
import traceback

from ..database.models import AgentResult
from ..agents import cost_variance, weather_impact, subcontractor_score

def generate_session_id() -> str:
    """Generate a unique session ID for agent runs."""
    return f"sess-{uuid.uuid4().hex[:12]}"

async def run_agent(
    db: Session,
    project_id: str,
    agent_name: str,
    input_data: Dict[str, Any]
) -> Dict[str, Any]:
    """Run an agent analysis and store results.
    
    Args:
        db: Database session
        project_id: Project identifier
        agent_name: Name of agent to run
        input_data: Parameters for agent analysis
        
    Returns:
        Dict containing agent result info
    """
    session_id = generate_session_id()
    
    # Create initial record
    agent_result = AgentResult(
        project_id=project_id,
        session_id=session_id,
        agent_name=agent_name,
        status="pending",
        input_data=input_data
    )
    db.add(agent_result)
    db.commit()
    
    try:
        # Update to running
        agent_result.status = "running"
        db.commit()
        
        # Execute appropriate agent
        if agent_name == "cost_variance":
            eac = cost_variance.calculate_eac(
                budget=input_data.get("budget", 0),
                cpi=input_data.get("cpi", 1.0),
                spent_to_date=input_data.get("spent_to_date", 0),
                pct_complete=input_data.get("pct_complete", 0)
            )
            pressure, observations = cost_variance.analyze_cost_pressure(
                spent_to_date=input_data.get("spent_to_date", 0),
                budget=input_data.get("budget", 0),
                pct_complete=input_data.get("pct_complete", 0),
                cost_variance=input_data.get("cost_variance", 0)
            )
            
            output = {
                "eac_analysis": eac,
                "pressure_level": pressure,
                "observations": observations
            }
            
        elif agent_name == "weather_impact":
            impact, descriptions = weather_impact.assess_weather_impact(
                weather_data=input_data.get("weather_data", {}),
                activity_type=input_data.get("activity_type", ""),
                duration_days=input_data.get("duration_days", 0)
            )
            suggestions = weather_impact.suggest_mitigations(
                impact_factor=impact,
                activity_type=input_data.get("activity_type", "")
            )
            
            output = {
                "impact_factor": impact,
                "impact_descriptions": descriptions,
                "suggested_mitigations": suggestions
            }
            
        elif agent_name == "subcontractor_score":
            schedule_score, schedule_msg = subcontractor_score.calculate_schedule_score(
                planned_days=input_data.get("planned_days", 0),
                actual_days=input_data.get("actual_days", 0),
                critical_path=input_data.get("critical_path", False)
            )
            
            quality_score, quality_obs = subcontractor_score.calculate_quality_score(
                defects=input_data.get("defects", 0),
                rework_hours=input_data.get("rework_hours", 0),
                inspections_passed=input_data.get("inspections_passed", 0),
                inspections_total=input_data.get("inspections_total", 0)
            )
            
            safety_score, safety_obs = subcontractor_score.calculate_safety_score(
                incidents=input_data.get("incidents", 0),
                near_misses=input_data.get("near_misses", 0),
                safety_observations=input_data.get("safety_observations", 0)
            )
            
            scores = {
                "schedule_adherence": schedule_score,
                "quality": quality_score,
                "safety": safety_score
            }
            
            risk_level, risk_factors = subcontractor_score.assess_risk_level(scores)
            suggestions = subcontractor_score.suggest_improvements(scores, risk_level)
            
            output = {
                "scores": scores,
                "schedule_message": schedule_msg,
                "quality_observations": quality_obs,
                "safety_observations": safety_obs,
                "risk_level": risk_level,
                "risk_factors": risk_factors,
                "suggested_improvements": suggestions
            }
            
        else:
            raise ValueError(f"Unknown agent: {agent_name}")
            
        # Update record with success
        agent_result.status = "completed"
        agent_result.output = json.dumps(output)
        agent_result.completed_at = datetime.utcnow()
        db.commit()
        
        return {
            "session_id": session_id,
            "status": "completed",
            "output": output
        }
        
    except Exception as e:
        # Update record with failure
        error_msg = f"{str(e)}\n{traceback.format_exc()}"
        agent_result.status = "failed"
        agent_result.error = error_msg
        agent_result.completed_at = datetime.utcnow()
        db.commit()
        
        return {
            "session_id": session_id,
            "status": "failed",
            "error": str(e)
        }

async def run_all_agents(
    db: Session,
    project_id: str,
    input_data: Dict[str, Any]
) -> Dict[str, Any]:
    """Run all agents for comprehensive analysis.
    
    Args:
        db: Database session
        project_id: Project identifier
        input_data: Combined input data for all agents
        
    Returns:
        Dict with all agent results
    """
    agents = ["cost_variance", "weather_impact", "subcontractor_score"]
    tasks = [
        run_agent(db, project_id, agent, input_data)
        for agent in agents
    ]
    
    results = await asyncio.gather(*tasks)
    return {
        agent: result
        for agent, result in zip(agents, results)
    }

def get_agent_history(
    db: Session,
    project_id: str,
    agent_name: Optional[str] = None,
    limit: int = 10
) -> list:
    """Get historical agent results.
    
    Args:
        db: Database session
        project_id: Project identifier
        agent_name: Optional filter by agent
        limit: Max number of results
        
    Returns:
        List of agent results, newest first
    """
    query = db.query(AgentResult).filter(
        AgentResult.project_id == project_id,
        AgentResult.status == "completed"
    )
    
    if agent_name:
        query = query.filter(AgentResult.agent_name == agent_name)
        
    results = query.order_by(AgentResult.created_at.desc()).limit(limit).all()
    
    return [{
        "session_id": r.session_id,
        "agent_name": r.agent_name,
        "created_at": r.created_at.isoformat(),
        "output": json.loads(r.output) if r.output else None
    } for r in results]
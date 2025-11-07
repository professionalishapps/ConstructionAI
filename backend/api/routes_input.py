from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime

router = APIRouter(prefix="/api/v1", tags=["input-analysis"])

# Import agents directly
from agents.schedule_variance import calculate_spi, days_ahead_behind
from agents.cost_variance import calculate_eac, analyze_cost_pressure
from agents.weather_impact import fetch_weather_forecast, analyze_weather_forecast

# Input model
class ProjectLocation(BaseModel):
    lat: float
    lon: float

class ProjectInfo(BaseModel):
    id: str
    name: str
    location: ProjectLocation
    contract_value: float

class ScheduleInfo(BaseModel):
    baseline_pct_complete: float
    actual_pct_complete: float
    total_days: int
    days_elapsed: int
    days_remaining: int

class BudgetInfo(BaseModel):
    total: float
    spent_to_date: float
    committed: float
    contingency: float

class AnalysisInput(BaseModel):
    project: ProjectInfo
    schedule: ScheduleInfo
    budget: BudgetInfo

@router.post("/analyze-input")
async def analyze_input(input_data: AnalysisInput):
    """
    Run analysis based on manual input data (no database required)
    """
    try:
        start_time = datetime.now()
        
        # Agent 1: Schedule Variance
        spi = calculate_spi(
            input_data.schedule.baseline_pct_complete,
            input_data.schedule.actual_pct_complete
        )
        days_delta = days_ahead_behind(
            input_data.schedule.baseline_pct_complete,
            input_data.schedule.actual_pct_complete,
            input_data.schedule.total_days
        )
        
        # Calculate schedule risk level
        if spi >= 1.0:
            schedule_risk = "LOW"
        elif spi >= 0.95:
            schedule_risk = "MEDIUM"
        else:
            schedule_risk = "HIGH"
        
        agent_1_result = {
            "spi": spi,
            "days_ahead_behind": days_delta,
            "risk_level": schedule_risk,
            "message": f"Schedule Performance Index: {spi:.3f}",
            "risk_score": max(0, min(100, int((1.0 - spi) * 100))) if spi < 1.0 else 0
        }
        
        # Agent 2: Cost Variance
        # Calculate CPI manually
        earned_value = input_data.budget.total * (input_data.schedule.actual_pct_complete / 100.0)
        cpi = earned_value / input_data.budget.spent_to_date if input_data.budget.spent_to_date > 0 else 1.0
        eac_result = calculate_eac(
            input_data.budget.total,
            cpi,
            input_data.budget.spent_to_date,
            input_data.schedule.actual_pct_complete
        )
        cost_risk, cost_flags = analyze_cost_pressure(
            input_data.budget.spent_to_date,
            input_data.budget.total,
            input_data.schedule.actual_pct_complete,
            input_data.budget.total - input_data.budget.spent_to_date
        )
        
        agent_2_result = {
            "cpi": cpi,
            "eac": eac_result,
            "risk_level": cost_risk,
            "flags": cost_flags,
            "risk_score": max(0, min(100, int((1.0 - cpi) * 100))) if cpi < 1.0 else 0
        }
        
        # Agent 4: Weather Impact
        weather_forecast = fetch_weather_forecast(
            latitude=input_data.project.location.lat,
            longitude=input_data.project.location.lon,
            forecast_days=14
        )
        
        weather_analysis = analyze_weather_forecast(
            weather_forecast=weather_forecast,
            activity_type="General Construction",
            activity_duration_days=14
        )
        
        agent_4_result = {
            **weather_analysis,
            "risk_score": weather_analysis.get("risk_score", 30)
        }
        
        # Agent 14: Risk Mitigation (Simplified)
        overall_health = "GREEN"
        avg_risk = (agent_1_result["risk_score"] + agent_2_result["risk_score"] + agent_4_result["risk_score"]) / 3
        
        if avg_risk > 60:
            overall_health = "RED"
        elif avg_risk > 30:
            overall_health = "YELLOW"
        
        # Generate recommendations
        recommendations = []
        rec_id = 1
        
        # Schedule recommendations
        if spi < 0.95:
            recommendations.append({
                "id": rec_id,
                "priority": "HIGH",
                "action": "Accelerate critical path activities to recover schedule delays",
                "expected_impact": f"Recover {abs(days_delta)} days of schedule slip. Current SPI: {spi:.3f}",
                "implementation_effort": "2-3 weeks",
                "icon": "⚡",
                "color": "error"
            })
            rec_id += 1
        
        # Cost recommendations
        if cpi < 0.95:
            recommendations.append({
                "id": rec_id,
                "priority": "HIGH",
                "action": "Implement value engineering to reduce cost overruns",
                "expected_impact": f"Reduce forecasted overrun. Current CPI: {cpi:.3f}, EAC: ${eac_result.get('eac_typical', 0):,.0f}",
                "implementation_effort": "1-2 weeks",
                "icon": "💰",
                "color": "warning"
            })
            rec_id += 1
        
        # Weather recommendations
        if agent_4_result.get("risk_score", 0) > 50:
            recommendations.append({
                "id": rec_id,
                "priority": "MEDIUM",
                "action": "Prepare weather contingency plans for outdoor activities",
                "expected_impact": f"Mitigate {agent_4_result.get('estimated_delay_days', 0)} days of weather delays",
                "implementation_effort": "1 week",
                "icon": "🌦️",
                "color": "warning"
            })
            rec_id += 1
        
        # General recommendations
        if overall_health != "GREEN":
            recommendations.append({
                "id": rec_id,
                "priority": "MEDIUM",
                "action": "Increase project monitoring frequency and stakeholder communication",
                "expected_impact": "Improve visibility and enable faster corrective actions",
                "implementation_effort": "Immediate",
                "icon": "📊",
                "color": "info"
            })
            rec_id += 1
        
        recommendations.append({
            "id": rec_id,
            "priority": "LOW",
            "action": "Conduct weekly risk review meetings with all stakeholders",
            "expected_impact": "Proactive risk identification and mitigation",
            "implementation_effort": "Ongoing",
            "icon": "👥",
            "color": "info"
        })
        
        agent_14_result = {
            "overall_health": overall_health,
            "recommendations": recommendations,
            "ollama_used": False,
            "reasoning": f"Automated analysis based on input metrics. Average risk score: {avg_risk:.1f}"
        }
        
        # Stub results for remaining agents
        stub_agents = {
            "agent_3_subcontractor": {"status": "no_data", "message": "Requires subcontractor database"},
            "agent_5_supply_chain": {"status": "no_data", "message": "Requires supply chain database"},
            "agent_6_change_orders": {"status": "no_data", "message": "Requires change order database"},
            "agent_7_productivity": {"status": "no_data", "message": "Requires productivity database"},
            "agent_8_quality": {"status": "no_data", "message": "Requires quality database"},
            "agent_9_progress": {"status": "no_data", "message": "Requires progress images"},
            "agent_10_cash_flow": {"status": "no_data", "message": "Requires cash flow database"},
            "agent_11_delay_cause": {"status": "no_data", "message": "Requires delay database"},
            "agent_12_completion": {"status": "no_data", "message": "Requires historical database"},
            "agent_13_cost_forecast": {"status": "no_data", "message": "Requires detailed cost database"},
        }
        
        # Combine all results
        analysis_results = {
            "agents": {
                "agent_1_schedule": agent_1_result,
                "agent_2_cost": agent_2_result,
                "agent_4_weather": agent_4_result,
                "agent_14_risk_mitigation": agent_14_result,
                **stub_agents
            },
            "total_duration_seconds": (datetime.now() - start_time).total_seconds()
        }
        
        return {
            "status": "success",
            "project": input_data.project.dict(),
            "analysis_results": analysis_results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


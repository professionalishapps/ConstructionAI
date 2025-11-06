"""Subcontractor Performance Scoring Agent

Evaluates subcontractor performance based on multiple factors and generates 
performance scores and risk assessments.
"""
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import math


class SubcontractorMetric:
    """Metric categories for subcontractor evaluation."""
    
    SCHEDULE_ADHERENCE = "schedule_adherence"
    QUALITY = "quality"
    SAFETY = "safety"
    DOCUMENTATION = "documentation"
    COOPERATION = "cooperation"
    RESOURCE_MANAGEMENT = "resource_management"
    

def calculate_schedule_score(planned_days: int,
                           actual_days: int,
                           critical_path: bool = False) -> Tuple[float, str]:
    """Calculate schedule performance score (0-100).
    
    Args:
        planned_days: Originally planned duration
        actual_days: Actual/projected duration
        critical_path: Whether activity is on critical path
    """
    if planned_days <= 0:
        return 0, "Invalid planned duration"
        
    variance = actual_days - planned_days
    variance_pct = (variance / planned_days) * 100
    
    # Base score starts at 100 and reduces based on variance
    base_score = 100 - abs(variance_pct) * (1.5 if critical_path else 1.0)
    
    # Floor at 0, ceiling at 100
    score = max(0, min(100, base_score))
    
    # Generate explanation
    if variance == 0:
        msg = "On schedule"
    elif variance > 0:
        msg = f"{variance} days behind schedule ({variance_pct:.1f}%)"
    else:
        msg = f"{abs(variance)} days ahead of schedule ({abs(variance_pct):.1f}%)"
        
    return score, msg


def calculate_quality_score(defects: int,
                          rework_hours: float,
                          inspections_passed: int,
                          inspections_total: int) -> Tuple[float, List[str]]:
    """Calculate quality performance score (0-100).
    
    Args:
        defects: Number of reported defects
        rework_hours: Hours spent on rework
        inspections_passed: Number of passed inspections
        inspections_total: Total number of inspections
    """
    observations = []
    
    # Calculate inspection pass rate
    if inspections_total > 0:
        pass_rate = (inspections_passed / inspections_total) * 100
        observations.append(f"Inspection pass rate: {pass_rate:.1f}%")
    else:
        pass_rate = 100
        observations.append("No inspections recorded")
        
    # Defect impact
    defect_score = 100 - (defects * 5)  # -5 points per defect
    defect_score = max(0, defect_score)
    if defects > 0:
        observations.append(f"{defects} defects reported")
        
    # Rework impact
    rework_score = 100 - (rework_hours * 2)  # -2 points per rework hour
    rework_score = max(0, rework_score)
    if rework_hours > 0:
        observations.append(f"{rework_hours:.1f} hours of rework required")
        
    # Weighted average of components
    # 50% inspection pass rate
    # 30% defect score
    # 20% rework score
    final_score = (pass_rate * 0.5) + (defect_score * 0.3) + (rework_score * 0.2)
    final_score = max(0, min(100, final_score))
    
    return final_score, observations


def calculate_safety_score(incidents: int,
                         near_misses: int,
                         safety_observations: int) -> Tuple[float, List[str]]:
    """Calculate safety performance score (0-100).
    
    Args:
        incidents: Number of safety incidents
        near_misses: Number of near misses
        safety_observations: Number of positive safety observations
    """
    observations = []
    
    # Incident impact (severe)
    incident_score = 100 - (incidents * 25)  # -25 points per incident
    
    # Near miss impact (moderate)
    near_miss_score = 100 - (near_misses * 10)  # -10 points per near miss
    
    # Positive observations (slight boost)
    observation_bonus = min(10, safety_observations * 2)  # +2 points per observation, max 10
    
    # Final score is weighted heavily toward incidents
    final_score = (incident_score * 0.6) + (near_miss_score * 0.3) + (observation_bonus * 0.1)
    final_score = max(0, min(100, final_score))
    
    # Generate observations
    if incidents > 0:
        observations.append(f"{incidents} safety incidents recorded")
    if near_misses > 0:
        observations.append(f"{near_misses} near misses reported")
    if safety_observations > 0:
        observations.append(f"{safety_observations} positive safety observations")
        
    return final_score, observations


def assess_risk_level(scores: Dict[str, float]) -> Tuple[str, List[str]]:
    """Assess overall risk level based on performance scores.
    
    Args:
        scores: Dict of metric categories to scores (0-100)
    
    Returns:
        Tuple of (risk_level, list of risk factors)
    """
    risk_factors = []
    
    # Critical metrics
    if scores.get(SubcontractorMetric.SAFETY, 100) < 85:
        risk_factors.append("Safety performance below threshold")
        
    if scores.get(SubcontractorMetric.QUALITY, 100) < 80:
        risk_factors.append("Quality concerns identified")
        
    if scores.get(SubcontractorMetric.SCHEDULE_ADHERENCE, 100) < 75:
        risk_factors.append("Schedule delays affecting project")
        
    # Secondary metrics
    if scores.get(SubcontractorMetric.RESOURCE_MANAGEMENT, 100) < 70:
        risk_factors.append("Resource management needs improvement")
        
    if scores.get(SubcontractorMetric.DOCUMENTATION, 100) < 70:
        risk_factors.append("Documentation compliance issues")
        
    # Determine overall risk level
    if len(risk_factors) >= 3 or any(s < 70 for s in scores.values()):
        risk_level = "HIGH"
    elif len(risk_factors) >= 1 or any(s < 85 for s in scores.values()):
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"
        
    return risk_level, risk_factors


def suggest_improvements(scores: Dict[str, float],
                       risk_level: str) -> List[str]:
    """Generate improvement suggestions based on scores.
    
    Args:
        scores: Dict of metric categories to scores (0-100)
        risk_level: Overall risk assessment level
    """
    suggestions = []
    
    # Safety improvements (highest priority)
    safety_score = scores.get(SubcontractorMetric.SAFETY, 100)
    if safety_score < 85:
        suggestions.extend([
            "Conduct additional safety training",
            "Increase safety monitoring frequency",
            "Review and update safety protocols"
        ])
        
    # Quality improvements
    quality_score = scores.get(SubcontractorMetric.QUALITY, 100)
    if quality_score < 80:
        suggestions.extend([
            "Implement additional quality control measures",
            "Review quality management procedures",
            "Increase inspection frequency"
        ])
        
    # Schedule improvements
    schedule_score = scores.get(SubcontractorMetric.SCHEDULE_ADHERENCE, 100)
    if schedule_score < 75:
        suggestions.extend([
            "Review resource allocation",
            "Analyze productivity factors",
            "Consider schedule recovery options"
        ])
        
    # General improvements based on risk level
    if risk_level == "HIGH":
        suggestions.extend([
            "Schedule immediate performance review meeting",
            "Develop detailed improvement action plan",
            "Increase oversight and monitoring"
        ])
    elif risk_level == "MEDIUM":
        suggestions.extend([
            "Schedule regular check-in meetings",
            "Document improvement requirements",
            "Monitor key metrics closely"
        ])
        
    return suggestions


if __name__ == "__main__":
    # Quick test
    schedule_score, schedule_msg = calculate_schedule_score(
        planned_days=30,
        actual_days=34,
        critical_path=True
    )
    
    quality_score, quality_obs = calculate_quality_score(
        defects=2,
        rework_hours=8.5,
        inspections_passed=4,
        inspections_total=5
    )
    
    safety_score, safety_obs = calculate_safety_score(
        incidents=0,
        near_misses=1,
        safety_observations=3
    )
    
    # Compile scores
    scores = {
        SubcontractorMetric.SCHEDULE_ADHERENCE: schedule_score,
        SubcontractorMetric.QUALITY: quality_score,
        SubcontractorMetric.SAFETY: safety_score
    }
    
    risk_level, risk_factors = assess_risk_level(scores)
    
    print("Subcontractor Performance Analysis")
    print(f"Schedule Score: {schedule_score:.1f} - {schedule_msg}")
    print("\nQuality Observations:")
    for obs in quality_obs:
        print(f"- {obs}")
    print("\nSafety Observations:")
    for obs in safety_obs:
        print(f"- {obs}")
        
    print(f"\nRisk Level: {risk_level}")
    print("Risk Factors:")
    for factor in risk_factors:
        print(f"- {factor}")
        
    suggestions = suggest_improvements(scores, risk_level)
    print("\nSuggested Improvements:")
    for sug in suggestions:
        print(f"- {sug}")
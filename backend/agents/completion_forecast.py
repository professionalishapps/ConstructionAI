"""Agent 12: Completion Date Forecaster

Predicts final completion date using current trajectory.
Depends on Agents 1, 7, 9 (Schedule, Productivity, Progress).
"""
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import math


def calculate_estimate_at_completion_time(
    current_pct_complete: float,
    spi: float,
    remaining_days_baseline: int,
    method: str = "spi"
) -> Tuple[int, str]:
    """Calculate Estimate at Completion (EAC) for project duration.
    
    Args:
        current_pct_complete: Current % complete (0-100)
        spi: Schedule Performance Index (1.0 = on schedule)
        remaining_days_baseline: Remaining days per baseline
        method: Calculation method ('spi', 'pace', 'composite')
    
    Returns:
        Tuple of (total_estimated_days, calculation_method_used)
    """
    if current_pct_complete <= 0:
        return remaining_days_baseline, "Insufficient progress data"
    
    remaining_work_pct = 100 - current_pct_complete
    
    if method == "spi" or method == "composite":
        # Use SPI to project remaining duration
        # If SPI < 1.0 (behind), will take longer
        # Remaining days = Baseline remaining / SPI
        if spi > 0:
            spi_based_remaining = remaining_days_baseline / spi
        else:
            spi_based_remaining = remaining_days_baseline * 1.5  # Assume 50% overrun
        
        if method == "spi":
            return int(spi_based_remaining), "SPI-based"
    
    if method == "pace":
        # Project based on actual pace
        # This would use actual days elapsed vs work completed
        # Simplified version here
        pace_based_remaining = remaining_days_baseline * (remaining_work_pct / (100 - current_pct_complete))
        return int(pace_based_remaining), "Pace-based"
    
    if method == "composite":
        # Weighted average of methods
        pace_based = remaining_days_baseline * (remaining_work_pct / current_pct_complete) if current_pct_complete > 0 else remaining_days_baseline
        composite = (spi_based_remaining * 0.6) + (pace_based * 0.4)
        return int(composite), "Composite"
    
    return remaining_days_baseline, "Baseline"


def forecast_completion_date(
    project_start_date: str,
    days_elapsed: int,
    estimated_remaining_days: int
) -> Dict[str, any]:
    """Forecast project completion date.
    
    Args:
        project_start_date: Project start date (ISO format)
        days_elapsed: Days elapsed since start
        estimated_remaining_days: Estimated remaining days
    
    Returns:
        Dict with completion date forecast
    """
    try:
        start_date = datetime.fromisoformat(project_start_date.replace('Z', '+00:00')).date()
    except:
        return {'error': 'Invalid start date'}
    
    total_estimated_days = days_elapsed + estimated_remaining_days
    forecast_date = start_date + timedelta(days=total_estimated_days)
    current_date = datetime.now().date()
    
    return {
        'forecast_completion_date': forecast_date.isoformat(),
        'days_from_today': (forecast_date - current_date).days,
        'total_estimated_duration': total_estimated_days,
        'days_elapsed': days_elapsed,
        'estimated_remaining': estimated_remaining_days
    }


def calculate_confidence_interval(
    estimated_remaining_days: int,
    spi: float,
    productivity_index: float,
    historical_variance: float = 0.15
) -> Dict[str, any]:
    """Calculate confidence interval for completion forecast.
    
    Args:
        estimated_remaining_days: Point estimate of remaining days
        spi: Schedule Performance Index
        productivity_index: Productivity vs benchmark
        historical_variance: Historical variance in schedule estimates (default 15%)
    
    Returns:
        Dict with confidence intervals
    """
    # Base variance on historical data
    base_variance = estimated_remaining_days * historical_variance
    
    # Adjust variance based on performance indicators
    # Poor performance = higher variance/uncertainty
    if spi < 0.9 or productivity_index < 0.9:
        variance_multiplier = 1.5
    elif spi < 0.95 or productivity_index < 0.95:
        variance_multiplier = 1.2
    else:
        variance_multiplier = 1.0
    
    adjusted_variance = base_variance * variance_multiplier
    
    # Calculate confidence intervals
    # Using normal distribution approximation
    # 90% CI ≈ ± 1.645 * standard deviation
    # 95% CI ≈ ± 1.96 * standard deviation
    
    ci_90_range = adjusted_variance * 1.645
    ci_95_range = adjusted_variance * 1.96
    
    return {
        'point_estimate': estimated_remaining_days,
        'confidence_90': {
            'low': max(0, int(estimated_remaining_days - ci_90_range)),
            'high': int(estimated_remaining_days + ci_90_range),
            'range_days': int(ci_90_range * 2)
        },
        'confidence_95': {
            'low': max(0, int(estimated_remaining_days - ci_95_range)),
            'high': int(estimated_remaining_days + ci_95_range),
            'range_days': int(ci_95_range * 2)
        },
        'uncertainty_level': 'High' if variance_multiplier > 1.2 else 'Moderate' if variance_multiplier > 1.0 else 'Low'
    }


def compare_to_baseline_completion(
    forecast_date: str,
    baseline_completion_date: str
) -> Dict[str, any]:
    """Compare forecast to baseline completion date.
    
    Args:
        forecast_date: Forecasted completion date (ISO format)
        baseline_completion_date: Baseline/planned completion date (ISO format)
    
    Returns:
        Dict with comparison
    """
    try:
        forecast = datetime.fromisoformat(forecast_date.replace('Z', '+00:00')).date()
        baseline = datetime.fromisoformat(baseline_completion_date.replace('Z', '+00:00')).date()
    except:
        return {'error': 'Invalid dates'}
    
    variance_days = (forecast - baseline).days
    
    if variance_days > 0:
        status = "Behind Schedule"
        impact = "HIGH" if variance_days > 30 else "MEDIUM" if variance_days > 14 else "LOW"
    elif variance_days < 0:
        status = "Ahead of Schedule"
        impact = "POSITIVE"
    else:
        status = "On Schedule"
        impact = "NONE"
    
    return {
        'baseline_date': baseline.isoformat(),
        'forecast_date': forecast.isoformat(),
        'variance_days': variance_days,
        'status': status,
        'impact': impact,
        'variance_weeks': round(variance_days / 7, 1)
    }


def integrate_productivity_and_progress_data(
    productivity_index: float,
    productivity_trend: str,
    progress_verification_status: str,
    spi: float
) -> Dict[str, any]:
    """Integrate data from Agents 7 and 9 to refine forecast.
    
    Args:
        productivity_index: From Agent 7
        productivity_trend: From Agent 7 (Declining/Stable/Improving)
        progress_verification_status: From Agent 9
        spi: From Agent 1
    
    Returns:
        Dict with integrated analysis and adjustments
    """
    adjustments = []
    adjustment_factor = 1.0
    
    # Productivity impact
    if productivity_trend == "Declining":
        adjustment_factor *= 1.1  # 10% longer
        adjustments.append("Declining productivity may extend schedule by ~10%")
    elif productivity_trend == "Improving":
        adjustment_factor *= 0.95  # 5% faster
        adjustments.append("Improving productivity may accelerate schedule by ~5%")
    
    if productivity_index < 0.85:
        adjustment_factor *= 1.05
        adjustments.append("Low productivity index adds schedule risk")
    
    # Progress verification impact
    if "over-reporting" in progress_verification_status.lower():
        adjustment_factor *= 1.08
        adjustments.append("Progress over-reporting detected - actual completion likely delayed")
    elif "under-reporting" in progress_verification_status.lower():
        adjustment_factor *= 0.97
        adjustments.append("Progress under-reporting - may complete earlier than reported")
    
    # SPI trend impact
    if spi < 0.9:
        adjustments.append("Significant schedule underperformance - high completion risk")
    elif spi > 1.05:
        adjustments.append("Schedule outperformance - early completion possible")
    
    confidence_level = "High" if adjustment_factor < 1.05 else "Medium" if adjustment_factor < 1.15 else "Low"
    
    return {
        'adjustment_factor': round(adjustment_factor, 3),
        'adjustments': adjustments,
        'confidence_level': confidence_level,
        'integrated_analysis': f"Combined factors suggest {adjustment_factor:.1%} schedule impact"
    }


def recommend_schedule_recovery_actions(
    variance_days: int,
    spi: float,
    productivity_index: float
) -> List[str]:
    """Recommend actions to recover schedule.
    
    Args:
        variance_days: Days behind schedule (negative if ahead)
        spi: Schedule Performance Index
        productivity_index: Productivity vs benchmark
    
    Returns:
        List of recommendations
    """
    recommendations = []
    
    if variance_days <= 0:
        recommendations.append("✓ Project ahead of or on schedule")
        recommendations.append("Maintain current pace and productivity")
        return recommendations
    
    # Prioritized recovery actions based on delay severity
    if variance_days > 30:
        recommendations.extend([
            "🚨 CRITICAL: Implement crash schedule with overtime",
            "Add resources to critical path activities",
            "Consider re-sequencing work for parallel execution",
            "Evaluate fast-track opportunities"
        ])
    elif variance_days > 14:
        recommendations.extend([
            "⚠️ Implement schedule acceleration plan",
            "Increase crew sizes on critical activities",
            "Extend work hours where feasible"
        ])
    else:
        recommendations.extend([
            "Monitor schedule closely and eliminate delays",
            "Optimize sequencing and resource allocation"
        ])
    
    # Productivity-specific
    if productivity_index < 0.9:
        recommendations.extend([
            "Address productivity issues as priority",
            "Review crew composition and skill levels",
            "Eliminate workflow bottlenecks"
        ])
    
    # SPI-specific
    if spi < 0.85:
        recommendations.extend([
            "Conduct detailed schedule analysis",
            "Re-baseline schedule if necessary",
            "Increase project management oversight"
        ])
    
    # General best practices
    recommendations.extend([
        "Update schedule weekly with actual progress",
        "Track critical path daily",
        "Hold weekly schedule coordination meetings"
    ])
    
    return recommendations


def calculate_completion_forecast_risk(
    variance_days: int,
    confidence_range_days: int,
    spi: float,
    productivity_trend: str
) -> Tuple[int, str]:
    """Calculate risk score for completion forecast.
    
    Args:
        variance_days: Days behind baseline schedule
        confidence_range_days: Width of 90% confidence interval
        spi: Schedule Performance Index
        productivity_trend: Trend in productivity
    
    Returns:
        Tuple of (risk_score 0-100, risk_level)
    """
    risk_score = 0
    
    # Variance impact (0-40 points)
    if variance_days > 60:
        risk_score += 40
    elif variance_days > 30:
        risk_score += 30
    elif variance_days > 14:
        risk_score += 20
    elif variance_days > 7:
        risk_score += 10
    
    # Uncertainty impact (0-25 points)
    if confidence_range_days > 60:
        risk_score += 25
    elif confidence_range_days > 30:
        risk_score += 15
    elif confidence_range_days > 14:
        risk_score += 10
    
    # SPI impact (0-20 points)
    if spi < 0.8:
        risk_score += 20
    elif spi < 0.9:
        risk_score += 15
    elif spi < 0.95:
        risk_score += 10
    
    # Trend impact (0-15 points)
    if productivity_trend == "Declining":
        risk_score += 15
    elif productivity_trend == "Stable":
        risk_score += 5
    
    risk_score = min(100, risk_score)
    
    if risk_score < 30:
        risk_level = "LOW"
    elif risk_score < 60:
        risk_level = "MEDIUM"
    else:
        risk_level = "HIGH"
    
    return risk_score, risk_level


if __name__ == "__main__":
    # Quick test
    print("=== Completion Date Forecaster Test ===\n")
    
    # Test EAC calculation
    remaining_days, method = calculate_estimate_at_completion_time(
        current_pct_complete=42.5,
        spi=0.944,
        remaining_days_baseline=202,
        method="composite"
    )
    print(f"Estimated Remaining: {remaining_days} days ({method})\n")
    
    # Test forecast
    forecast = forecast_completion_date(
        project_start_date="2025-01-15",
        days_elapsed=148,
        estimated_remaining_days=remaining_days
    )
    print(f"Forecast Completion: {forecast['forecast_completion_date']}")
    print(f"Days from Today: {forecast['days_from_today']}\n")
    
    # Confidence interval
    confidence = calculate_confidence_interval(
        estimated_remaining_days=remaining_days,
        spi=0.944,
        productivity_index=0.92,
        historical_variance=0.15
    )
    print(f"90% Confidence Interval: {confidence['confidence_90']['low']}-{confidence['confidence_90']['high']} days")
    print(f"Uncertainty: {confidence['uncertainty_level']}\n")
    
    # Compare to baseline
    comparison = compare_to_baseline_completion(
        forecast_date=forecast['forecast_completion_date'],
        baseline_completion_date="2025-12-31"
    )
    print(f"Schedule Status: {comparison['status']}")
    print(f"Variance: {comparison['variance_days']} days ({comparison['variance_weeks']} weeks)\n")
    
    # Risk score
    risk_score, risk_level = calculate_completion_forecast_risk(
        variance_days=comparison['variance_days'],
        confidence_range_days=confidence['confidence_90']['range_days'],
        spi=0.944,
        productivity_trend="Declining"
    )
    print(f"Completion Forecast Risk: {risk_score} - {risk_level}")


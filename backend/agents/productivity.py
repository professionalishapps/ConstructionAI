"""Agent 7: Productivity Trend Tracker

Measures daily productivity rates vs benchmarks and identifies declining trends.
"""
from typing import Dict, List, Tuple, Optional
from datetime import datetime


def calculate_productivity_rate(
    units_completed: float,
    labor_hours: float,
    unit_type: str = "units"
) -> Tuple[float, str]:
    """Calculate productivity rate (units per labor-hour).
    
    Args:
        units_completed: Units of work completed (sq ft, cubic yards, etc.)
        labor_hours: Total labor hours spent
        unit_type: Type of unit for display
    
    Returns:
        Tuple of (productivity_rate, formatted_string)
    """
    if labor_hours <= 0:
        return 0.0, f"0.0 {unit_type}/hour (No labor data)"
    
    rate = units_completed / labor_hours
    return round(rate, 2), f"{rate:.2f} {unit_type}/hour"


def compare_to_benchmark(
    actual_rate: float,
    benchmark_rate: float
) -> Tuple[float, str]:
    """Compare actual productivity to benchmark.
    
    Args:
        actual_rate: Actual productivity rate
        benchmark_rate: Industry benchmark or target rate
    
    Returns:
        Tuple of (productivity_index, assessment)
        Productivity Index: 1.0 = at benchmark, >1.0 = above, <1.0 = below
    """
    if benchmark_rate <= 0:
        return 1.0, "No benchmark available"
    
    index = actual_rate / benchmark_rate
    
    if index >= 1.1:
        assessment = "Excellent - Above benchmark"
    elif index >= 0.95:
        assessment = "Good - At benchmark"
    elif index >= 0.8:
        assessment = "Fair - Below benchmark"
    else:
        assessment = "Poor - Significantly below benchmark"
    
    return round(index, 3), assessment


def detect_productivity_decline(
    historical_rates: List[Dict[str, any]],
    threshold_pct: float = 15.0
) -> Tuple[bool, List[str]]:
    """Detect declining productivity trends.
    
    Args:
        historical_rates: List of dicts with 'date' and 'rate'
        threshold_pct: Decline threshold percentage to trigger alert
    
    Returns:
        Tuple of (decline_detected, list of observations)
    """
    observations = []
    decline_detected = False
    
    if len(historical_rates) < 3:
        return False, ["Insufficient data for trend analysis"]
    
    # Sort by date
    sorted_rates = sorted(historical_rates, key=lambda x: x.get('date', ''))
    rates = [r.get('rate', 0) for r in sorted_rates]
    
    # Calculate moving average
    recent_avg = sum(rates[-3:]) / 3  # Last 3 periods
    earlier_avg = sum(rates[:3]) / 3  # First 3 periods
    
    if earlier_avg > 0:
        change_pct = ((recent_avg - earlier_avg) / earlier_avg) * 100
        
        if change_pct < -threshold_pct:
            decline_detected = True
            observations.append(f"Productivity declined {abs(change_pct):.1f}% from baseline")
        elif change_pct > threshold_pct:
            observations.append(f"Productivity improved {change_pct:.1f}% from baseline")
        else:
            observations.append(f"Productivity relatively stable ({change_pct:+.1f}%)")
    
    # Check for consecutive declines
    declines = 0
    for i in range(1, len(rates)):
        if rates[i] < rates[i-1]:
            declines += 1
    
    if declines >= len(rates) * 0.6:
        decline_detected = True
        observations.append(f"Consistent downward trend detected ({declines}/{len(rates)-1} periods)")
    
    # Check volatility
    if len(rates) >= 5:
        avg_rate = sum(rates) / len(rates)
        variance = sum((r - avg_rate) ** 2 for r in rates) / len(rates)
        std_dev = variance ** 0.5
        cv = (std_dev / avg_rate * 100) if avg_rate > 0 else 0
        
        if cv > 20:
            observations.append(f"High productivity variability (CV: {cv:.1f}%)")
    
    if not observations:
        observations.append("No significant productivity trends detected")
    
    return decline_detected, observations


def analyze_contributing_factors(
    productivity_data: List[Dict[str, any]],
    weather_data: Optional[List[Dict[str, any]]] = None,
    crew_size_data: Optional[List[Dict[str, any]]] = None
) -> List[str]:
    """Analyze factors contributing to productivity changes.
    
    Args:
        productivity_data: List of productivity records with 'date', 'rate'
        weather_data: Optional weather data with 'date', 'adverse_conditions'
        crew_size_data: Optional crew size data with 'date', 'crew_size'
    
    Returns:
        List of contributing factor insights
    """
    factors = []
    
    if len(productivity_data) < 2:
        return ["Insufficient data for factor analysis"]
    
    # Sort all data by date for alignment
    prod_by_date = {p['date']: p['rate'] for p in productivity_data}
    dates = sorted(prod_by_date.keys())
    
    # Weather correlation
    if weather_data:
        weather_by_date = {w['date']: w.get('adverse_conditions', False) for w in weather_data}
        
        bad_weather_productivity = []
        good_weather_productivity = []
        
        for date in dates:
            if date in weather_by_date:
                rate = prod_by_date[date]
                if weather_by_date[date]:
                    bad_weather_productivity.append(rate)
                else:
                    good_weather_productivity.append(rate)
        
        if bad_weather_productivity and good_weather_productivity:
            bad_avg = sum(bad_weather_productivity) / len(bad_weather_productivity)
            good_avg = sum(good_weather_productivity) / len(good_weather_productivity)
            
            if good_avg > 0:
                impact_pct = ((good_avg - bad_avg) / good_avg) * 100
                if impact_pct > 10:
                    factors.append(f"Weather impacts productivity by ~{impact_pct:.0f}%")
    
    # Crew size correlation
    if crew_size_data:
        crew_by_date = {c['date']: c.get('crew_size', 0) for c in crew_size_data}
        
        # Check if productivity scales with crew size
        paired_data = []
        for date in dates:
            if date in crew_by_date:
                paired_data.append((crew_by_date[date], prod_by_date[date]))
        
        if len(paired_data) >= 3:
            # Simple correlation check
            avg_crew = sum(p[0] for p in paired_data) / len(paired_data)
            large_crew_prod = [p[1] for p in paired_data if p[0] > avg_crew]
            small_crew_prod = [p[1] for p in paired_data if p[0] <= avg_crew]
            
            if large_crew_prod and small_crew_prod:
                large_avg = sum(large_crew_prod) / len(large_crew_prod)
                small_avg = sum(small_crew_prod) / len(small_crew_prod)
                
                if large_avg < small_avg * 0.9:
                    factors.append("Larger crews showing lower per-person productivity")
                elif large_avg > small_avg * 1.1:
                    factors.append("Crew size scaling effectively")
    
    # Learning curve analysis
    if len(dates) >= 5:
        early_rates = [prod_by_date[d] for d in dates[:len(dates)//2]]
        later_rates = [prod_by_date[d] for d in dates[len(dates)//2:]]
        
        early_avg = sum(early_rates) / len(early_rates)
        later_avg = sum(later_rates) / len(later_rates)
        
        if later_avg > early_avg * 1.15:
            factors.append("Positive learning curve observed")
        elif later_avg < early_avg * 0.85:
            factors.append("Productivity declining over time - investigate fatigue or resource issues")
    
    if not factors:
        factors.append("No clear contributing factors identified")
    
    return factors


def recommend_productivity_improvements(
    productivity_index: float,
    decline_detected: bool,
    contributing_factors: List[str]
) -> List[str]:
    """Recommend actions to improve productivity.
    
    Args:
        productivity_index: Current productivity vs benchmark
        decline_detected: Whether declining trend detected
        contributing_factors: List of identified contributing factors
    
    Returns:
        List of recommendations
    """
    recommendations = []
    
    # Based on productivity level
    if productivity_index >= 1.0:
        recommendations.append("Productivity is meeting or exceeding benchmark")
        recommendations.append("Document successful practices for replication")
    else:
        recommendations.append("Productivity below benchmark - implement improvement plan")
    
    # Based on trends
    if decline_detected:
        recommendations.extend([
            "Investigate root causes of productivity decline",
            "Review crew composition and experience levels",
            "Assess tool and equipment adequacy",
            "Check for material availability issues"
        ])
    
    # Factor-specific recommendations
    factors_text = ' '.join(contributing_factors).lower()
    
    if 'weather' in factors_text:
        recommendations.extend([
            "Improve weather protection measures",
            "Plan weather-independent backup activities"
        ])
    
    if 'crew' in factors_text or 'fatigue' in factors_text:
        recommendations.extend([
            "Optimize crew size for tasks",
            "Review work schedules and break patterns",
            "Consider crew rotation or additional shifts"
        ])
    
    if 'learning curve' in factors_text and 'declining' in factors_text:
        recommendations.extend([
            "Provide additional training or supervision",
            "Review work methods and procedures",
            "Assess crew morale and motivation"
        ])
    
    # General recommendations
    if productivity_index < 0.9:
        recommendations.extend([
            "Benchmark against similar activities",
            "Conduct time and motion studies",
            "Identify and eliminate waste in work processes"
        ])
    
    return recommendations


def calculate_productivity_risk_score(
    productivity_index: float,
    decline_detected: bool,
    variability_high: bool
) -> Tuple[int, str]:
    """Calculate productivity risk score.
    
    Args:
        productivity_index: Productivity vs benchmark (1.0 = at benchmark)
        decline_detected: Whether declining trend detected
        variability_high: Whether high variability detected
    
    Returns:
        Tuple of (risk_score 0-100, risk_level)
    """
    risk_score = 0
    
    # Index-based risk (0-50 points)
    if productivity_index < 0.6:
        risk_score += 50
    elif productivity_index < 0.75:
        risk_score += 40
    elif productivity_index < 0.9:
        risk_score += 25
    elif productivity_index < 0.95:
        risk_score += 10
    
    # Decline trend (0-30 points)
    if decline_detected:
        risk_score += 30
    
    # Variability (0-20 points)
    if variability_high:
        risk_score += 20
    
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
    print("=== Productivity Trend Tracker Test ===\n")
    
    # Test productivity calculation
    rate, rate_str = calculate_productivity_rate(
        units_completed=450,
        labor_hours=180,
        unit_type="sq ft"
    )
    print(f"Productivity Rate: {rate_str}\n")
    
    # Test benchmark comparison
    benchmark = 3.0
    index, assessment = compare_to_benchmark(rate, benchmark)
    print(f"Productivity Index: {index} ({assessment})\n")
    
    # Test trend detection
    historical = [
        {'date': '2025-01-01', 'rate': 3.2},
        {'date': '2025-01-08', 'rate': 3.0},
        {'date': '2025-01-15', 'rate': 2.8},
        {'date': '2025-01-22', 'rate': 2.6},
        {'date': '2025-01-29', 'rate': 2.5},
    ]
    
    decline, observations = detect_productivity_decline(historical)
    print(f"Decline Detected: {decline}")
    print("Observations:")
    for obs in observations:
        print(f"  - {obs}")
    print()
    
    # Test risk score
    risk_score, risk_level = calculate_productivity_risk_score(
        productivity_index=index,
        decline_detected=decline,
        variability_high=False
    )
    print(f"Productivity Risk: {risk_score} - {risk_level}")


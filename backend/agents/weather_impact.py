"""Weather Impact Analysis Agent

Analyzes weather data and project sensitivity to determine schedule impacts
and suggest mitigation strategies.
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import math


def calculate_sensitivity_factor(activity_type: str) -> float:
    """Calculate weather sensitivity factor for different activity types.
    
    Returns value 0-1 where:
    0 = Not affected by weather
    1 = Completely weather dependent
    """
    sensitivity_map = {
        # Exterior work highly affected
        'excavation': 0.9,
        'foundation': 0.8,
        'site_work': 0.9,
        'concrete_pour': 0.8,
        'roofing': 0.9,
        'exterior_finish': 0.7,
        'landscaping': 0.8,
        
        # Some weather impact
        'framing': 0.5,
        'exterior_walls': 0.6,
        'windows': 0.5,
        'exterior_doors': 0.5,
        
        # Minimal weather impact
        'interior_rough': 0.2,
        'drywall': 0.1,
        'interior_finish': 0.1,
        'mep': 0.2,
        
        # Indoor work largely unaffected
        'interior_paint': 0.0,
        'flooring': 0.0,
        'fixtures': 0.0,
        'cleanup': 0.0
    }
    
    return sensitivity_map.get(activity_type.lower(), 0.5)  # default moderate sensitivity


def assess_weather_impact(weather_data: Dict,
                        activity_type: str,
                        duration_days: int) -> Tuple[float, List[str]]:
    """Assess weather impact on activity.
    
    Args:
        weather_data: Dict with weather metrics
        activity_type: Type of construction activity
        duration_days: Planned duration in days
    
    Returns:
        Tuple of (impact_factor, list of impact descriptions)
        impact_factor: 0-1 where 1 = severe impact
    """
    impacts = []
    sensitivity = calculate_sensitivity_factor(activity_type)
    
    if sensitivity < 0.2:
        impacts.append("Activity has minimal weather sensitivity")
        return 0.1, impacts
        
    # Example weather thresholds
    rain_threshold_mm = 5.0  # significant rain
    wind_threshold_kph = 25.0  # strong wind
    temp_min_c = 4.0  # too cold
    temp_max_c = 35.0  # too hot
    
    # Count impact days
    impact_days = 0
    
    # This would iterate through actual weather data
    # Using placeholder logic for now
    example_bad_weather_days = 3
    impact_days = example_bad_weather_days
    
    impact_ratio = impact_days / duration_days if duration_days > 0 else 0
    weighted_impact = impact_ratio * sensitivity
    
    # Generate impact descriptions
    if weighted_impact > 0.5:
        impacts.append(f"Severe weather impact likely: {round(weighted_impact * 100)}% impact expected")
    elif weighted_impact > 0.25:
        impacts.append(f"Moderate weather impact possible: {round(weighted_impact * 100)}% impact expected")
    else:
        impacts.append(f"Minor weather impact: {round(weighted_impact * 100)}% impact expected")
        
    if sensitivity > 0.7:
        impacts.append("Activity is highly weather-sensitive - consider schedule buffers")
        
    return weighted_impact, impacts


def suggest_mitigations(impact_factor: float, 
                       activity_type: str) -> List[str]:
    """Suggest mitigation strategies based on weather impact.
    
    Args:
        impact_factor: 0-1 severity of weather impact
        activity_type: Type of construction activity
    
    Returns:
        List of mitigation suggestions
    """
    suggestions = []
    
    if impact_factor < 0.2:
        suggestions.append("Standard weather monitoring adequate")
        return suggestions
        
    # High impact mitigations
    if impact_factor > 0.5:
        suggestions.extend([
            "Consider temporary weather protection structures",
            "Plan alternative indoor work for severe weather days",
            "Add weather contingency to schedule",
            "Review weather-dependent material storage",
            "Evaluate equipment rental timing"
        ])
        
    # Moderate impact mitigations    
    if 0.2 < impact_factor <= 0.5:
        suggestions.extend([
            "Monitor detailed weather forecasts",
            "Prepare backup work areas",
            "Review material protection measures",
            "Consider schedule flexibility"
        ])
        
    # Activity-specific suggestions
    if activity_type.lower() in ['concrete_pour', 'foundation']:
        suggestions.append("Ensure concrete curing requirements account for weather")
    elif activity_type.lower() in ['roofing', 'exterior_finish']:
        suggestions.append("Plan work during optimal weather windows")
    elif activity_type.lower() in ['excavation', 'site_work']:
        suggestions.append("Monitor soil conditions and drainage")
        
    return suggestions


if __name__ == "__main__":
    # Quick test
    weather_data = {
        'rain_mm': 12.5,
        'wind_kph': 28,
        'temp_c': 18
    }
    
    activity = "foundation"
    duration = 14
    
    impact, descriptions = assess_weather_impact(weather_data, activity, duration)
    
    print(f"Weather Impact Analysis for {activity}")
    print(f"Impact Factor: {impact:.2f}")
    print("\nImpact Assessment:")
    for desc in descriptions:
        print(f"- {desc}")
        
    suggestions = suggest_mitigations(impact, activity)
    print("\nSuggested Mitigations:")
    for sug in suggestions:
        print(f"- {sug}")
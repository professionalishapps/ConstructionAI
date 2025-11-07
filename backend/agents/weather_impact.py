"""Weather Impact Analysis Agent

Analyzes weather data and project sensitivity to determine schedule impacts
and suggest mitigation strategies.
Uses Open-Meteo API for real weather forecasts.
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import math
import requests


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


def fetch_weather_forecast(
    latitude: float,
    longitude: float,
    forecast_days: int = 14
) -> Dict[str, any]:
    """Fetch weather forecast from Open-Meteo API.
    
    Args:
        latitude: Location latitude
        longitude: Location longitude
        forecast_days: Number of days to forecast (max 16)
    
    Returns:
        Dict with weather forecast data
    """
    try:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            'latitude': latitude,
            'longitude': longitude,
            'daily': 'temperature_2m_max,temperature_2m_min,precipitation_sum,windspeed_10m_max,rain_sum',
            'forecast_days': min(forecast_days, 16),
            'temperature_unit': 'fahrenheit',
            'windspeed_unit': 'mph',
            'precipitation_unit': 'inch',
            'timezone': 'auto'
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return {
                'success': True,
                'data': data,
                'daily': data.get('daily', {}),
                'location': {
                    'latitude': latitude,
                    'longitude': longitude
                }
            }
        else:
            return {
                'success': False,
                'error': f'API returned status {response.status_code}',
                'fallback': True
            }
    
    except requests.exceptions.RequestException as e:
        return {
            'success': False,
            'error': f'API request failed: {str(e)}',
            'fallback': True
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Unexpected error: {str(e)}',
            'fallback': True
        }


def analyze_weather_forecast(
    weather_forecast: Dict[str, any],
    activity_type: str,
    activity_duration_days: int
) -> Dict[str, any]:
    """Analyze weather forecast for construction impact.
    
    Args:
        weather_forecast: Weather data from Open-Meteo
        activity_type: Type of construction activity
        activity_duration_days: Duration of activity
    
    Returns:
        Dict with impact analysis
    """
    if not weather_forecast.get('success', False):
        # Fallback to simulated data
        return {
            'estimated_delay_days': 3,
            'risk_score': 45,
            'bad_weather_days': 3,
            'observations': ['Using simulated weather data - API unavailable']
        }
    
    daily_data = weather_forecast.get('daily', {})
    
    # Weather thresholds for construction
    RAIN_THRESHOLD_INCH = 0.2  # Significant rain
    WIND_THRESHOLD_MPH = 25.0  # Strong wind
    TEMP_MIN_F = 40.0  # Too cold for concrete
    TEMP_MAX_F = 95.0  # Too hot
    
    precipitation = daily_data.get('rain_sum', [])
    wind_speeds = daily_data.get('windspeed_10m_max', [])
    temps_max = daily_data.get('temperature_2m_max', [])
    temps_min = daily_data.get('temperature_2m_min', [])
    dates = daily_data.get('time', [])
    
    # Count bad weather days
    bad_weather_days = 0
    bad_weather_reasons = []
    
    forecast_length = min(len(dates), activity_duration_days)
    
    for i in range(forecast_length):
        reasons = []
        
        if i < len(precipitation) and precipitation[i] > RAIN_THRESHOLD_INCH:
            reasons.append(f"Rain: {precipitation[i]:.2f}\"")
        
        if i < len(wind_speeds) and wind_speeds[i] > WIND_THRESHOLD_MPH:
            reasons.append(f"Wind: {wind_speeds[i]:.0f} mph")
        
        if i < len(temps_min) and temps_min[i] < TEMP_MIN_F:
            reasons.append(f"Cold: {temps_min[i]:.0f}°F")
        
        if i < len(temps_max) and temps_max[i] > TEMP_MAX_F:
            reasons.append(f"Hot: {temps_max[i]:.0f}°F")
        
        if reasons:
            bad_weather_days += 1
            if i < len(dates):
                bad_weather_reasons.append(f"{dates[i]}: {', '.join(reasons)}")
    
    # Calculate impact based on activity sensitivity
    sensitivity = calculate_sensitivity_factor(activity_type)
    estimated_delay = int(bad_weather_days * sensitivity)
    
    # Risk score (0-100)
    risk_score = min(100, int((bad_weather_days / forecast_length * 100) * sensitivity))
    
    observations = []
    observations.append(f"{bad_weather_days} adverse weather days in {forecast_length}-day forecast")
    
    if estimated_delay > 5:
        observations.append(f"High risk: {estimated_delay} days potential delay")
    elif estimated_delay > 2:
        observations.append(f"Moderate risk: {estimated_delay} days potential delay")
    else:
        observations.append(f"Low risk: {estimated_delay} days potential delay")
    
    if bad_weather_reasons[:3]:  # Show first 3
        observations.extend(bad_weather_reasons[:3])
    
    return {
        'estimated_delay_days': estimated_delay,
        'risk_score': risk_score,
        'bad_weather_days': bad_weather_days,
        'forecast_days_analyzed': forecast_length,
        'observations': observations,
        'weather_details': bad_weather_reasons[:5]
    }


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
    # Quick test with real API
    print("=== Weather Impact Modeler Test ===\n")
    
    # San Francisco coordinates (from spec)
    latitude = 37.7749
    longitude = -122.4194
    
    print(f"Fetching weather forecast for SF ({latitude}, {longitude})...\n")
    
    # Fetch real forecast
    forecast = fetch_weather_forecast(latitude, longitude, forecast_days=14)
    
    if forecast.get('success'):
        print("✓ Successfully fetched weather data from Open-Meteo API\n")
    else:
        print(f"⚠ API unavailable: {forecast.get('error')}\n")
    
    # Analyze for foundation work
    activity = "foundation"
    duration = 14
    
    analysis = analyze_weather_forecast(forecast, activity, duration)
    
    print(f"Weather Impact Analysis for {activity} (14-day forecast):")
    print(f"  Estimated Delay: {analysis['estimated_delay_days']} days")
    print(f"  Risk Score: {analysis['risk_score']}/100")
    print(f"  Bad Weather Days: {analysis['bad_weather_days']}")
    print("\nObservations:")
    for obs in analysis['observations']:
        print(f"  - {obs}")
    
    # Suggestions
    suggestions = suggest_mitigations(analysis['risk_score'] / 100, activity)
    print("\nSuggested Mitigations:")
    for sug in suggestions[:5]:
        print(f"  - {sug}")
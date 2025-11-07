"""Agent 5: Supply Chain Disruption Detector

Monitors material availability, supplier delivery reliability, and supply chain risks.
"""
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional


def calculate_supplier_reliability(
    on_time_deliveries: int,
    total_deliveries: int,
    lead_time_extensions: int = 0
) -> Tuple[float, str]:
    """Calculate supplier reliability score (0-100).
    
    Args:
        on_time_deliveries: Number of deliveries made on time
        total_deliveries: Total number of deliveries
        lead_time_extensions: Number of times lead time was extended
    
    Returns:
        Tuple of (reliability_score, assessment)
    """
    if total_deliveries == 0:
        return 100.0, "No delivery history available"
    
    # Base score from on-time delivery rate
    on_time_rate = (on_time_deliveries / total_deliveries) * 100
    
    # Penalty for lead time extensions
    extension_penalty = min(20, lead_time_extensions * 5)
    
    score = max(0, on_time_rate - extension_penalty)
    
    if score >= 90:
        assessment = "Excellent"
    elif score >= 75:
        assessment = "Good"
    elif score >= 60:
        assessment = "Fair"
    else:
        assessment = "Poor - High Risk"
    
    return round(score, 1), assessment


def detect_material_shortages(
    materials_list: List[Dict[str, any]]
) -> Tuple[List[str], int]:
    """Detect at-risk materials based on supply indicators.
    
    Args:
        materials_list: List of material dicts with 'name', 'lead_time_days', 
                       'stock_level', 'critical'
    
    Returns:
        Tuple of (at_risk_materials list, risk_score 0-100)
    """
    at_risk = []
    risk_points = 0
    
    for material in materials_list:
        name = material.get('name', 'Unknown')
        lead_time = material.get('lead_time_days', 0)
        stock_level = material.get('stock_level', 100)  # percentage
        is_critical = material.get('critical', False)
        
        # Risk factors
        if stock_level < 20:
            at_risk.append(f"{name} - Low stock ({stock_level}%)")
            risk_points += 15 if is_critical else 10
        elif stock_level < 50 and lead_time > 14:
            at_risk.append(f"{name} - Moderate stock with long lead time")
            risk_points += 8 if is_critical else 5
        
        if lead_time > 30:
            if name not in [item.split(' - ')[0] for item in at_risk]:
                at_risk.append(f"{name} - Extended lead time ({lead_time} days)")
            risk_points += 10 if is_critical else 5
    
    # Cap risk score at 100
    risk_score = min(100, risk_points)
    
    return at_risk, risk_score


def analyze_supply_chain_trends(
    delivery_history: List[Dict[str, any]]
) -> Dict[str, any]:
    """Analyze trends in supply chain performance.
    
    Args:
        delivery_history: List of delivery records with 'date', 'on_time', 
                         'delay_days'
    
    Returns:
        Dict with trend analysis
    """
    if not delivery_history:
        return {
            'trend': 'No Data',
            'avg_delay_days': 0,
            'deterioration': False,
            'observations': ['Insufficient delivery history']
        }
    
    # Sort by date
    sorted_history = sorted(delivery_history, key=lambda x: x.get('date', ''))
    
    # Calculate metrics
    total_deliveries = len(sorted_history)
    on_time_count = sum(1 for d in sorted_history if d.get('on_time', False))
    total_delay_days = sum(d.get('delay_days', 0) for d in sorted_history)
    
    on_time_rate = (on_time_count / total_deliveries) * 100
    avg_delay = total_delay_days / total_deliveries
    
    # Trend analysis - compare first half vs second half
    mid_point = len(sorted_history) // 2
    first_half_on_time = sum(1 for d in sorted_history[:mid_point] if d.get('on_time', False))
    second_half_on_time = sum(1 for d in sorted_history[mid_point:] if d.get('on_time', False))
    
    first_half_rate = (first_half_on_time / mid_point * 100) if mid_point > 0 else 0
    second_half_rate = (second_half_on_time / (total_deliveries - mid_point) * 100) if (total_deliveries - mid_point) > 0 else 0
    
    deterioration = second_half_rate < first_half_rate - 10  # 10% threshold
    
    observations = []
    if on_time_rate >= 90:
        observations.append("Supply chain performance is excellent")
    elif on_time_rate >= 75:
        observations.append("Supply chain performance is good")
    else:
        observations.append("Supply chain performance needs improvement")
    
    if deterioration:
        observations.append(f"Performance declining: {first_half_rate:.1f}% to {second_half_rate:.1f}%")
    
    if avg_delay > 5:
        observations.append(f"Average delivery delay: {avg_delay:.1f} days")
    
    trend = "Deteriorating" if deterioration else "Stable" if abs(second_half_rate - first_half_rate) < 5 else "Improving"
    
    return {
        'trend': trend,
        'on_time_rate': round(on_time_rate, 1),
        'avg_delay_days': round(avg_delay, 1),
        'deterioration': deterioration,
        'observations': observations
    }


def recommend_alternatives(
    at_risk_materials: List[str],
    supplier_database: Optional[Dict[str, List[str]]] = None
) -> List[str]:
    """Recommend alternative suppliers or mitigation strategies.
    
    Args:
        at_risk_materials: List of materials at risk
        supplier_database: Optional dict mapping materials to alternative suppliers
    
    Returns:
        List of recommendations
    """
    recommendations = []
    
    if not at_risk_materials:
        recommendations.append("No immediate supply chain concerns")
        return recommendations
    
    recommendations.append(f"{len(at_risk_materials)} materials identified as at-risk")
    
    # General recommendations
    recommendations.extend([
        "Review inventory levels for critical materials",
        "Contact suppliers to confirm delivery schedules",
        "Identify alternative suppliers for at-risk materials",
        "Consider increasing safety stock for long-lead items",
        "Evaluate potential for material substitutions"
    ])
    
    # If we have supplier database, provide specific alternatives
    if supplier_database:
        for material in at_risk_materials[:3]:  # Top 3
            material_name = material.split(' - ')[0]
            if material_name in supplier_database:
                alternatives = supplier_database[material_name]
                if alternatives:
                    recommendations.append(
                        f"Alternative suppliers for {material_name}: {', '.join(alternatives[:2])}"
                    )
    
    return recommendations


def calculate_supply_chain_risk_score(
    supplier_scores: List[float],
    material_shortage_score: int,
    trend_deterioration: bool
) -> Tuple[int, str]:
    """Calculate overall supply chain risk score.
    
    Args:
        supplier_scores: List of individual supplier reliability scores
        material_shortage_score: Material shortage risk score (0-100)
        trend_deterioration: Whether trends are deteriorating
    
    Returns:
        Tuple of (risk_score 0-100, risk_level)
    """
    # Average supplier score (inverted to risk)
    if supplier_scores:
        avg_supplier_score = sum(supplier_scores) / len(supplier_scores)
        supplier_risk = 100 - avg_supplier_score
    else:
        supplier_risk = 50  # Unknown
    
    # Weighted combination
    # 40% supplier reliability, 50% material shortage risk, 10% trend
    risk_score = (
        supplier_risk * 0.4 +
        material_shortage_score * 0.5 +
        (20 if trend_deterioration else 0) * 0.1
    )
    
    risk_score = min(100, max(0, risk_score))
    
    if risk_score < 30:
        risk_level = "LOW"
    elif risk_score < 60:
        risk_level = "MEDIUM"
    else:
        risk_level = "HIGH"
    
    return int(risk_score), risk_level


if __name__ == "__main__":
    # Quick test
    print("=== Supply Chain Disruption Detector Test ===\n")
    
    # Test supplier reliability
    score, assessment = calculate_supplier_reliability(
        on_time_deliveries=18,
        total_deliveries=20,
        lead_time_extensions=2
    )
    print(f"Supplier Reliability: {score} - {assessment}\n")
    
    # Test material shortages
    materials = [
        {'name': 'Rebar Steel', 'lead_time_days': 21, 'stock_level': 15, 'critical': True},
        {'name': 'Concrete', 'lead_time_days': 3, 'stock_level': 80, 'critical': True},
        {'name': 'Lumber', 'lead_time_days': 35, 'stock_level': 45, 'critical': False},
    ]
    at_risk, risk_score = detect_material_shortages(materials)
    print(f"Material Shortage Risk Score: {risk_score}")
    print("At-risk materials:")
    for material in at_risk:
        print(f"  - {material}")
    print()
    
    # Test trend analysis
    from datetime import date
    history = [
        {'date': '2025-01-01', 'on_time': True, 'delay_days': 0},
        {'date': '2025-01-05', 'on_time': True, 'delay_days': 0},
        {'date': '2025-01-10', 'on_time': False, 'delay_days': 3},
        {'date': '2025-01-15', 'on_time': False, 'delay_days': 5},
        {'date': '2025-01-20', 'on_time': False, 'delay_days': 2},
        {'date': '2025-01-25', 'on_time': True, 'delay_days': 0},
    ]
    trends = analyze_supply_chain_trends(history)
    print(f"Trend Analysis: {trends['trend']}")
    print(f"On-time Rate: {trends['on_time_rate']}%")
    print("Observations:")
    for obs in trends['observations']:
        print(f"  - {obs}")
    print()
    
    # Overall risk
    overall_risk, level = calculate_supply_chain_risk_score(
        supplier_scores=[score],
        material_shortage_score=risk_score,
        trend_deterioration=trends['deterioration']
    )
    print(f"Overall Supply Chain Risk: {overall_risk} - {level}")


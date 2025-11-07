"""Agent 11: Delay Cause Identifier

Categorizes delays by root cause (weather, labor, materials, design).
Depends on Agents 1, 4, 5, 6.
"""
from typing import Dict, List, Tuple, Optional
from collections import defaultdict


def categorize_delay_incidents(
    delay_incidents: List[Dict[str, any]]
) -> Dict[str, any]:
    """Categorize delays by root cause.
    
    Args:
        delay_incidents: List of delay dicts with 'cause', 'days', 'date', 'controllable'
    
    Returns:
        Dict with delay categorization
    """
    by_cause = defaultdict(lambda: {'count': 0, 'total_days': 0, 'incidents': []})
    
    total_delay_days = 0
    controllable_days = 0
    uncontrollable_days = 0
    
    for incident in delay_incidents:
        cause = incident.get('cause', 'Unknown')
        days = incident.get('days', 0)
        controllable = incident.get('controllable', True)
        
        by_cause[cause]['count'] += 1
        by_cause[cause]['total_days'] += days
        by_cause[cause]['incidents'].append(incident)
        
        total_delay_days += days
        
        if controllable:
            controllable_days += days
        else:
            uncontrollable_days += days
    
    # Calculate percentages
    for cause, data in by_cause.items():
        data['percentage'] = (data['total_days'] / total_delay_days * 100) if total_delay_days > 0 else 0
        data['percentage'] = round(data['percentage'], 1)
    
    return {
        'by_cause': dict(by_cause),
        'total_incidents': len(delay_incidents),
        'total_delay_days': total_delay_days,
        'controllable_days': controllable_days,
        'uncontrollable_days': uncontrollable_days,
        'controllable_pct': round((controllable_days / total_delay_days * 100) if total_delay_days > 0 else 0, 1)
    }


def integrate_agent_data_for_delay_analysis(
    schedule_data: Dict[str, any],
    weather_data: Dict[str, any],
    supply_chain_data: Dict[str, any],
    change_order_data: Dict[str, any]
) -> List[Dict[str, any]]:
    """Integrate data from other agents to identify delays.
    
    Args:
        schedule_data: Data from Schedule Variance Agent (Agent 1)
        weather_data: Data from Weather Impact Agent (Agent 4)
        supply_chain_data: Data from Supply Chain Agent (Agent 5)
        change_order_data: Data from Change Order Agent (Agent 6)
    
    Returns:
        List of identified delay incidents
    """
    incidents = []
    
    # Schedule-based delays
    schedule_variance_days = schedule_data.get('days_behind', 0)
    if schedule_variance_days > 0:
        incidents.append({
            'cause': 'Schedule Variance',
            'days': schedule_variance_days,
            'source': 'Agent 1',
            'controllable': True,
            'description': f"{schedule_variance_days} days behind baseline schedule"
        })
    
    # Weather-based delays
    weather_delay_days = weather_data.get('estimated_delay_days', 0)
    weather_risk = weather_data.get('risk_score', 0)
    if weather_delay_days > 0 or weather_risk > 60:
        incidents.append({
            'cause': 'Weather',
            'days': weather_delay_days,
            'source': 'Agent 4',
            'controllable': False,
            'description': f"Weather impact: {weather_delay_days} days delay, risk score {weather_risk}"
        })
    
    # Supply chain delays
    supply_at_risk = supply_chain_data.get('at_risk_materials', [])
    if supply_at_risk:
        # Estimate delay from supply chain issues
        estimated_supply_delay = len(supply_at_risk) * 2  # Rough estimate
        incidents.append({
            'cause': 'Material/Supply Chain',
            'days': estimated_supply_delay,
            'source': 'Agent 5',
            'controllable': True,
            'description': f"{len(supply_at_risk)} at-risk materials causing potential delays"
        })
    
    # Change order delays
    co_count = change_order_data.get('total_count', 0)
    late_phase_cos = change_order_data.get('late_phase_count', 0)
    if co_count > 10 or late_phase_cos > 5:
        # Estimate delay from change orders
        estimated_co_delay = late_phase_cos * 3  # Late changes cause more delay
        incidents.append({
            'cause': 'Design/Change Orders',
            'days': estimated_co_delay,
            'source': 'Agent 6',
            'controllable': True,
            'description': f"{co_count} change orders, {late_phase_cos} in late phase"
        })
    
    return incidents


def analyze_controllable_vs_uncontrollable(
    controllable_pct: float,
    controllable_days: int,
    total_days: int
) -> Dict[str, any]:
    """Analyze the split between controllable and uncontrollable delays.
    
    Args:
        controllable_pct: Percentage of delays that are controllable
        controllable_days: Number of controllable delay days
        total_days: Total delay days
    
    Returns:
        Dict with analysis and opportunity assessment
    """
    uncontrollable_days = total_days - controllable_days
    uncontrollable_pct = 100 - controllable_pct
    
    # Assess improvement opportunity
    if controllable_pct > 70:
        opportunity_level = "HIGH"
        assessment = "Most delays are controllable - significant improvement opportunity"
    elif controllable_pct > 40:
        opportunity_level = "MEDIUM"
        assessment = "Balanced mix - focus on reducing controllable delays"
    else:
        opportunity_level = "LOW"
        assessment = "Most delays are external factors - limited control"
    
    # Potential recovery
    # Assume 50% of controllable delays could be recovered with proper action
    potential_recovery_days = int(controllable_days * 0.5)
    
    return {
        'controllable_days': controllable_days,
        'controllable_pct': controllable_pct,
        'uncontrollable_days': uncontrollable_days,
        'uncontrollable_pct': round(uncontrollable_pct, 1),
        'opportunity_level': opportunity_level,
        'assessment': assessment,
        'potential_recovery_days': potential_recovery_days
    }


def prioritize_mitigation_actions(
    delay_categorization: Dict[str, any]
) -> List[Dict[str, any]]:
    """Prioritize mitigation actions based on delay causes.
    
    Args:
        delay_categorization: Categorized delay data
    
    Returns:
        List of prioritized actions with impact estimates
    """
    actions = []
    by_cause = delay_categorization.get('by_cause', {})
    
    # Sort causes by impact (total delay days)
    sorted_causes = sorted(
        by_cause.items(),
        key=lambda x: x[1]['total_days'],
        reverse=True
    )
    
    for cause, data in sorted_causes[:5]:  # Top 5 causes
        days = data['total_days']
        pct = data['percentage']
        count = data['count']
        
        # Generate cause-specific actions
        if 'weather' in cause.lower():
            action = {
                'cause': cause,
                'priority': 'HIGH' if pct > 30 else 'MEDIUM',
                'impact_days': days,
                'impact_pct': pct,
                'actions': [
                    'Improve weather contingency planning',
                    'Schedule weather-sensitive work in optimal seasons',
                    'Invest in temporary weather protection'
                ],
                'potential_reduction': int(days * 0.2)  # Can reduce by ~20%
            }
        elif 'material' in cause.lower() or 'supply' in cause.lower():
            action = {
                'cause': cause,
                'priority': 'HIGH',
                'impact_days': days,
                'impact_pct': pct,
                'actions': [
                    'Improve procurement planning and lead time management',
                    'Develop backup supplier relationships',
                    'Increase material inventory buffers'
                ],
                'potential_reduction': int(days * 0.6)  # Can reduce by ~60%
            }
        elif 'design' in cause.lower() or 'change' in cause.lower():
            action = {
                'cause': cause,
                'priority': 'HIGH',
                'impact_days': days,
                'impact_pct': pct,
                'actions': [
                    'Improve design coordination and review processes',
                    'Implement stricter change control procedures',
                    'Increase upfront planning time'
                ],
                'potential_reduction': int(days * 0.7)  # Can reduce by ~70%
            }
        elif 'labor' in cause.lower():
            action = {
                'cause': cause,
                'priority': 'MEDIUM',
                'impact_days': days,
                'impact_pct': pct,
                'actions': [
                    'Improve labor resource planning',
                    'Develop backup labor sources',
                    'Enhance crew productivity through training'
                ],
                'potential_reduction': int(days * 0.5)  # Can reduce by ~50%
            }
        else:
            action = {
                'cause': cause,
                'priority': 'MEDIUM',
                'impact_days': days,
                'impact_pct': pct,
                'actions': [
                    f'Investigate root cause of {cause} delays',
                    'Develop mitigation plan',
                    'Monitor and track improvement'
                ],
                'potential_reduction': int(days * 0.4)  # Can reduce by ~40%
            }
        
        actions.append(action)
    
    return actions


def generate_delay_breakdown_chart_data(
    delay_categorization: Dict[str, any]
) -> Dict[str, any]:
    """Generate data for delay breakdown pie chart.
    
    Args:
        delay_categorization: Categorized delay data
    
    Returns:
        Dict with chart data
    """
    by_cause = delay_categorization.get('by_cause', {})
    
    labels = []
    values = []
    percentages = []
    
    for cause, data in by_cause.items():
        labels.append(cause)
        values.append(data['total_days'])
        percentages.append(data['percentage'])
    
    return {
        'chart_type': 'pie',
        'labels': labels,
        'values': values,
        'percentages': percentages,
        'title': 'Delay Root Cause Breakdown'
    }


def calculate_delay_cause_risk_score(
    total_delay_days: int,
    controllable_pct: float,
    top_cause_concentration: float
) -> Tuple[int, str]:
    """Calculate risk score for delay causes.
    
    Args:
        total_delay_days: Total days of delay
        controllable_pct: Percentage of controllable delays
        top_cause_concentration: % of delays from single largest cause
    
    Returns:
        Tuple of (risk_score 0-100, risk_level)
    """
    risk_score = 0
    
    # Total delay magnitude (0-40 points)
    if total_delay_days > 60:
        risk_score += 40
    elif total_delay_days > 30:
        risk_score += 30
    elif total_delay_days > 15:
        risk_score += 20
    elif total_delay_days > 5:
        risk_score += 10
    
    # Controllable delays (0-30 points)
    # Higher controllable % = higher risk (means we should have prevented them)
    if controllable_pct > 70:
        risk_score += 30
    elif controllable_pct > 50:
        risk_score += 20
    elif controllable_pct > 30:
        risk_score += 10
    
    # Concentration risk (0-30 points)
    # High concentration in one cause is risky
    if top_cause_concentration > 50:
        risk_score += 30
    elif top_cause_concentration > 35:
        risk_score += 20
    elif top_cause_concentration > 25:
        risk_score += 10
    
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
    print("=== Delay Cause Identifier Test ===\n")
    
    # Test data
    delays = [
        {'cause': 'Weather', 'days': 12, 'controllable': False},
        {'cause': 'Material Delivery', 'days': 8, 'controllable': True},
        {'cause': 'Weather', 'days': 5, 'controllable': False},
        {'cause': 'Design Changes', 'days': 15, 'controllable': True},
        {'cause': 'Labor Shortage', 'days': 6, 'controllable': True},
        {'cause': 'Material Delivery', 'days': 4, 'controllable': True},
    ]
    
    # Categorize
    categorization = categorize_delay_incidents(delays)
    print(f"Total Delays: {categorization['total_delay_days']} days")
    print(f"Controllable: {categorization['controllable_pct']}%\n")
    
    print("Breakdown by Cause:")
    for cause, data in categorization['by_cause'].items():
        print(f"  {cause}: {data['total_days']} days ({data['percentage']}%)")
    print()
    
    # Analyze controllable vs uncontrollable
    analysis = analyze_controllable_vs_uncontrollable(
        controllable_pct=categorization['controllable_pct'],
        controllable_days=categorization['controllable_days'],
        total_days=categorization['total_delay_days']
    )
    print(f"Opportunity Assessment: {analysis['opportunity_level']}")
    print(f"Potential Recovery: {analysis['potential_recovery_days']} days\n")
    
    # Prioritize actions
    actions = prioritize_mitigation_actions(categorization)
    print("Top Mitigation Actions:")
    for i, action in enumerate(actions[:3], 1):
        print(f"{i}. {action['cause']} ({action['impact_days']} days, {action['impact_pct']}%)")
        print(f"   Potential reduction: {action['potential_reduction']} days")
    print()
    
    # Risk score
    top_cause_pct = max(d['percentage'] for d in categorization['by_cause'].values())
    risk_score, risk_level = calculate_delay_cause_risk_score(
        total_delay_days=categorization['total_delay_days'],
        controllable_pct=categorization['controllable_pct'],
        top_cause_concentration=top_cause_pct
    )
    print(f"Delay Cause Risk: {risk_score} - {risk_level}")


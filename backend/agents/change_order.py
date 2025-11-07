"""Agent 6: Change Order Pattern Analyzer

Identifies excessive change orders suggesting scope creep and analyzes patterns.
"""
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from collections import defaultdict


def calculate_change_order_rate(
    total_change_orders: float,
    original_budget: float
) -> Tuple[float, str]:
    """Calculate change order rate as percentage of original budget.
    
    Args:
        total_change_orders: Total value of all change orders
        original_budget: Original contract budget
    
    Returns:
        Tuple of (rate_percentage, assessment)
    """
    if original_budget <= 0:
        return 0.0, "Invalid budget"
    
    rate = (total_change_orders / original_budget) * 100
    
    # Industry benchmarks
    if rate < 5:
        assessment = "Excellent - Well controlled"
    elif rate < 10:
        assessment = "Good - Within normal range"
    elif rate < 15:
        assessment = "Elevated - Monitor closely"
    elif rate < 25:
        assessment = "High - Scope creep likely"
    else:
        assessment = "Critical - Major scope issues"
    
    return round(rate, 2), assessment


def categorize_change_orders(
    change_orders: List[Dict[str, any]]
) -> Dict[str, any]:
    """Categorize change orders by type and responsibility.
    
    Args:
        change_orders: List of change order dicts with 'category', 'amount', 
                      'reason', 'initiated_by'
    
    Returns:
        Dict with categorization analysis
    """
    if not change_orders:
        return {
            'by_category': {},
            'by_initiator': {},
            'total_count': 0,
            'total_value': 0
        }
    
    by_category = defaultdict(lambda: {'count': 0, 'value': 0})
    by_initiator = defaultdict(lambda: {'count': 0, 'value': 0})
    
    total_value = 0
    
    for co in change_orders:
        category = co.get('category', 'Unknown')
        amount = co.get('amount', 0)
        initiator = co.get('initiated_by', 'Unknown')
        
        by_category[category]['count'] += 1
        by_category[category]['value'] += amount
        
        by_initiator[initiator]['count'] += 1
        by_initiator[initiator]['value'] += amount
        
        total_value += amount
    
    return {
        'by_category': dict(by_category),
        'by_initiator': dict(by_initiator),
        'total_count': len(change_orders),
        'total_value': round(total_value, 2)
    }


def detect_scope_creep_patterns(
    change_orders: List[Dict[str, any]],
    original_budget: float
) -> Tuple[bool, List[str]]:
    """Detect patterns indicating scope creep.
    
    Args:
        change_orders: List of change order dicts
        original_budget: Original contract budget
    
    Returns:
        Tuple of (scope_creep_detected, list of indicators)
    """
    indicators = []
    scope_creep = False
    
    if not change_orders:
        return False, ["No change orders to analyze"]
    
    # Sort by date
    sorted_cos = sorted(change_orders, key=lambda x: x.get('date', ''))
    
    # Pattern 1: High frequency
    if len(change_orders) > 20:
        indicators.append(f"High frequency: {len(change_orders)} change orders")
        scope_creep = True
    
    # Pattern 2: Acceleration over time
    if len(sorted_cos) >= 6:
        first_half_count = len(sorted_cos[:len(sorted_cos)//2])
        second_half_count = len(sorted_cos[len(sorted_cos)//2:])
        
        if second_half_count > first_half_count * 1.5:
            indicators.append("Change orders accelerating over time")
            scope_creep = True
    
    # Pattern 3: Owner-initiated changes dominate
    categorization = categorize_change_orders(change_orders)
    owner_initiated = categorization['by_initiator'].get('Owner', {}).get('count', 0)
    
    if owner_initiated > len(change_orders) * 0.6:
        indicators.append(f"Owner-initiated changes: {owner_initiated}/{len(change_orders)}")
        scope_creep = True
    
    # Pattern 4: Design-related changes
    design_category = categorization['by_category'].get('Design Change', {})
    design_count = design_category.get('count', 0)
    
    if design_count > len(change_orders) * 0.4:
        indicators.append(f"High design changes: {design_count} changes")
        scope_creep = True
    
    # Pattern 5: Large cumulative value
    total_co_value = categorization['total_value']
    co_rate = (total_co_value / original_budget * 100) if original_budget > 0 else 0
    
    if co_rate > 15:
        indicators.append(f"Change orders exceed 15% of budget ({co_rate:.1f}%)")
        scope_creep = True
    
    if not indicators:
        indicators.append("No significant scope creep patterns detected")
    
    return scope_creep, indicators


def analyze_change_order_timing(
    change_orders: List[Dict[str, any]],
    project_start_date: str,
    project_duration_days: int
) -> Dict[str, any]:
    """Analyze when change orders occur in project lifecycle.
    
    Args:
        change_orders: List of change order dicts with 'date'
        project_start_date: Project start date (ISO format)
        project_duration_days: Total planned project duration
    
    Returns:
        Dict with timing analysis
    """
    if not change_orders:
        return {
            'early_phase_count': 0,
            'mid_phase_count': 0,
            'late_phase_count': 0,
            'observation': 'No change orders'
        }
    
    try:
        start_date = datetime.fromisoformat(project_start_date.replace('Z', '+00:00'))
    except:
        return {'observation': 'Invalid project start date'}
    
    early_count = 0
    mid_count = 0
    late_count = 0
    
    for co in change_orders:
        try:
            co_date = datetime.fromisoformat(co.get('date', '').replace('Z', '+00:00'))
            days_elapsed = (co_date - start_date).days
            
            progress_pct = (days_elapsed / project_duration_days * 100) if project_duration_days > 0 else 0
            
            if progress_pct < 33:
                early_count += 1
            elif progress_pct < 67:
                mid_count += 1
            else:
                late_count += 1
        except:
            continue
    
    # Analysis
    observation = ""
    if late_count > early_count + mid_count:
        observation = "Warning: Most changes occurring late in project"
    elif early_count > mid_count + late_count:
        observation = "Good: Most changes identified early"
    else:
        observation = "Changes distributed throughout project"
    
    return {
        'early_phase_count': early_count,
        'mid_phase_count': mid_count,
        'late_phase_count': late_count,
        'observation': observation
    }


def recommend_change_order_controls(
    scope_creep_detected: bool,
    co_rate: float,
    indicators: List[str]
) -> List[str]:
    """Recommend controls to manage change orders.
    
    Args:
        scope_creep_detected: Whether scope creep was detected
        co_rate: Change order rate as % of budget
        indicators: List of scope creep indicators
    
    Returns:
        List of recommendations
    """
    recommendations = []
    
    if not scope_creep_detected and co_rate < 10:
        recommendations.append("Change order management is effective")
        return recommendations
    
    # High-priority recommendations
    if scope_creep_detected:
        recommendations.extend([
            "Conduct scope baseline review with stakeholders",
            "Implement stricter change order approval process",
            "Review contract terms regarding change orders"
        ])
    
    if co_rate > 15:
        recommendations.extend([
            "Analyze root causes of changes",
            "Improve upfront design and planning",
            "Evaluate project controls effectiveness"
        ])
    
    # Pattern-specific recommendations
    if any('Owner-initiated' in ind for ind in indicators):
        recommendations.append("Schedule client expectations alignment meeting")
    
    if any('design changes' in ind.lower() for ind in indicators):
        recommendations.extend([
            "Review design completion and quality",
            "Consider value engineering workshop"
        ])
    
    if any('accelerating' in ind for ind in indicators):
        recommendations.append("Implement weekly change order review meetings")
    
    # General recommendations
    recommendations.extend([
        "Document lessons learned for future projects",
        "Track change order metrics weekly",
        "Improve change impact assessment process"
    ])
    
    return recommendations


def calculate_change_order_risk_score(
    co_rate: float,
    scope_creep_detected: bool,
    co_count: int,
    late_phase_ratio: float
) -> Tuple[int, str]:
    """Calculate overall change order risk score.
    
    Args:
        co_rate: Change order rate as % of budget
        scope_creep_detected: Whether scope creep detected
        co_count: Number of change orders
        late_phase_ratio: Ratio of late-phase changes
    
    Returns:
        Tuple of (risk_score 0-100, risk_level)
    """
    risk_score = 0
    
    # CO rate impact (0-40 points)
    if co_rate > 25:
        risk_score += 40
    elif co_rate > 15:
        risk_score += 30
    elif co_rate > 10:
        risk_score += 20
    elif co_rate > 5:
        risk_score += 10
    
    # Scope creep impact (0-30 points)
    if scope_creep_detected:
        risk_score += 30
    
    # Frequency impact (0-20 points)
    if co_count > 30:
        risk_score += 20
    elif co_count > 20:
        risk_score += 15
    elif co_count > 10:
        risk_score += 10
    
    # Timing impact (0-10 points)
    if late_phase_ratio > 0.5:
        risk_score += 10
    elif late_phase_ratio > 0.3:
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
    print("=== Change Order Pattern Analyzer Test ===\n")
    
    # Test data
    change_orders = [
        {'category': 'Design Change', 'amount': 50000, 'initiated_by': 'Owner', 'date': '2025-02-15'},
        {'category': 'Site Conditions', 'amount': 30000, 'initiated_by': 'Contractor', 'date': '2025-03-01'},
        {'category': 'Design Change', 'amount': 45000, 'initiated_by': 'Owner', 'date': '2025-04-10'},
        {'category': 'Owner Request', 'amount': 75000, 'initiated_by': 'Owner', 'date': '2025-05-20'},
        {'category': 'Design Change', 'amount': 25000, 'initiated_by': 'Architect', 'date': '2025-06-15'},
    ]
    
    original_budget = 15_000_000
    
    # Test CO rate
    total_co_value = sum(co['amount'] for co in change_orders)
    co_rate, assessment = calculate_change_order_rate(total_co_value, original_budget)
    print(f"Change Order Rate: {co_rate}% - {assessment}\n")
    
    # Test categorization
    categorization = categorize_change_orders(change_orders)
    print(f"Total Change Orders: {categorization['total_count']}")
    print(f"Total Value: ${categorization['total_value']:,.2f}")
    print("\nBy Category:")
    for cat, data in categorization['by_category'].items():
        print(f"  {cat}: {data['count']} orders, ${data['value']:,.2f}")
    print()
    
    # Test scope creep detection
    scope_creep, indicators = detect_scope_creep_patterns(change_orders, original_budget)
    print(f"Scope Creep Detected: {scope_creep}")
    print("Indicators:")
    for ind in indicators:
        print(f"  - {ind}")
    print()
    
    # Calculate risk
    risk_score, risk_level = calculate_change_order_risk_score(
        co_rate=co_rate,
        scope_creep_detected=scope_creep,
        co_count=len(change_orders),
        late_phase_ratio=0.2
    )
    print(f"Change Order Risk: {risk_score} - {risk_level}")


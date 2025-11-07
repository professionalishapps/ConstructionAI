"""Agent 8: Quality Issue Detector

Analyzes inspection reports for rework risk and quality problems.
"""
from typing import Dict, List, Tuple, Optional
from collections import defaultdict


def analyze_defect_severity(
    defects: List[Dict[str, any]]
) -> Dict[str, any]:
    """Analyze defects by severity level.
    
    Args:
        defects: List of defect dicts with 'severity', 'category', 'cost_estimate'
    
    Returns:
        Dict with severity analysis
    """
    severity_counts = defaultdict(int)
    severity_costs = defaultdict(float)
    category_counts = defaultdict(int)
    
    total_cost = 0
    
    for defect in defects:
        severity = defect.get('severity', 'Minor')
        category = defect.get('category', 'Unknown')
        cost = defect.get('cost_estimate', 0)
        
        severity_counts[severity] += 1
        severity_costs[severity] += cost
        category_counts[category] += 1
        total_cost += cost
    
    return {
        'by_severity': dict(severity_counts),
        'cost_by_severity': dict(severity_costs),
        'by_category': dict(category_counts),
        'total_defects': len(defects),
        'total_estimated_cost': round(total_cost, 2)
    }


def calculate_rework_probability(
    defect_count: int,
    inspection_failures: int,
    total_inspections: int,
    punch_list_items: int
) -> Tuple[float, str]:
    """Calculate probability of significant rework being required.
    
    Args:
        defect_count: Total number of defects identified
        inspection_failures: Number of failed inspections
        total_inspections: Total inspections conducted
        punch_list_items: Current punch list item count
    
    Returns:
        Tuple of (probability 0-100, risk_level)
    """
    # Base probability from defect density
    defect_factor = min(50, defect_count * 2)  # 2% per defect, max 50%
    
    # Inspection failure rate
    if total_inspections > 0:
        failure_rate = (inspection_failures / total_inspections) * 100
        inspection_factor = failure_rate * 0.5  # Half weight
    else:
        inspection_factor = 0
    
    # Punch list factor
    punch_factor = min(30, punch_list_items * 0.5)  # 0.5% per item, max 30%
    
    # Combined probability
    probability = defect_factor + inspection_factor + punch_factor
    probability = min(100, probability)
    
    if probability < 20:
        risk_level = "LOW"
    elif probability < 50:
        risk_level = "MEDIUM"
    elif probability < 75:
        risk_level = "HIGH"
    else:
        risk_level = "CRITICAL"
    
    return round(probability, 1), risk_level


def estimate_rework_cost(
    defects: List[Dict[str, any]],
    total_project_cost: float,
    quality_contingency_pct: float = 2.0
) -> Dict[str, float]:
    """Estimate cost impact of rework.
    
    Args:
        defects: List of defect dicts with cost estimates
        total_project_cost: Total project budget
        quality_contingency_pct: Quality contingency as % of budget
    
    Returns:
        Dict with cost estimates
    """
    # Direct defect costs
    direct_cost = sum(d.get('cost_estimate', 0) for d in defects)
    
    # Indirect costs (schedule impact, coordination, etc.)
    # Estimate as 30% of direct costs
    indirect_cost = direct_cost * 0.3
    
    total_rework_cost = direct_cost + indirect_cost
    
    # Compare to contingency
    available_contingency = total_project_cost * (quality_contingency_pct / 100)
    contingency_usage_pct = (total_rework_cost / available_contingency * 100) if available_contingency > 0 else 0
    
    return {
        'direct_rework_cost': round(direct_cost, 2),
        'indirect_cost': round(indirect_cost, 2),
        'total_rework_cost': round(total_rework_cost, 2),
        'available_contingency': round(available_contingency, 2),
        'contingency_usage_pct': round(contingency_usage_pct, 1),
        'exceeds_contingency': total_rework_cost > available_contingency
    }


def identify_systemic_issues(
    defects: List[Dict[str, any]],
    min_occurrences: int = 3
) -> List[str]:
    """Identify systemic quality problems from defect patterns.
    
    Args:
        defects: List of defect dicts with 'category', 'trade', 'root_cause'
        min_occurrences: Minimum occurrences to flag as systemic
    
    Returns:
        List of systemic issues identified
    """
    issues = []
    
    if len(defects) < min_occurrences:
        return ["Insufficient defects to identify systemic patterns"]
    
    # Count by category
    by_category = defaultdict(int)
    by_trade = defaultdict(int)
    by_root_cause = defaultdict(int)
    
    for defect in defects:
        category = defect.get('category', 'Unknown')
        trade = defect.get('trade', 'Unknown')
        root_cause = defect.get('root_cause', 'Unknown')
        
        by_category[category] += 1
        by_trade[trade] += 1
        by_root_cause[root_cause] += 1
    
    # Identify systemic category issues
    for category, count in by_category.items():
        if count >= min_occurrences:
            pct = (count / len(defects)) * 100
            issues.append(f"Recurring {category} issues ({count} occurrences, {pct:.0f}%)")
    
    # Identify problematic trades
    for trade, count in by_trade.items():
        if count >= min_occurrences and trade != 'Unknown':
            issues.append(f"{trade} trade quality concerns ({count} defects)")
    
    # Identify root cause patterns
    for cause, count in by_root_cause.items():
        if count >= min_occurrences and cause != 'Unknown':
            issues.append(f"Pattern: {cause} ({count} instances)")
    
    if not issues:
        issues.append("No systemic patterns detected - defects appear isolated")
    
    return issues


def analyze_inspection_trends(
    inspection_history: List[Dict[str, any]]
) -> Dict[str, any]:
    """Analyze trends in inspection results.
    
    Args:
        inspection_history: List of inspection dicts with 'date', 'passed', 'defects_found'
    
    Returns:
        Dict with trend analysis
    """
    if len(inspection_history) < 2:
        return {
            'trend': 'Insufficient data',
            'pass_rate': 0,
            'improving': False,
            'observations': ['Need more inspection data']
        }
    
    # Sort by date
    sorted_history = sorted(inspection_history, key=lambda x: x.get('date', ''))
    
    # Overall pass rate
    passed_count = sum(1 for i in sorted_history if i.get('passed', False))
    pass_rate = (passed_count / len(sorted_history)) * 100
    
    # Trend analysis
    mid_point = len(sorted_history) // 2
    first_half_passed = sum(1 for i in sorted_history[:mid_point] if i.get('passed', False))
    second_half_passed = sum(1 for i in sorted_history[mid_point:] if i.get('passed', False))
    
    first_half_rate = (first_half_passed / mid_point * 100) if mid_point > 0 else 0
    second_half_rate = (second_half_passed / (len(sorted_history) - mid_point) * 100) if (len(sorted_history) - mid_point) > 0 else 0
    
    improving = second_half_rate > first_half_rate + 5  # 5% improvement threshold
    deteriorating = second_half_rate < first_half_rate - 5
    
    # Defect trend
    total_defects = sum(i.get('defects_found', 0) for i in sorted_history)
    avg_defects_per_inspection = total_defects / len(sorted_history)
    
    observations = []
    
    if pass_rate >= 90:
        observations.append("Excellent inspection pass rate")
    elif pass_rate >= 75:
        observations.append("Good inspection performance")
    else:
        observations.append("Quality improvement needed")
    
    if improving:
        observations.append(f"Quality improving: {first_half_rate:.0f}% to {second_half_rate:.0f}% pass rate")
    elif deteriorating:
        observations.append(f"Quality declining: {first_half_rate:.0f}% to {second_half_rate:.0f}% pass rate")
    else:
        observations.append("Quality performance stable")
    
    if avg_defects_per_inspection > 3:
        observations.append(f"High defect rate: {avg_defects_per_inspection:.1f} defects per inspection")
    
    trend = "Improving" if improving else "Deteriorating" if deteriorating else "Stable"
    
    return {
        'trend': trend,
        'pass_rate': round(pass_rate, 1),
        'improving': improving,
        'avg_defects_per_inspection': round(avg_defects_per_inspection, 1),
        'observations': observations
    }


def recommend_quality_improvements(
    rework_probability: float,
    systemic_issues: List[str],
    inspection_trend: str,
    cost_exceeds_contingency: bool
) -> List[str]:
    """Recommend quality improvement actions.
    
    Args:
        rework_probability: Probability of significant rework
        systemic_issues: List of identified systemic issues
        inspection_trend: Trend in inspection results
        cost_exceeds_contingency: Whether costs exceed quality contingency
    
    Returns:
        List of recommendations
    """
    recommendations = []
    
    # High-priority recommendations
    if rework_probability > 50:
        recommendations.extend([
            "Implement enhanced quality control measures immediately",
            "Conduct root cause analysis of defects",
            "Increase inspection frequency for high-risk activities"
        ])
    
    if cost_exceeds_contingency:
        recommendations.extend([
            "Review and increase quality contingency budget",
            "Prioritize defect resolution by cost impact",
            "Assess financial impact on project budget"
        ])
    
    # Trend-based recommendations
    if inspection_trend == "Deteriorating":
        recommendations.extend([
            "Investigate causes of quality decline",
            "Review subcontractor performance and supervision",
            "Implement corrective action plan"
        ])
    elif inspection_trend == "Stable" and rework_probability > 30:
        recommendations.append("Quality improvement initiative needed")
    
    # Systemic issue recommendations
    if systemic_issues and not any('No systemic' in issue for issue in systemic_issues):
        recommendations.extend([
            "Address systemic quality issues identified",
            "Provide targeted training for recurring problems",
            "Review quality management procedures"
        ])
        
        # Trade-specific
        if any('trade' in issue.lower() for issue in systemic_issues):
            recommendations.append("Meet with subcontractors showing quality concerns")
        
        # Process-specific
        if any('pattern' in issue.lower() for issue in systemic_issues):
            recommendations.append("Revise work processes to prevent recurring issues")
    
    # General best practices
    if rework_probability > 20:
        recommendations.extend([
            "Document lessons learned for future phases",
            "Enhance quality specifications and acceptance criteria",
            "Consider third-party quality audits"
        ])
    
    if not recommendations:
        recommendations.append("Quality performance is acceptable - maintain current practices")
    
    return recommendations


def calculate_quality_risk_score(
    rework_probability: float,
    defect_count: int,
    inspection_pass_rate: float,
    cost_factor: float
) -> Tuple[int, str]:
    """Calculate overall quality risk score.
    
    Args:
        rework_probability: Probability of rework (0-100)
        defect_count: Number of defects
        inspection_pass_rate: Pass rate percentage (0-100)
        cost_factor: Cost as ratio of contingency
    
    Returns:
        Tuple of (risk_score 0-100, risk_level)
    """
    # Rework probability (0-40 points)
    rework_points = rework_probability * 0.4
    
    # Defect count (0-20 points)
    defect_points = min(20, defect_count * 0.5)
    
    # Inspection failures (0-25 points)
    inspection_points = (100 - inspection_pass_rate) * 0.25
    
    # Cost impact (0-15 points)
    cost_points = min(15, cost_factor * 15)
    
    risk_score = rework_points + defect_points + inspection_points + cost_points
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
    print("=== Quality Issue Detector Test ===\n")
    
    # Test data
    defects = [
        {'severity': 'Major', 'category': 'Concrete', 'cost_estimate': 5000, 'trade': 'Concrete', 'root_cause': 'Poor workmanship'},
        {'severity': 'Minor', 'category': 'Finish', 'cost_estimate': 500, 'trade': 'Painting', 'root_cause': 'Material defect'},
        {'severity': 'Major', 'category': 'Concrete', 'cost_estimate': 4500, 'trade': 'Concrete', 'root_cause': 'Poor workmanship'},
        {'severity': 'Moderate', 'category': 'Framing', 'cost_estimate': 2000, 'trade': 'Carpentry', 'root_cause': 'Design unclear'},
    ]
    
    # Analyze defects
    analysis = analyze_defect_severity(defects)
    print(f"Total Defects: {analysis['total_defects']}")
    print(f"Estimated Cost: ${analysis['total_estimated_cost']:,.2f}")
    print(f"By Severity: {analysis['by_severity']}\n")
    
    # Rework probability
    prob, level = calculate_rework_probability(
        defect_count=4,
        inspection_failures=2,
        total_inspections=10,
        punch_list_items=15
    )
    print(f"Rework Probability: {prob}% - {level}\n")
    
    # Systemic issues
    systemic = identify_systemic_issues(defects, min_occurrences=2)
    print("Systemic Issues:")
    for issue in systemic:
        print(f"  - {issue}")
    print()
    
    # Risk score
    risk_score, risk_level = calculate_quality_risk_score(
        rework_probability=prob,
        defect_count=4,
        inspection_pass_rate=80,
        cost_factor=0.5
    )
    print(f"Quality Risk: {risk_score} - {risk_level}")


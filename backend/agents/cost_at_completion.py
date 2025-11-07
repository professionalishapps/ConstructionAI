"""Agent 13: Cost at Completion Estimator

Projects final cost with confidence intervals.
Depends on Agents 2, 6, 10 (Cost Variance, Change Orders, Cash Flow).
"""
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import math


def calculate_eac_multiple_methods(
    budget: float,
    actual_cost: float,
    earned_value: float,
    cpi: float,
    pct_complete: float
) -> Dict[str, any]:
    """Calculate Estimate at Completion using multiple EVM formulas.
    
    Args:
        budget: Budget at Completion (BAC)
        actual_cost: Actual Cost to date (AC)
        earned_value: Earned Value to date (EV)
        cpi: Cost Performance Index
        pct_complete: Percent complete (0-100)
    
    Returns:
        Dict with multiple EAC calculations
    """
    remaining_work = budget - earned_value
    
    # Method 1: EAC = BAC / CPI
    # Assumes current cost efficiency continues
    if cpi > 0:
        eac_cpi = budget / cpi
    else:
        eac_cpi = budget * 1.5
    
    # Method 2: EAC = AC + (BAC - EV)
    # Assumes future work at planned cost (atypical variances)
    eac_atypical = actual_cost + remaining_work
    
    # Method 3: EAC = AC + [(BAC - EV) / CPI]
    # Assumes future work at current efficiency
    if cpi > 0:
        eac_typical = actual_cost + (remaining_work / cpi)
    else:
        eac_typical = actual_cost + (remaining_work * 1.5)
    
    # Method 4: Burn rate projection
    if pct_complete > 0:
        burn_rate = actual_cost / (pct_complete / 100)
        eac_burn = burn_rate
    else:
        eac_burn = budget
    
    # Weighted composite (favor CPI-based as project progresses)
    weight_cpi = min(0.6, pct_complete / 100 * 0.8)  # Increase CPI weight with progress
    weight_typical = 0.3
    weight_burn = 0.1
    
    eac_composite = (eac_cpi * weight_cpi) + (eac_typical * weight_typical) + (eac_burn * weight_burn)
    
    return {
        'method_1_cpi': round(eac_cpi, 2),
        'method_2_atypical': round(eac_atypical, 2),
        'method_3_typical': round(eac_typical, 2),
        'method_4_burn_rate': round(eac_burn, 2),
        'composite_eac': round(eac_composite, 2),
        'variance_across_methods': round(max(eac_cpi, eac_atypical, eac_typical, eac_burn) - 
                                        min(eac_cpi, eac_atypical, eac_typical, eac_burn), 2)
    }


def calculate_confidence_intervals_cost(
    eac_composite: float,
    budget: float,
    cpi: float,
    cost_volatility: float = 0.10
) -> Dict[str, any]:
    """Calculate confidence intervals for cost forecast.
    
    Args:
        eac_composite: Composite EAC estimate
        budget: Original budget
        cpi: Cost Performance Index
        cost_volatility: Historical cost variance (default 10%)
    
    Returns:
        Dict with confidence intervals
    """
    # Base variance on budget and historical volatility
    base_variance = budget * cost_volatility
    
    # Adjust for performance - poor CPI increases uncertainty
    if cpi < 0.9:
        variance_multiplier = 1.4
    elif cpi < 0.95:
        variance_multiplier = 1.2
    else:
        variance_multiplier = 1.0
    
    adjusted_variance = base_variance * variance_multiplier
    
    # 90% and 95% confidence intervals
    ci_90_range = adjusted_variance * 1.645
    ci_95_range = adjusted_variance * 1.96
    
    return {
        'point_estimate': eac_composite,
        'confidence_90': {
            'low': max(budget * 0.8, eac_composite - ci_90_range),  # Floor at 80% of budget
            'high': eac_composite + ci_90_range,
            'range': ci_90_range * 2
        },
        'confidence_95': {
            'low': max(budget * 0.8, eac_composite - ci_95_range),
            'high': eac_composite + ci_95_range,
            'range': ci_95_range * 2
        },
        'uncertainty_level': 'High' if variance_multiplier > 1.2 else 'Moderate' if variance_multiplier > 1.0 else 'Low'
    }


def integrate_change_order_and_cashflow_data(
    base_eac: float,
    pending_change_orders: float,
    change_order_trend: str,
    cash_flow_pressure: str
) -> Dict[str, any]:
    """Integrate data from Agents 6 and 10 to refine cost forecast.
    
    Args:
        base_eac: Base Estimate at Completion
        pending_change_orders: Value of pending/likely change orders
        change_order_trend: Trend from Agent 6
        cash_flow_pressure: Pressure level from Agent 10
    
    Returns:
        Dict with adjusted forecast
    """
    adjustments = []
    adjustment_value = 0
    
    # Pending change orders
    adjustment_value += pending_change_orders
    if pending_change_orders > 0:
        adjustments.append(f"Pending change orders: +${pending_change_orders:,.2f}")
    
    # Change order trend adjustment
    if "accelerating" in change_order_trend.lower() or "increasing" in change_order_trend.lower():
        # Estimate additional 5% for future changes
        future_co_estimate = base_eac * 0.05
        adjustment_value += future_co_estimate
        adjustments.append(f"Change order trend risk: +${future_co_estimate:,.2f}")
    
    # Cash flow pressure can indicate cost issues
    if cash_flow_pressure == "HIGH":
        # May indicate unbudgeted costs
        cash_adjustment = base_eac * 0.03
        adjustment_value += cash_adjustment
        adjustments.append(f"Cash flow pressure indicator: +${cash_adjustment:,.2f}")
    
    adjusted_eac = base_eac + adjustment_value
    
    return {
        'base_eac': round(base_eac, 2),
        'total_adjustments': round(adjustment_value, 2),
        'adjusted_eac': round(adjusted_eac, 2),
        'adjustments': adjustments,
        'adjustment_pct': round((adjustment_value / base_eac * 100) if base_eac > 0 else 0, 1)
    }


def calculate_expected_overrun(
    adjusted_eac: float,
    budget: float
) -> Dict[str, any]:
    """Calculate expected cost overrun.
    
    Args:
        adjusted_eac: Adjusted Estimate at Completion
        budget: Original budget
    
    Returns:
        Dict with overrun analysis
    """
    variance = budget - adjusted_eac
    variance_pct = (variance / budget * 100) if budget > 0 else 0
    
    if variance < 0:
        status = "Over Budget"
        severity = "CRITICAL" if abs(variance_pct) > 15 else "HIGH" if abs(variance_pct) > 10 else "MEDIUM"
    elif variance > 0:
        status = "Under Budget"
        severity = "POSITIVE"
    else:
        status = "On Budget"
        severity = "NONE"
    
    return {
        'budget': budget,
        'forecast_final_cost': adjusted_eac,
        'variance': round(variance, 2),
        'variance_pct': round(variance_pct, 1),
        'overrun_amount': round(abs(variance), 2) if variance < 0 else 0,
        'status': status,
        'severity': severity
    }


def generate_probability_distribution(
    eac_point: float,
    ci_90_low: float,
    ci_90_high: float
) -> Dict[str, any]:
    """Generate probability distribution for cost outcomes.
    
    Args:
        eac_point: Point estimate EAC
        ci_90_low: 90% confidence interval lower bound
        ci_90_high: 90% confidence interval upper bound
    
    Returns:
        Dict with probability distribution data
    """
    # Generate points for probability curve
    # Assume normal distribution
    
    std_dev = (ci_90_high - eac_point) / 1.645
    
    # Calculate probabilities for key thresholds
    def calc_probability_under(threshold, mean, std):
        if std == 0:
            return 1.0 if threshold >= mean else 0.0
        z = (threshold - mean) / std
        # Simplified normal CDF approximation
        return 0.5 * (1 + math.erf(z / math.sqrt(2)))
    
    prob_at_budget = calc_probability_under(eac_point, eac_point, std_dev)
    prob_within_10pct = calc_probability_under(eac_point * 1.10, eac_point, std_dev)
    prob_within_20pct = calc_probability_under(eac_point * 1.20, eac_point, std_dev)
    
    return {
        'distribution_type': 'Normal',
        'mean': round(eac_point, 2),
        'std_dev': round(std_dev, 2),
        'prob_at_or_below_forecast': round(prob_at_budget * 100, 1),
        'prob_within_10pct_overrun': round(prob_within_10pct * 100, 1),
        'prob_within_20pct_overrun': round(prob_within_20pct * 100, 1)
    }


def recommend_cost_control_actions(
    variance_pct: float,
    cpi: float,
    change_order_rate: float
) -> List[str]:
    """Recommend cost control actions.
    
    Args:
        variance_pct: Cost variance as % of budget
        cpi: Cost Performance Index
        change_order_rate: Change order rate as % of budget
    
    Returns:
        List of recommendations
    """
    recommendations = []
    
    if variance_pct >= 0:
        recommendations.append("✓ Project forecasted at or under budget")
        recommendations.append("Maintain current cost controls")
        return recommendations
    
    # Overrun severity-based recommendations
    if abs(variance_pct) > 15:
        recommendations.extend([
            "🚨 CRITICAL: Major cost overrun forecasted",
            "Implement immediate cost reduction measures",
            "Freeze all non-essential spending",
            "Review and renegotiate subcontractor prices",
            "Consider scope reduction with owner"
        ])
    elif abs(variance_pct) > 10:
        recommendations.extend([
            "⚠️ Significant cost overrun - implement cost controls",
            "Review all pending expenditures",
            "Accelerate value engineering efforts",
            "Negotiate better pricing on remaining work"
        ])
    else:
        recommendations.extend([
            "Moderate overrun forecasted - increase cost monitoring",
            "Identify cost reduction opportunities"
        ])
    
    # CPI-specific
    if cpi < 0.9:
        recommendations.extend([
            "Poor cost efficiency - review work methods",
            "Analyze cost drivers and eliminate waste",
            "Increase cost tracking frequency to weekly"
        ])
    
    # Change order-specific
    if change_order_rate > 10:
        recommendations.extend([
            "High change order rate contributing to overrun",
            "Implement stricter change order controls",
            "Negotiate change order pricing more aggressively"
        ])
    
    # General best practices
    recommendations.extend([
        "Update cost forecast bi-weekly",
        "Review committed costs vs budget weekly",
        "Hold cost review meetings with all stakeholders"
    ])
    
    return recommendations


def calculate_cost_forecast_risk(
    variance_pct: float,
    confidence_range_pct: float,
    cpi: float,
    change_order_rate: float
) -> Tuple[int, str]:
    """Calculate risk score for cost forecast.
    
    Args:
        variance_pct: Cost variance as % of budget
        confidence_range_pct: Width of 90% CI as % of budget
        cpi: Cost Performance Index
        change_order_rate: Change order rate as % of budget
    
    Returns:
        Tuple of (risk_score 0-100, risk_level)
    """
    risk_score = 0
    
    # Variance magnitude (0-40 points)
    abs_variance_pct = abs(variance_pct)
    if abs_variance_pct > 20:
        risk_score += 40
    elif abs_variance_pct > 15:
        risk_score += 35
    elif abs_variance_pct > 10:
        risk_score += 25
    elif abs_variance_pct > 5:
        risk_score += 15
    
    # Uncertainty (0-20 points)
    if confidence_range_pct > 20:
        risk_score += 20
    elif confidence_range_pct > 15:
        risk_score += 15
    elif confidence_range_pct > 10:
        risk_score += 10
    
    # CPI (0-25 points)
    if cpi < 0.85:
        risk_score += 25
    elif cpi < 0.90:
        risk_score += 20
    elif cpi < 0.95:
        risk_score += 10
    
    # Change orders (0-15 points)
    if change_order_rate > 15:
        risk_score += 15
    elif change_order_rate > 10:
        risk_score += 10
    elif change_order_rate > 5:
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
    print("=== Cost at Completion Estimator Test ===\n")
    
    # Test data
    budget = 15_000_000
    actual_cost = 6_800_000
    pct_complete = 42.5
    earned_value = budget * (pct_complete / 100)
    cpi = earned_value / actual_cost
    
    # Calculate EAC
    eac_methods = calculate_eac_multiple_methods(
        budget=budget,
        actual_cost=actual_cost,
        earned_value=earned_value,
        cpi=cpi,
        pct_complete=pct_complete
    )
    print(f"EAC Calculations:")
    print(f"  CPI Method: ${eac_methods['method_1_cpi']:,.2f}")
    print(f"  Typical: ${eac_methods['method_3_typical']:,.2f}")
    print(f"  Composite: ${eac_methods['composite_eac']:,.2f}\n")
    
    # Confidence intervals
    confidence = calculate_confidence_intervals_cost(
        eac_composite=eac_methods['composite_eac'],
        budget=budget,
        cpi=cpi
    )
    print(f"90% Confidence Interval: ${confidence['confidence_90']['low']:,.2f} - ${confidence['confidence_90']['high']:,.2f}\n")
    
    # Integrate other data
    integrated = integrate_change_order_and_cashflow_data(
        base_eac=eac_methods['composite_eac'],
        pending_change_orders=150_000,
        change_order_trend="Accelerating",
        cash_flow_pressure="MEDIUM"
    )
    print(f"Adjusted EAC: ${integrated['adjusted_eac']:,.2f}")
    print(f"Adjustments: +${integrated['total_adjustments']:,.2f} ({integrated['adjustment_pct']}%)\n")
    
    # Expected overrun
    overrun = calculate_expected_overrun(integrated['adjusted_eac'], budget)
    print(f"Forecast Status: {overrun['status']}")
    print(f"Expected Overrun: ${overrun['overrun_amount']:,.2f} ({overrun['variance_pct']}%)\n")
    
    # Risk score
    ci_range_pct = (confidence['confidence_90']['range'] / budget) * 100
    risk_score, risk_level = calculate_cost_forecast_risk(
        variance_pct=overrun['variance_pct'],
        confidence_range_pct=ci_range_pct,
        cpi=cpi,
        change_order_rate=2.5
    )
    print(f"Cost Forecast Risk: {risk_score} - {risk_level}")


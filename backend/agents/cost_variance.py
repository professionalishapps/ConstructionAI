"""Agent 2: Cost Variance Analyzer

Analyzes project cost performance, spending patterns, and estimates future cost overruns.
Uses CPI (Cost Performance Index) to forecast completion costs and detect cost pressure areas.
"""
from decimal import Decimal
from typing import Dict, List, Optional, Tuple
import math


def calculate_eac(budget: float, cpi: float, spent_to_date: float, pct_complete: float) -> Dict[str, float]:
    """Calculate Estimate at Completion (EAC) using current performance.
    
    Args:
        budget: Total project budget/contract value
        cpi: Current Cost Performance Index
        spent_to_date: Actual cost spent so far
        pct_complete: Current completion percentage (0-100)
    
    Returns:
        Dict with EAC and variance metrics
    """
    if pct_complete <= 0 or budget <= 0:
        return {
            'eac': budget,
            'variance_at_completion': 0,
            'variance_pct': 0
        }
    
    # Simple EAC = (Spent to Date / % Complete) 
    # i.e., extrapolate current burn rate
    try:
        eac_burn_rate = spent_to_date / (pct_complete / 100.0)
    except ZeroDivisionError:
        eac_burn_rate = budget

    # CPI-based EAC = Budget / CPI
    # Assumes future work follows current efficiency
    try:
        eac_cpi = budget / cpi if cpi > 0 else budget * 1.5
    except ZeroDivisionError:
        eac_cpi = budget * 1.5

    # Use weighted average (favor CPI-based when further along)
    weight = min(0.8, pct_complete / 100.0)  # max 80% weight on CPI
    eac = (eac_cpi * weight) + (eac_burn_rate * (1 - weight))
    
    # Sanity bounds
    eac = min(eac, budget * 2.0)  # cap at 2x budget
    eac = max(eac, budget * 0.8)  # floor at 80% budget
    
    variance = budget - eac
    variance_pct = (variance / budget) * 100 if budget > 0 else 0
    
    return {
        'eac': round(eac, 2),
        'variance_at_completion': round(variance, 2),
        'variance_pct': round(variance_pct, 1)
    }


def analyze_cost_pressure(spent_to_date: float, 
                        budget: float,
                        pct_complete: float,
                        cost_variance: float) -> Tuple[str, List[str]]:
    """Analyze cost pressure and suggest focus areas.
    
    Returns:
        Tuple of (pressure_level, list of observations)
    """
    observations = []
    
    # Burn rate analysis
    expected_spent = budget * (pct_complete / 100.0)
    burn_ratio = spent_to_date / expected_spent if expected_spent > 0 else 1.0
    
    if burn_ratio > 1.1:
        observations.append(f"Spending {round((burn_ratio-1)*100, 1)}% faster than planned")
    elif burn_ratio < 0.9:
        observations.append(f"Spending {round((1-burn_ratio)*100, 1)}% slower than planned")
        
    # Cost variance analysis
    cv_pct = (cost_variance / budget) * 100 if budget > 0 else 0
    if abs(cv_pct) >= 5:
        observations.append(f"Cost variance is {round(abs(cv_pct), 1)}% of budget")
        
    # Progress-cost alignment
    cost_progress_ratio = (spent_to_date / budget) / (pct_complete / 100.0) if pct_complete > 0 else 1.0
    if cost_progress_ratio > 1.1:
        observations.append("Costs outpacing physical progress")
    elif cost_progress_ratio < 0.9:
        observations.append("Physical progress outpacing costs")
        
    # Determine pressure level
    if burn_ratio > 1.2 or cv_pct < -10:
        pressure = "HIGH"
    elif burn_ratio > 1.1 or cv_pct < -5:
        pressure = "MEDIUM"
    else:
        pressure = "LOW"
        
    return pressure, observations


if __name__ == "__main__":
    # Quick test
    budget = 15_000_000
    spent = 6_800_000
    pct = 42.5
    cpi = 0.938
    cv = -4263
    
    eac = calculate_eac(budget, cpi, spent, pct)
    print(f"EAC Analysis:")
    print(f"Original budget: ${budget:,.2f}")
    print(f"New EAC: ${eac['eac']:,.2f}")
    print(f"Variance: ${eac['variance_at_completion']:,.2f} ({eac['variance_pct']}%)")
    
    pressure, obs = analyze_cost_pressure(spent, budget, pct, cv)
    print(f"\nCost Pressure: {pressure}")
    print("Observations:")
    for o in obs:
        print(f"- {o}")